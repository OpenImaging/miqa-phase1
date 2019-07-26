import os
import shutil
import tempfile
import time


def retrain(csv_path=None):
    # pseudo code
    # if not csv_path:
        # retrain model with the master csv
        # return None
    # else:
    #     csv = read(csv_path)
    #     if csv has rows with decision:
    #         update master csv and retrain model
    #     evalute all rows with model regard less if there is a decision and save the score to a dedicate column
    #     return a path to the new csv file with new scores

    # dummy code below
    with open(csv_path, 'r') as csv_file:
        print(csv_file.read())
    new_path = os.path.join(
        tempfile.mkdtemp(), 'new_session.csv')
    time.sleep(4)
    shutil.copyfile(csv_path, new_path)
    print(csv_path, new_path)
    return new_path
