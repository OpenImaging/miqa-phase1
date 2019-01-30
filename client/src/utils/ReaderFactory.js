import vtkHttpDataAccessHelper from "vtk.js/Sources/IO/Core/DataAccessHelper/HttpDataAccessHelper";

const READER_MAPPING = {};

const FETCH_DATA = {
  readAsArrayBuffer(url, progressCallback) {
    return vtkHttpDataAccessHelper.fetchBinary(url, { progressCallback });
  },
  readAsText(url, progressCallback) {
    return vtkHttpDataAccessHelper.fetchText({}, url, { progressCallback });
  }
};

function registerReader({
  extension,
  name,
  vtkReader,
  readMethod,
  parseMethod,
  fileNameMethod,
  fileSeriesMethod,
  sourceType,
  binary
}) {
  READER_MAPPING[extension] = {
    name,
    vtkReader,
    readMethod: readMethod || binary ? "readAsArrayBuffer" : "readAsText",
    parseMethod: parseMethod || binary ? "parseAsArrayBuffer" : "parseAsText",
    fileNameMethod,
    fileSeriesMethod,
    sourceType
  };
}

function getReader({ name }) {
  const lowerCaseName = name.toLowerCase();
  const extToUse = Object.keys(READER_MAPPING).find(ext =>
    lowerCaseName.endsWith(ext)
  );
  return READER_MAPPING[extToUse];
}

function readRawData({ fileName, data }) {
  return new Promise((resolve, reject) => {
    const readerMapping = getReader({ name: fileName });
    if (readerMapping) {
      const {
        vtkReader,
        parseMethod,
        fileNameMethod,
        sourceType
      } = readerMapping;
      const reader = vtkReader.newInstance();
      if (fileNameMethod) {
        reader[fileNameMethod](fileName);
      }
      const ds = reader[parseMethod](data);
      Promise.resolve(ds)
        .then(dataset =>
          resolve({ dataset, reader, sourceType, name: fileName })
        )
        .catch(reject);
    } else {
      reject();
    }
  });
}

function readFile(file) {
  return new Promise((resolve, reject) => {
    const readerMapping = getReader(file);
    if (readerMapping) {
      const { readMethod } = readerMapping;
      const io = new FileReader();
      io.onload = function onLoad() {
        readRawData({ fileName: file.name, data: io.result })
          .then(result => resolve(result))
          .catch(error => reject(error));
      };
      io[readMethod](file);
    } else {
      reject(new Error("No reader mapping"));
    }
  });
}

function loadFiles(files) {
  const promises = [];
  for (let i = 0; i < files.length; i += 1) {
    promises.push(readFile(files[i]));
  }
  return Promise.all(promises);
}

function downloadDataset(fileName, url, progressCallback) {
  return new Promise((resolve, reject) => {
    const readerMapping = getReader({ name: fileName });
    if (readerMapping) {
      const { readMethod } = readerMapping;
      FETCH_DATA[readMethod](url, progressCallback)
        .then(rawData => {
          if (rawData) {
            resolve(new File([rawData], fileName));
          } else {
            throw new Error(`No data for ${fileName}`);
          }
        })
        .catch(reject);
    } else {
      throw new Error(`No reader found for ${fileName}`);
    }
  });
}

export default {
  downloadDataset,
  loadFiles,
  registerReader
};
