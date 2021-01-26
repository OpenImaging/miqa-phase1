import os
import shutil
import tempfile

from girder import logger
from girder_worker_utils.transforms.girder_io import GirderClientTransform


class TextToFile(GirderClientTransform):
    def __init__(self, stringIO, **kwargs):
        super(TextToFile, self).__init__(**kwargs)
        self.stringIO = stringIO

    def _repr_model_(self):
        return "{}".format(self.__class__.__name__)

    def transform(self):
        self.file_path = os.path.join(
            tempfile.mkdtemp(), 'session.csv')

        with open(self.file_path, "w") as csv_file:
            self.stringIO.seek(0)
            shutil.copyfileobj(self.stringIO, csv_file)

        return self.file_path

    def cleanup(self):
        logger.info('TextToFile will cleanup {0}'.format(self.file_path))
        shutil.rmtree(os.path.dirname(self.file_path),
                      ignore_errors=True)
