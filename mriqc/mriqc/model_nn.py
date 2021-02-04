#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from girder import logger
from datetime import datetime
import os
import glob

import random
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report

torch.manual_seed(1983)  # maybe remove this later?


class trainData(Dataset):
    def __init__(self, X_data, y_data):
        self.X_data = X_data
        self.y_data = y_data

    def __getitem__(self, index):
        return self.X_data[index], self.y_data[index]

    def __len__(self):
        return len(self.X_data)


class testData(Dataset):
    def __init__(self, X_data):
        self.X_data = X_data

    def __getitem__(self, index):
        return self.X_data[index]

    def __len__(self):
        return len(self.X_data)


class binaryClassification(nn.Module):
    def __init__(self):
        super(binaryClassification, self).__init__()
        # First number is fixed: it is the number of input features
        self.layer_1 = nn.Linear(58, 64)
        self.layer_2 = nn.Linear(64, 64)
        self.layer_out = nn.Linear(64, 1)

        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(p=0.1)
        self.batchnorm1 = nn.BatchNorm1d(64)
        self.batchnorm2 = nn.BatchNorm1d(64)

    def forward(self, inputs):
        x = self.relu(self.layer_1(inputs))
        x = self.batchnorm1(x)
        x = self.relu(self.layer_2(x))
        x = self.batchnorm2(x)
        x = self.dropout(x)
        x = self.layer_out(x)

        return x


def binary_acc(y_pred, y_test):
    y_pred_tag = torch.round(torch.sigmoid(y_pred))

    correct_results_sum = (y_pred_tag == y_test).sum().float()
    acc = correct_results_sum / y_test.shape[0]
    acc = torch.round(acc * 100)

    return acc


def debug(msg):
    logger.info(msg)
    print(msg)


class ModelNN():
    '''
    This class defines the model that we'll be using for our image quality prediction task.
    Here we use neural network via PyTorch library.
    '''

    def __init__(self):
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model = binaryClassification()
        self.model.to(self.device)

    def fit(self, X, y):
        '''
        This function is to fit the data to the model.

        Args:
            X: features of the data to be fit
            y: the true labels
        Returns:
            None
        '''
        # debug('features')
        # debug(X)
        # debug('labels')
        # debug(y)

        train_data = trainData(torch.FloatTensor(X), torch.FloatTensor(y))
        train_loader = DataLoader(dataset=train_data, batch_size=64, shuffle=True)

        # debug(self.model)
        criterion = nn.BCEWithLogitsLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)

        self.model.train()
        for e in range(0, 10):
            epoch_loss = 0
            epoch_acc = 0
            for X_batch, y_batch in train_loader:
                X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)
                optimizer.zero_grad()

                y_pred = self.model(X_batch)

                loss = criterion(y_pred, y_batch.unsqueeze(1))
                acc = binary_acc(y_pred, y_batch.unsqueeze(1))

                loss.backward()
                optimizer.step()

                epoch_loss += loss.item()
                epoch_acc += acc.item()

            print(
                f'Epoch {e + 0:03}: | Loss: {epoch_loss / len(train_loader):.5f} | Acc: {epoch_acc / len(train_loader):.3f}')

        # save the current model
        debug("Finished training")
        debug(self.model)

    def predict_proba(self, X):
        '''
        This function is to predict the probabilities of the input the data.

        Args:
            X: data to be predicted
        Returns:
            prob_good: array for the probabilities of data point being good
        '''
        test_data = testData(torch.FloatTensor(X))
        test_loader = DataLoader(dataset=test_data, batch_size=1)

        y_pred_list = []
        self.model.eval()
        with torch.no_grad():
            for X_batch in test_loader:
                X_batch = X_batch.to(self.device)
                y_test_pred = self.model(X_batch)
                y_test_pred = torch.sigmoid(y_test_pred)
                y_pred_list.append(y_test_pred.cpu().numpy())

        y_pred_list = [a.squeeze().tolist() for a in y_pred_list]
        return y_pred_list

    def save_model(self, model_path):
        '''
        This function saves the trained model in the given path

        Args:
            model_path: The path where the model needs to be saved
        Returns:
            None
        '''
        if not os.path.isdir(model_path):
            os.mkdir(model_path)

        file_name = os.path.join(model_path, 'nnc_' + datetime.now().strftime("%Y%m%d-%H%M%S") + '.pth')
        torch.save(self.model.state_dict(), file_name)

    def load_model(self, model_path):
        '''
        This function loads the most recently saved trained model in the given path

        Args:
            model_path: The path where the model needs to be saved
        Returns:
            None
        '''
        saved_models = glob.glob(os.path.join(model_path, '*.pth'))
        chckpt = max(saved_models, key=os.path.getctime)
        self.model.load_state_dict(torch.load(chckpt))
