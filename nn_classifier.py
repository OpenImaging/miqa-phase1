import argparse
import logging
import math
import os
import sys
from pathlib import Path

import itk
import monai
import numpy as np
import pandas as pd
import torch
import wandb
from monai.metrics import compute_roc_auc
from monai.networks.nets.regressor import Regressor
from monai.transforms import AddChanneld, Compose, LoadImaged, ScaleIntensityd, ToTensord
from sklearn.metrics import confusion_matrix, classification_report
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter

existing_count = 0
missing_count = 0
predict_hd_data_root = "P:/PREDICTHD_BIDS_DEFACE/"
use_focal_loss = False


def get_image_dimension(path):
    image_io = itk.ImageIOFactory.CreateImageIO(path, itk.CommonEnums.IOFileMode_ReadMode)
    dim = (0, 0, 0)
    if image_io is not None:
        try:
            image_io.SetFileName(path)
            image_io.ReadImageInformation()
            assert image_io.GetNumberOfDimensions() == 3
            dim = (image_io.GetDimensions(0), image_io.GetDimensions(1), image_io.GetDimensions(2))
        except RuntimeError:
            pass
    return dim


def recursively_search_images(images, decisions, path_prefix, kind):
    count = 0
    for path in Path(path_prefix).rglob('*.nii.gz'):
        images.append(str(path))
        decisions.append(kind)
        count += 1
    print(f"{count} images in prefix {path_prefix}")


def construct_path_from_csv_fields(participant_id, session_id, series_type, series_number, overall_qa_assessment):
    sub_num = "sub-" + str(participant_id).zfill(6)
    ses_num = "ses-" + str(session_id)
    run_num = "run-" + str(series_number).zfill(3)
    scan_type = "PD"
    if series_type[0] == "T":  # not PD
        scan_type = series_type[0:2] + "w"
    if overall_qa_assessment < 6:
        scan_type = "BAD" + scan_type
    file_name = predict_hd_data_root + sub_num + "/" + ses_num + "/anat/" + \
                sub_num + "_" + ses_num + "_" + run_num + "_" + scan_type + ".nii.gz"
    return file_name


def does_file_exist(file_name):
    my_file = Path(file_name)
    global existing_count
    global missing_count
    if my_file.is_file():
        # print(f"Exists: {fileName}")
        existing_count += 1
        return True
    else:
        # print(f"Missing: {fileName}")
        missing_count += 1
        return False


def read_and_normalize_data_frame(tsv_path):
    df = pd.read_csv(tsv_path, sep='\t')
    df['file_path'] = df.apply(
        lambda row: construct_path_from_csv_fields(row['participant_id'],
                                                   row['session_id'],
                                                   row['series_type'],
                                                   row['series_number'],
                                                   row['overall_qa_assessment'],
                                                   ), axis=1)
    global existing_count
    global missing_count
    existing_count = 0
    missing_count = 0
    df['exists'] = df.apply(lambda row: does_file_exist(row['file_path']), axis=1)
    df['dimensions'] = df.apply(lambda row: get_image_dimension(row['file_path']), axis=1)
    print(f"Existing files: {existing_count}, non-existent files: {missing_count}")
    return df


class TiledClassifier(monai.networks.nets.Classifier):
    def forward(self, inputs):
        # split the input image into tiles and run each tile through NN
        results = []
        x_tile_size = self.in_shape[0]
        y_tile_size = self.in_shape[1]
        z_tile_size = self.in_shape[2]
        x_size = inputs.shape[2]
        y_size = inputs.shape[3]
        z_size = inputs.shape[4]
        x_steps = math.ceil(x_size / x_tile_size)
        y_steps = math.ceil(y_size / y_tile_size)
        z_steps = math.ceil(z_size / z_tile_size)
        # TODO: figure out the best tiling order (IJK vs KJI)
        for i in range(x_steps):
            i_start = round(i * (x_size - x_tile_size) / x_steps)
            for j in range(y_steps):
                j_start = round(j * (y_size - y_tile_size) / y_steps)
                for k in range(z_steps):
                    k_start = round(k * (z_size - z_tile_size) / z_steps)

                    # use slicing operator to make a tile
                    tile = inputs[:, :,
                           i_start:i_start + x_tile_size,
                           j_start:j_start + y_tile_size,
                           k_start: k_start + z_tile_size]
                    results.append(super().forward(tile))

        # TODO: do something smarter than mean here
        # self.out_shape[0] is the number of output classes
        average = torch.mean(torch.stack(results), dim=0)
        return average


def evaluate_model(model, data_loader, device, writer, epoch, run_name):
    model.eval()
    y_pred = []
    y_true = []
    with torch.no_grad():
        metric_count = 0
        for val_data in data_loader:
            val_images, val_labels = val_data["img"].to(device), val_data["label"].to(device)
            val_outputs = model(val_images).argmax(dim=1)

            y_true.extend(val_labels.cpu().tolist())
            y_pred.extend(val_outputs.cpu().tolist())

            metric_count += len(val_outputs)
            print('.', end='')
            if metric_count % 60 == 0:
                print("")

        print("\n" + run_name + "_confusion_matrix:")
        print(confusion_matrix(y_true, y_pred))
        print(classification_report(y_true, y_pred))

        auc_metric = compute_roc_auc(torch.as_tensor(y_pred), torch.as_tensor(y_true),
                                     average=monai.utils.Average.MACRO)
        writer.add_scalar(run_name + "_AUC", auc_metric, epoch + 1)
        wandb.log({run_name + "_AUC": auc_metric})
        return auc_metric


def train_and_save_model(df, count_train, save_path, num_epochs, val_interval, only_evaluate):
    images = []
    decisions = []
    sizes = {}
    for row in df.itertuples():
        if row.exists:
            images.append(row.file_path)
            decision = 0 if row.overall_qa_assessment < 6 else 1
            decisions.append(decision)

            size = row.dimensions
            if size not in sizes:
                sizes[size] = 1
            else:
                sizes[size] += 1

    # 2 binary labels for scan classification: 1=good, 0=bad
    labels = np.asarray(decisions, dtype=np.int64)
    count_val = df.shape[0] - count_train
    train_files = [{"img": img, "label": label} for img, label in zip(images[:count_train], labels[:count_train])]
    val_files = [{"img": img, "label": label} for img, label in zip(images[-count_val:], labels[-count_val:])]

    # TODO: shuffle train_files (if not already done)

    # Define transforms for image
    train_transforms = Compose(
        [
            LoadImaged(keys=["img"]),
            AddChanneld(keys=["img"]),
            ScaleIntensityd(keys=["img"]),
            ToTensord(keys=["img"]),
        ]
    )
    val_transforms = Compose(
        [
            LoadImaged(keys=["img"]),
            AddChanneld(keys=["img"]),
            ScaleIntensityd(keys=["img"]),
            ToTensord(keys=["img"]),
        ]
    )

    if False: # Check size of the first input
        # Define dataset, data loader
        check_ds = monai.data.Dataset(data=train_files, transform=train_transforms)
        check_loader = DataLoader(check_ds, batch_size=1, num_workers=1, pin_memory=torch.cuda.is_available())
        check_data = monai.utils.misc.first(check_loader)
        print(f'Single input\'s shape: {check_data["img"].shape}, label: {check_data["label"]}')

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # calculate class weights
    good_count = np.sum(labels[:count_train])
    bad_count = count_train - good_count
    weights_array = [good_count / count_train, bad_count / count_train]
    print(f"bad_count: {bad_count}, good_count: {good_count}, weights_array: {weights_array}")
    class_weights = torch.tensor(weights_array, dtype=torch.float).to(device)

    samples_weight = np.array([weights_array[t] for t in decisions[:count_train]])
    samples_weight = torch.from_numpy(samples_weight)
    samples_weight = samples_weight.double()
    sampler = torch.utils.data.WeightedRandomSampler(samples_weight, len(samples_weight))

    # create a training data loader
    train_ds = monai.data.Dataset(data=train_files, transform=train_transforms)
    train_loader = DataLoader(train_ds, batch_size=1, sampler=sampler, num_workers=1,
                              pin_memory=torch.cuda.is_available())

    # create a validation data loader
    val_ds = monai.data.Dataset(data=val_files, transform=val_transforms)
    val_loader = DataLoader(val_ds, batch_size=1, num_workers=1, pin_memory=torch.cuda.is_available())

    model = TiledClassifier(in_shape=(1, 128, 48, 48), classes=2,
                            channels=(2, 4, 8, 16),
                            strides=(2, 2, 2, 2,))

    if torch.cuda.is_available() and torch.cuda.device_count() > 1:
        print("Let's use", torch.cuda.device_count(), "GPUs!")
        # dim = 0 [20, xxx] -> [10, ...], [10, ...] on 2 GPUs
        model = torch.nn.DataParallel(model)

    model.to(device)

    if os.path.exists(save_path) and only_evaluate:
        model.load_state_dict(torch.load(save_path))
        print(f"Loaded NN model from file '{save_path}'")
    else:
        print("Training NN from scratch")

    # Create a loss function and Adam optimizer
    if use_focal_loss:
        loss_function = monai.losses.FocalLoss(weight=class_weights, to_onehot_y=True)
    else:
        loss_function = torch.nn.CrossEntropyLoss(weight=class_weights)
    wandb.config.learning_rate = 5e-5
    optimizer = torch.optim.Adam(model.parameters(), wandb.config.learning_rate)
    wandb.watch(model)

    # start a typical PyTorch training
    best_metric = -1
    best_metric_epoch = -1
    writer = SummaryWriter(log_dir=wandb.run.dir)

    if only_evaluate:
        print("Evaluating NN model on validation data")
        evaluate_model(model, val_loader, device, writer, 0, "val")
        print("Evaluating NN model on training data")
        evaluate_model(model, train_loader, device, writer, 0, "train")
        return sizes

    for epoch in range(num_epochs):
        print("-" * 10)
        print(f"epoch {epoch + 1}/{num_epochs}")
        model.train()
        epoch_loss = 0
        step = 0
        epoch_len = len(train_ds) // train_loader.batch_size
        print(f"epoch_len: {epoch_len}")
        y_true = []
        y_pred = []

        for batch_data in train_loader:
            step += 1
            inputs, labels = batch_data["img"].to(device), batch_data["label"].to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            y_true.extend(labels.cpu().tolist())
            y_pred.extend(outputs.cpu().argmax(dim=1).tolist())
            loss = loss_function(outputs, labels)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
            epoch_len = len(train_ds) // train_loader.batch_size
            # print(f"{step}:{loss.item():.4f}", end=' ')
            print(".", end='')
            if step % 70 == 0:
                print("")  # new line
            writer.add_scalar("train_loss", loss.item(), epoch_len * epoch + step)
            wandb.log({"train_loss": loss.item()})
        epoch_loss /= step
        print(f"\nepoch {epoch + 1} average loss: {epoch_loss:.4f}")
        wandb.log({f"epoch average loss": epoch_loss})
        epoch_cm = confusion_matrix(y_true, y_pred)
        print(f"confusion matrix:\n{epoch_cm}")
        wandb.log({f"confusion matrix": epoch_cm})

        if (epoch + 1) % val_interval == 0:
            print("Evaluating on validation set")
            auc_metric = evaluate_model(model, val_loader, device, writer, epoch, "val")

            if auc_metric >= best_metric:
                best_metric = auc_metric
                best_metric_epoch = epoch + 1
                torch.save(model.state_dict(), save_path)
                torch.save(model.state_dict(), os.path.join(wandb.run.dir, 'miqa01.pt'))
                print("saved new best metric model")

            print(
                "current epoch: {} current AUC: {:.4f} best AUC: {:.4f} at epoch {}".format(
                    epoch + 1, auc_metric, best_metric, best_metric_epoch
                )
            )

    epoch_suffix = ".epoch" + str(num_epochs)
    torch.save(model.state_dict(), save_path + epoch_suffix)
    torch.save(model.state_dict(), os.path.join(wandb.run.dir, 'miqa01.pt' + epoch_suffix))

    print(f"train completed, best_metric: {best_metric:.4f} at epoch: {best_metric_epoch}")
    writer.close()
    return sizes


def process_folds(folds_prefix, validation_fold, evaluate_only):
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    wandb.init(project="miqa_01", sync_tensorboard=True)

    folds = []
    for f in range(3):
        folds.append(pd.read_csv(folds_prefix + f"{f}.csv"))

    df = pd.concat(folds)
    print(df)

    print(f"Using fold {validation_fold} for validation")
    vf = folds.pop(validation_fold)
    folds.append(vf)
    df = pd.concat(folds)
    count_train = df.shape[0] - vf.shape[0]
    model_path = os.getcwd() + f"/miqa01-val{validation_fold}.pth"
    sizes = train_and_save_model(df, count_train, save_path=model_path, num_epochs=50, val_interval=2,
                                 only_evaluate=evaluate_only)

    print("Image size distribution:\n", sizes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--predicthd', '-p', help="Path to PredictHD data", type=str)
    parser.add_argument('--ncanda', '-n', help="Path to NCANDA data", type=str)
    parser.add_argument('--folds', '-f', help="Prefix to folds CSVs", type=str)
    parser.add_argument('--vfold', '-v', help="Which fold to use for validation", type=int, default=2)
    # add bool for evaluation
    parser.add_argument('--evaluate', dest='evaluate', action='store_true')
    parser.add_argument('-e', dest='evaluate', action='store_true')
    parser.add_argument('--train', dest='evaluate', action='store_false')
    parser.add_argument('-t', dest='evaluate', action='store_false')
    parser.set_defaults(evaluate=False)
    # add bool for full cross-validation
    parser.add_argument('--all', dest='all', action='store_true')
    parser.set_defaults(all=False)

    args = parser.parse_args()
    # print(args)

    monai.config.print_config()

    if args.all:
        # train all 3 folds
        process_folds(args.folds, 0, False)
        process_folds(args.folds, 1, False)
        process_folds(args.folds, 2, False)
        # evaluate all at the end, so results are easy to pick up from the log
        process_folds(args.folds, 0, True)
        process_folds(args.folds, 1, True)
        process_folds(args.folds, 2, True)
    elif args.folds is not None:
        process_folds(args.folds, args.vfold, args.evaluate)
    elif args.predicthd is not None:
        predict_hd_data_root = args.predicthd
        df = read_and_normalize_data_frame(predict_hd_data_root + r'phenotype/bids_image_qc_information.tsv')
        print(df)
        full_path = Path('bids_image_qc_information-customized.csv').absolute()
        df.to_csv(full_path, index=False)
        print(f"CSV file written: {full_path}")
    elif args.ncanda is not None:
        print("Adding support for NCANDA data is a TODO")
    else:
        print("Not enough arguments specified")
        print(parser.format_help())
