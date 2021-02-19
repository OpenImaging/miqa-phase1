import Promise from "bluebird";
import Vue from "vue";
import Vuex from "vuex";
import vtkProxyManager from "vtk.js/Sources/Proxy/Core/ProxyManager";
import _ from "lodash";

import ReaderFactory from "../utils/ReaderFactory";
import "../utils/registerReaders";

import readImageArrayBuffer from "itk/readImageArrayBuffer";
import WorkerPool from "itk/WorkerPool";
import ITKHelper from "vtk.js/Sources/Common/DataModel/ITKHelper";

import { proxy } from "../vtk";
import { getView } from "../vtk/viewManager";
import girder from "../girder";

const { convertItkToVtkImage } = ITKHelper;

Vue.use(Vuex);

const fileCache = new Map();
const datasetCache = new Map();
var readDataQueue = [];

const poolSize = navigator.hardwareConcurrency / 2 || 2;
let workerPool = new WorkerPool(poolSize, poolFunction);
let taskRunId = -1;
let savedWorker = null;

const store = new Vuex.Store({
  state: {
    drawer: false,
    experimentIds: [],
    experiments: {},
    experimentSessions: {},
    sessions: {},
    sessionDatasets: {},
    datasets: {},
    proxyManager: null,
    vtkViews: [],
    currentDatasetId: null,
    loadingDataset: false,
    errorLoadingDataset: false,
    currentScreenshot: null,
    screenshots: [],
    sites: null,
    sessionCachedPercentage: 0,
    sessionsModifiedTime: new Date().toISOString()
  },
  getters: {
    currentDataset(state) {
      return state.currentDatasetId
        ? state.datasets[state.currentDatasetId]
        : null;
    },
    previousDataset(state, getters) {
      return getters.currentDataset
        ? getters.currentDataset.previousDataset
        : null;
    },
    nextDataset(state, getters) {
      return getters.currentDataset ? getters.currentDataset.nextDataset : null;
    },
    getDataset(state) {
      return function(datasetId) {
        if (!datasetId || !state.datasets[datasetId]) {
          return;
        }
        return state.datasets[datasetId];
      };
    },
    currentSession(state, getters) {
      if (getters.currentDataset) {
        const curSessionId = getters.currentDataset.session;
        return state.sessions[curSessionId];
      }
      return null;
    },
    currentExperiment(state, getters) {
      if (getters.currentSession) {
        const curExperimentId = getters.currentSession.experiment;
        return state.experiments[curExperimentId];
      }
      return null;
    },
    experimentDatasets(state) {
      return function(expId) {
        const experimentSessions = state.experimentSessions[expId];
        const expDatasets = [];
        experimentSessions.forEach(sessionId => {
          const sessionDatasets = state.sessionDatasets[sessionId];
          sessionDatasets.forEach(datasetId => {
            expDatasets.push(datasetId);
          });
        });
        return expDatasets;
      };
    },
    getTodoById: state => id => {
      return state.todos.find(todo => todo.id === id);
    },
    firstDatasetInPreviousSession(state, getters) {
      return getters.currentDataset
        ? getters.currentDataset.firstDatasetInPreviousSession
        : null;
    },
    firstDatasetInNextSession(state, getters) {
      return getters.currentDataset
        ? getters.currentDataset.firstDatasetInNextSession
        : null;
    },
    firstDatasetInPreviousExeriment(state, getters) {
      if (getters.currentExperiment) {
        const expIdx = getters.currentExperiment.index;
        if (expIdx >= 1) {
          const prevExp = state.experiments[state.experimentIds[expIdx - 1]];
          const prevExpSessions = state.experimentSessions[prevExp.id];
          const prevExpSessionDatasets =
            state.sessionDatasets[prevExpSessions[0].id];
          return prevExpSessionDatasets[0];
        }
      }
      return null;
    },
    firstDatasetInNextExeriment(state, getters) {
      if (getters.currentExperiment) {
        const expIdx = getters.currentExperiment.index;
        if (expIdx < state.experimentIds.length - 1) {
          const nextExp = state.experiments[state.experimentIds[expIdx + 1]];
          const nextExpSessions = state.experimentSessions[nextExp.id];
          const nextExpSessionDatasets =
            state.sessionDatasets[nextExpSessions[0].id];
          return nextExpSessionDatasets[0];
        }
      }
      return null;
    },
    siteMap(state) {
      if (!state.sites) {
        return {};
      } else {
        return _.keyBy(state.sites, "name");
      }
    },
    getSiteDisplayName(state, getters) {
      return function(name) {
        var siteMap = getters.siteMap;
        if (
          siteMap[name] &&
          siteMap[name].meta &&
          siteMap[name].meta.displayName
        ) {
          return siteMap[name].meta.displayName;
        } else {
          return name;
        }
      };
    }
  },
  mutations: {
    setDrawer(state, value) {
      state.drawer = value;
    },
    setCurrentScreenshot(state, screenshot) {
      state.currentScreenshot = screenshot;
    },
    addScreenshot(state, screenshot) {
      state.screenshots.push(screenshot);
    },
    removeScreenshot(state, screenshot) {
      state.screenshots.splice(state.screenshots.indexOf(screenshot), 1);
    }
  },
  actions: {
    async loadSessions({ state }) {
      let { data: sessionTree } = await girder.rest.get(`miqa/sessions`);

      state.experimentIds = [];
      state.experiments = {};
      state.experimentSessions = {};
      state.sessions = {};
      state.sessionDatasets = {};
      state.datasets = {};

      // Build navigation links throughout the dataset to improve performance.
      let firstInPrev = null;

      for (let i = 0; i < sessionTree.length; i++) {
        let experiment = sessionTree[i];
        let experimentId = experiment.folderId;

        state.experimentIds.push(experimentId);
        state.experiments[experimentId] = {
          id: experimentId,
          folderId: experimentId,
          name: experiment.name,
          index: i
        };

        let sessions = experiment.sessions.sort(
          (a, b) => a.meta.scanId - b.meta.scanId
        );

        state.experimentSessions[experimentId] = [];

        for (let j = 0; j < sessions.length; j++) {
          let session = sessions[j];
          let sessionId = session.folderId;

          state.experimentSessions[experimentId].push(sessionId);
          state.sessions[sessionId] = {
            id: sessionId,
            folderId: sessionId,
            name: session.name,
            meta: Object.assign({}, session.meta),
            numDatasets: session.datasets.length,
            cumulativeRange: [Number.MAX_VALUE, -Number.MAX_VALUE], // [null, null],
            experiment: experimentId
          };

          state.sessionsModifiedTime = new Date().toISOString();

          state.sessionDatasets[sessionId] = [];

          for (let k = 0; k < session.datasets.length; k++) {
            let dataset = session.datasets[k];
            let datasetId = dataset._id;

            state.sessionDatasets[sessionId].push(datasetId);
            state.datasets[datasetId] = Object.assign({}, dataset);
            state.datasets[datasetId].session = sessionId;
            state.datasets[datasetId].index = k;
            state.datasets[datasetId].previousDataset =
              k > 0 ? session.datasets[k - 1]._id : null;
            state.datasets[datasetId].nextDataset =
              k < session.datasets.length - 1
                ? session.datasets[k + 1]._id
                : null;
            state.datasets[
              datasetId
            ].firstDatasetInPreviousSession = firstInPrev;
          }
          firstInPrev = session.datasets[0]._id;
        }
      }

      // Now iterate through the session tree backwards to build up the links
      // to the "firstInNext" datasets.
      let firstInNext = null;

      for (let i = sessionTree.length - 1; i >= 0; i--) {
        let experiment = sessionTree[i];
        for (let j = experiment.sessions.length - 1; j >= 0; j--) {
          let session = experiment.sessions[j];
          for (let k = session.datasets.length - 1; k >= 0; k--) {
            let datasetId = session.datasets[k]._id;
            let dataset = state.datasets[datasetId];
            dataset.firstDatasetInNextSession = firstInNext;
          }
          firstInNext = session.datasets[0]._id;
        }
      }
    },
    async swapToDataset({ state, getters }, dataset) {
      if (!dataset) {
        throw new Error(`dataset id doesn't exist`);
      }
      if (getters.currentDataset === dataset) {
        return;
      }
      state.loadingDataset = true;
      state.errorLoadingDataset = false;
      var oldSession = getters.currentSession;
      const newSession = state.sessions[dataset.session];
      const oldExperiment = getters.currentExperiment
        ? getters.currentExperiment
        : null;
      const newExperimentId = state.sessions[dataset.session].experiment;
      const newExperiment = state.experiments[newExperimentId];

      // Check if we should cancel the currently loading experiment
      if (
        newExperiment &&
        oldExperiment &&
        newExperiment.folderId !== oldExperiment.folderId &&
        taskRunId >= 0
      ) {
        workerPool.cancel(taskRunId);
        taskRunId = -1;
      }

      var newProxyManager = false;
      if (oldSession !== newSession && state.proxyManager) {
        // If we don't "shrinkProxyManager()" and reinitialize it between
        // "sessions" (a.k.a "scans"), then we can end up with no image
        // slices displayed, even though we have the data and attempted
        // to render it.  This may be due to image extents changing between
        // scans, which is not the case from one timestep of a single scan
        // to tne next.
        shrinkProxyManager(state.proxyManager);
        newProxyManager = true;
      }

      if (!state.proxyManager || newProxyManager) {
        state.proxyManager = vtkProxyManager.newInstance({
          proxyConfiguration: proxy
        });
        state.vtkViews = [];
      }

      let sourceProxy = state.proxyManager.getActiveSource();
      let needPrep = false;
      if (!sourceProxy) {
        sourceProxy = state.proxyManager.createProxy(
          "Sources",
          "TrivialProducer"
        );
        needPrep = true;
      }

      // This try catch and within logic are mainly for handling data doesn't exist issue
      try {
        let imageData = null;
        if (datasetCache.has(dataset._id)) {
          imageData = datasetCache.get(dataset._id).imageData;
        } else {
          const result = await loadFileAndGetData(dataset._id);
          imageData = result.imageData;
        }
        sourceProxy.setInputData(imageData);
        if (needPrep || !state.proxyManager.getViews().length) {
          prepareProxyManager(state.proxyManager);
          state.vtkViews = state.proxyManager.getViews();
        }
        if (!state.vtkViews.length) {
          state.vtkViews = state.proxyManager.getViews();
        }
      } catch (err) {
        console.log("Caught exception loading next image");
        console.log(err);
        state.vtkViews = [];
        state.errorLoadingDataset = true;
      } finally {
        state.currentDatasetId = dataset._id;
        state.loadingDataset = false;
      }

      // If necessary, queue loading scans of new experiment
      checkLoadExperiment(oldExperiment, newExperiment);
    },
    async loadSites({ state }) {
      let { data: sites } = await girder.rest.get("miqa_setting/site");
      state.sites = sites;
    }
  }
});

// cache datasets associated with sessions of current experiment
function checkLoadExperiment(oldValue, newValue) {
  if (
    !newValue ||
    newValue === oldValue ||
    (newValue && oldValue && newValue.folderId === oldValue.folderId)
  ) {
    return;
  }

  if (oldValue) {
    const oldExperimentSessions = store.state.experimentSessions[oldValue.id];
    oldExperimentSessions.forEach(sessionId => {
      const sessionDatasets = store.state.sessionDatasets[sessionId];
      sessionDatasets.forEach(datasetId => {
        fileCache.delete(datasetId);
        datasetCache.delete(datasetId);
      });
      const session = store.state.sessions[sessionId];
      session.cached = false;
      store.state.sessionsModifiedTime = new Date().toISOString();
    });
  }

  readDataQueue = [];
  const newExperimentSessions = store.state.experimentSessions[newValue.id];
  newExperimentSessions.forEach(sessionId => {
    const sessionDatasets = store.state.sessionDatasets[sessionId];
    sessionDatasets.forEach(datasetId => {
      readDataQueue.push({ id: datasetId });
    });
    readDataQueue.push({
      status: "sessionLoaded",
      sessionId
    });
  });
  startReaderWorkerPool();
}

function prepareProxyManager(proxyManager) {
  if (!proxyManager.getViews().length) {
    ["View2D_Z:z", "View2D_X:x", "View2D_Y:y"].forEach(type => {
      let view = getView(proxyManager, type);
      view.setOrientationAxesVisibility(false);
      view.getRepresentations().forEach(representation => {
        representation.onModified(() => {
          view.render(true);
        });
      });
    });
  }
}

function shrinkProxyManager(proxyManager) {
  proxyManager.getViews().forEach(view => {
    view.setContainer(null);
    proxyManager.deleteProxy(view);
  });
}

function loadFile(id) {
  if (fileCache.has(id)) {
    return { id, fileP: fileCache.get(id) };
  }
  let p = ReaderFactory.downloadDataset(
    girder.rest,
    "nifti.nii.gz",
    `/item/${id}/download`
  );
  fileCache.set(id, p);
  return { id, fileP: p };
}

function getData(id, file, webWorker = null) {
  return new Promise((resolve, reject) => {
    if (datasetCache.has(id)) {
      resolve({ imageData: datasetCache.get(id), webWorker });
    } else {
      const fileName = file.name;
      const io = new FileReader();

      io.onload = function onLoad() {
        readImageArrayBuffer(webWorker, io.result, fileName)
          .then(({ webWorker, image }) => {
            const imageData = convertItkToVtkImage(image, {
              scalarArrayName: getArrayName(fileName)
            });
            const dataRange = imageData
              .getPointData()
              .getArray(0)
              .getRange();
            datasetCache.set(id, { imageData });
            expandSessionRange(id, dataRange);
            resolve({ imageData, webWorker });
          })
          .catch(error => {
            console.log("Problem reading image array buffer");
            console.log("webworker", webWorker);
            console.log("fileName", fileName);
            console.log(error);
            reject(error);
          });
      };

      io.readAsArrayBuffer(file);
    }
  });
}

function loadFileAndGetData(id) {
  return loadFile(id).fileP.then(file => {
    return getData(id, file, savedWorker)
      .then(({ webWorker, imageData }) => {
        savedWorker = webWorker;
        return Promise.resolve({ imageData });
      })
      .catch(error => {
        const msg = "loadFileAndGetData caught error getting data";
        console.log(msg);
        console.log(error);
        return Promise.reject(msg);
      })
      .finally(() => {
        if (savedWorker) {
          savedWorker.terminate();
          savedWorker = null;
        }
      });
  });
}

function getArrayName(filename) {
  const idx = filename.lastIndexOf(".");
  const name = idx > -1 ? filename.substring(0, idx) : filename;
  return `Scalars ${name}`;
}

function poolFunction(webWorker, taskInfo) {
  return new Promise((resolve, reject) => {
    if ("status" in taskInfo) {
      const { sessionId } = taskInfo;
      const session = store.state.sessions[sessionId];
      session.cached = true;
      store.state.sessionsModifiedTime = new Date().toISOString();
      resolve({ imageData: null, webWorker });
    } else {
      const { id } = taskInfo;

      let filePromise = null;

      if (fileCache.has(id)) {
        filePromise = fileCache.get(id);
      } else {
        filePromise = ReaderFactory.downloadDataset(
          girder.rest,
          "nifti.nii.gz",
          `/item/${id}/download`
        );
        fileCache.set(id, filePromise);
      }

      filePromise
        .then(file => {
          resolve(getData(id, file, webWorker));
        })
        .catch(err => {
          console.log("poolFunction: fileP error of some kind");
          console.log(err);
          reject(err);
        });
    }
  });
}

function progressHandler(completed, total) {
  const percentComplete = completed / total;
  store.state.sessionCachedPercentage = percentComplete;
}

function startReaderWorkerPool() {
  const taskArgsArray = [];

  readDataQueue.forEach(taskInfo => {
    taskArgsArray.push([taskInfo]);
  });

  readDataQueue = [];

  const { runId, promise } = workerPool.runTasks(
    taskArgsArray,
    progressHandler
  );
  taskRunId = runId;

  promise
    .then(results => {
      console.log(`WorkerPool finished with ${results.length} results`);
      taskRunId = -1;
    })
    .catch(err => {
      console.log("startReaderWorkerPool: workerPool error");
      console.log(err);
    })
    .finally(() => {
      workerPool.terminateWorkers();
    });
}

function expandSessionRange(datasetId, dataRange) {
  const sessionId = store.state.datasets[datasetId].session;
  const session = store.state.sessions[sessionId];
  if (dataRange[0] < session.cumulativeRange[0]) {
    session.cumulativeRange[0] = dataRange[0];
  }
  if (dataRange[1] > session.cumulativeRange[1]) {
    session.cumulativeRange[1] = dataRange[1];
  }
}

export default store;
