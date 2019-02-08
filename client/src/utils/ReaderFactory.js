import vtkHttpDataAccessHelper from 'vtk.js/Sources/IO/Core/DataAccessHelper/HttpDataAccessHelper';

const READER_MAPPING = {};

const FETCH_DATA = {
  readAsArrayBuffer(url, progressCallback) {
    return vtkHttpDataAccessHelper.fetchBinary(url, { progressCallback });
  },
  readAsText(url, progressCallback) {
    return vtkHttpDataAccessHelper.fetchText({}, url, { progressCallback });
  },
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
  binary,
}) {
  READER_MAPPING[extension] = {
    name,
    vtkReader,
    readMethod: readMethod || binary ? 'readAsArrayBuffer' : 'readAsText',
    parseMethod: parseMethod || binary ? 'parseAsArrayBuffer' : 'parseAsText',
    fileNameMethod,
    fileSeriesMethod,
    sourceType,
  };
}

function getReader({ name }) {
  const lowerCaseName = name.toLowerCase();
  const extToUse = Object.keys(READER_MAPPING).find((ext) =>
    lowerCaseName.endsWith(ext)
  );
  return READER_MAPPING[extToUse];
}

function listReaders() {
  return Object.keys(READER_MAPPING).map((ext) => ({
    name: READER_MAPPING[ext].name,
    ext,
  }));
}

function listSupportedExtensions() {
  return Object.keys(READER_MAPPING);
}

// ----------------------------------------------------------------------------

let filesCallback = null;

function handleFile(e) {
  if (filesCallback) {
    filesCallback(e.target.files);
  }
  filesCallback = null;
}

const HIDDEN_FILE_ELEMENT = document.createElement('input');
HIDDEN_FILE_ELEMENT.setAttribute('type', 'file');
HIDDEN_FILE_ELEMENT.setAttribute('multiple', 'multiple');
HIDDEN_FILE_ELEMENT.addEventListener('change', handleFile);

// ----------------------------------------------------------------------------

function openFiles(extensions, onFilesCallback) {
  filesCallback = onFilesCallback;
  HIDDEN_FILE_ELEMENT.setAttribute(
    'accept',
    extensions.map((t) => `.${t}`).join(',')
  );
  HIDDEN_FILE_ELEMENT.value = null;
  HIDDEN_FILE_ELEMENT.click();
}

// ----------------------------------------------------------------------------

function readRawData({ fileName, data }) {
  return new Promise((resolve, reject) => {
    const readerMapping = getReader({ name: fileName });
    if (readerMapping) {
      const {
        vtkReader,
        parseMethod,
        fileNameMethod,
        sourceType,
      } = readerMapping;
      const reader = vtkReader.newInstance();
      if (fileNameMethod) {
        reader[fileNameMethod](fileName);
      }
      const ds = reader[parseMethod](data);
      Promise.resolve(ds)
        .then((dataset) =>
          resolve({ dataset, reader, sourceType, name: fileName })
        )
        .catch(reject);
    } else {
      reject();
    }
  });
}

// ----------------------------------------------------------------------------

function readFile(file) {
  return new Promise((resolve, reject) => {
    const readerMapping = getReader(file);
    if (readerMapping) {
      const { readMethod } = readerMapping;
      const io = new FileReader();
      io.onload = function onLoad() {
        readRawData({ fileName: file.name, data: io.result })
          .then((result) => resolve(result))
          .catch((error) => reject(error));
      };
      io[readMethod](file);
    } else {
      reject(new Error('No reader mapping'));
    }
  });
}

// ----------------------------------------------------------------------------

function loadFiles(files) {
  const promises = [];
  for (let i = 0; i < files.length; i += 1) {
    promises.push(readFile(files[i]));
  }
  return Promise.all(promises);
}

// ----------------------------------------------------------------------------

function loadFileSeries(files, extension, outFileName = '') {
  return new Promise((resolve, reject) => {
    if (files.length) {
      const readerMapping = READER_MAPPING[extension];
      if (readerMapping) {
        const {
          vtkReader,
          fileSeriesMethod,
          fileNameMethod,
          sourceType,
        } = readerMapping;
        const reader = vtkReader.newInstance();

        if (fileNameMethod) {
          reader[fileNameMethod](outFileName);
        }

        if (fileSeriesMethod) {
          const ds = reader[fileSeriesMethod](files);
          Promise.resolve(ds).then((dataset) =>
            resolve({ dataset, reader, sourceType, name: outFileName })
          );
        } else {
          reject(new Error('No file series method available'));
        }
      } else {
        reject(new Error(`No file series reader mapping for ${extension}`));
      }
    } else {
      resolve(/* empty */);
    }
  });
}

// ----------------------------------------------------------------------------

function downloadDataset(fileName, url, progressCallback) {
  return new Promise((resolve, reject) => {
    const readerMapping = getReader({ name: fileName });
    if (readerMapping) {
      const { readMethod } = readerMapping;
      FETCH_DATA[readMethod](url, progressCallback)
        .then((rawData) => {
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

// ----------------------------------------------------------------------------

function registerReadersToProxyManager(readers, proxyManager) {
  for (let i = 0; i < readers.length; i += 1) {
    const { reader, sourceType, name, dataset, metadata } = readers[i];
    if (reader || dataset) {
      const needSource =
        (reader && reader.getOutputData) ||
        (dataset && dataset.isA && dataset.isA('vtkDataSet'));
      const source = needSource
        ? proxyManager.createProxy(
          'Sources',
          'TrivialProducer',
          Object.assign({ name }, metadata)
        )
        : null;
      if (dataset && dataset.isA && dataset.isA('vtkDataSet')) {
        source.setInputData(dataset, sourceType);
      } else if (reader && reader.getOutputData) {
        source.setInputAlgorithm(reader, sourceType);
      } else if (reader && reader.setProxyManager) {
        reader.setProxyManager(proxyManager);
      } else {
        console.error(`No proper reader handler was found for ${name}`);
      }

      if (source) {
        source.activate();

        proxyManager.createRepresentationInAllViews(source);
        proxyManager.renderAllViews();
      }
    }
  }
}

// ----------------------------------------------------------------------------

export default {
  downloadDataset,
  openFiles,
  loadFiles,
  loadFileSeries,
  registerReader,
  listReaders,
  listSupportedExtensions,
  registerReadersToProxyManager,
};

export {
  downloadDataset,
  openFiles,
  loadFiles,
  loadFileSeries,
  registerReader,
  listReaders,
  listSupportedExtensions,
  registerReadersToProxyManager,
};
