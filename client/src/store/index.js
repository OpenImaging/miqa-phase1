import Vue from "vue";
import Vuex from "vuex";
import vtkProxyManager from "vtk.js/Sources/Proxy/Core/ProxyManager";
import _ from "lodash";

import ReaderFactory from "../utils/ReaderFactory";
import "../utils/registerReaders";

import { proxy } from "../vtk";
import { getView } from "../vtk/viewManager";
import girder from "../girder";

Vue.use(Vuex);

const fileCache = new Map();
const datasetCache = new Map();
var readDataQueue = [];

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
    sessionCachedPercentage: 0
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

      console.log("breakpoint sessionTree");

      // Build navigation links throughout the dataset to improve performance.
      let firstInPrev = null;

      for (let i = 0; i < sessionTree.length; i++) {
        let experiment = sessionTree[i];
        let experimentId = experiment.folderId;

        state.experimentIds.push(experimentId);
        state.experiments[experimentId] = {
          id: experimentId,
          folderId: experimentId,
          name: experiment.name
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

          state.sessionDatasets[sessionId] = [];

          for (let k = 0; k < session.datasets.length; k++) {
            let dataset = session.datasets[k];
            let datasetId = dataset._id;

            state.sessionDatasets[sessionId].push(datasetId);
            state.datasets[datasetId] = Object.assign(
              {
                cached: false
              },
              dataset
            );
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
      var newProxyManager = false;
      if (oldSession !== newSession && state.proxyManager) {
        // At this moment. use new proxyManger between session could avoid a not showing issue.
        // However maybe unnecessary
        shrinkProxyManager(state.proxyManager);
        newProxyManager = true;
        readDataQueue.forEach(({ fileP }) => {
          fileP.cancel();
        });
        readDataQueue = [];
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

      calculateCachedPercentage();
      // This try catch and within logic are mainly for handling data doesn't exist issue
      try {
        var imagedata = await loadFileAndGetData(dataset._id);
        sourceProxy.setInputData(imagedata);
        if (needPrep || !state.proxyManager.getViews().length) {
          prepareProxyManager(state.proxyManager);
          state.vtkViews = state.proxyManager.getViews();
        }
        if (!state.vtkViews.length) {
          state.vtkViews = state.proxyManager.getViews();
        }
      } catch {
        state.vtkViews = [];
        state.errorLoadingDataset = true;
      } finally {
        state.currentDatasetId = dataset._id;
        state.loadingDataset = false;
      }
    },
    async loadSites({ state }) {
      let { data: sites } = await girder.rest.get("miqa_setting/site");
      state.sites = sites;
    }
  }
});

// cache datasets of current session and first dataset of next session
store.watch(
  (state, getters) => getters.currentSession,
  (newValue, oldValue) => {
    if (
      !newValue ||
      newValue === oldValue ||
      (newValue && oldValue && newValue.folderId === oldValue.folderId)
    ) {
      return;
    }
    if (oldValue) {
      const oldSessionDatasets = store.state.sessionDatasets[oldValue.id];
      oldSessionDatasets.forEach(datasetId => {
        fileCache.delete(datasetId);
        datasetCache.delete(datasetId);
      });
      readDataQueue = [];
    }
    const newSessionDatasets = store.state.sessionDatasets[newValue.id];
    readDataQueue = newSessionDatasets.map(datasetId => {
      return loadFile(datasetId);
    });
    if (store.getters.firstDatasetInNextSession) {
      readDataQueue.unshift(loadFile(store.getters.firstDatasetInNextSession));
    }
    var concurrency = navigator.hardwareConcurrency + 1 || 2;
    calculateCachedPercentage();
    for (var i = 0; i < concurrency; i++) {
      startReaderWorker();
    }
  }
);

function prepareProxyManager(proxyManager) {
  if (!proxyManager.getViews().length) {
    var handler = null;
    var update = () => {
      proxyManager.renderAllViews();
      // proxyManager.autoAnimateViews();
    };
    ["View2D_Z:z", "View2D_X:x", "View2D_Y:y"].forEach(type => {
      let view = getView(proxyManager, type);
      view.setOrientationAxesVisibility(false);
      view.getRepresentations().forEach(representation => {
        representation.onModified(() => {
          clearTimeout(handler);
          handler = setTimeout(update);
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

function getData(id, file) {
  return ReaderFactory.loadFiles([file])
    .then(readers => readers[0])
    .then(({ reader }) => {
      var imageData = reader.getOutputData();
      const dataRange = imageData
        .getPointData()
        .getArray(0)
        .getRange();
      console.log(`vtkImageData array range ${dataRange}`);
      datasetCache.set(id, imageData);
      return imageData;
    });
}

function loadFileAndGetData(id) {
  if (datasetCache.has(id)) {
    return Promise.resolve(datasetCache.get(id));
  }
  var p = loadFile(id).fileP.then(file => {
    return getData(id, file);
  });
  datasetCache.set(id, p);
  return p;
}

var calculateCachedPercentage = _.throttle(() => {
  if (!store.getters.currentSession) {
    return;
  }
  const currentSession = store.getters.currentSession;
  const sessionDatasets = store.state.sessionDatasets[currentSession.id];
  var percentage =
    sessionDatasets.reduce((total, datasetId) => {
      return total + (datasetCache.has(datasetId) ? 1 : 0);
    }, 0) / sessionDatasets.length;
  store.state.sessionCachedPercentage = percentage;
}, 500);

async function startReaderWorker() {
  var data = readDataQueue.shift();
  if (!data) {
    return;
  }
  var { id, fileP } = data;
  var file = await fileP;
  await getData(id, file);
  calculateCachedPercentage();
  if (readDataQueue.length) {
    setTimeout(() => {
      startReaderWorker();
    });
  }
}

export default store;
