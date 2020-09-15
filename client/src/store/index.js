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
    sessionTree: null,
    proxyManager: null,
    vtkViews: [],
    currentDataset: null,
    loadingDataset: false,
    errorLoadingDataset: false,
    currentScreenshot: null,
    screenshots: [],
    sites: null,
    sessionCachedPercentage: 0
  },
  getters: {
    currentDatasetId(state) {
      return state.currentDataset ? state.currentDataset["_id"] : null;
    },
    allDatasets(state) {
      if (!state.sessionTree) {
        return;
      }
      return _.flatMap(state.sessionTree, experiment => {
        return _.flatMap(experiment.sessions, session => session.datasets);
      });
    },
    previousDataset(state) {
      return state.currentDataset ? state.currentDataset.previousDataset : null;
    },
    nextDataset(state) {
      return state.currentDataset ? state.currentDataset.nextDataset : null;
    },
    getDataset(state, getters) {
      return function(datasetId) {
        if (!datasetId || !getters.allDatasets) {
          return;
        }
        return getters.allDatasets.find(dataset => dataset._id === datasetId);
      };
    },
    currentSession(state) {
      return state.currentDataset ? state.currentDataset.session : null;
    },
    firstDatasetInPreviousSession(state) {
      return state.currentDataset
        ? state.currentDataset.firstDatasetInPreviousSession
        : null;
    },
    firstDatasetInNextSession(state) {
      return state.currentDataset
        ? state.currentDataset.firstDatasetInNextSession
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
      state.sessionTree = sessionTree.map(experiment => {
        return {
          ...experiment,
          ...{
            sessions: experiment.sessions.sort(
              (a, b) => a.meta.scanId - b.meta.scanId
            )
          }
        };
      });

      // Build navigation links throughout the dataset to improve performance.

      // First iterate through the session tree forwards to build up "previous" links
      let previousDataset = null;
      let firstInPrev = null;

      for (let i = 0; i < state.sessionTree.length; i++) {
        let experiment = state.sessionTree[i];
        for (let j = 0; j < experiment.sessions.length; j++) {
          let session = experiment.sessions[j];
          for (let k = 0; k < session.datasets.length; k++) {
            let dataset = session.datasets[k];
            dataset.session = session;
            dataset.index = k;
            dataset.previousDataset = previousDataset;
            dataset.firstDatasetInPreviousSession = firstInPrev;
            previousDataset = dataset;
          }
          firstInPrev = session.datasets[0];
        }
      }

      // Now iterate through the session tree backwards to build up "next" links
      let nextDataset = null;
      let firstInNext = null;

      for (let i = state.sessionTree.length - 1; i >= 0; i--) {
        let experiment = state.sessionTree[i];
        for (let j = experiment.sessions.length - 1; j >= 0; j--) {
          let session = experiment.sessions[j];
          for (let k = session.datasets.length - 1; k >= 0; k--) {
            let dataset = session.datasets[k];
            dataset.nextDataset = nextDataset;
            dataset.firstDatasetInNextSession = firstInNext;
            nextDataset = dataset;
          }
          firstInNext = session.datasets[0];
        }
      }
    },
    async swapToDataset({ state, getters }, dataset) {
      if (!dataset) {
        throw new Error(`dataset id doesn't exist`);
      }
      // console.log('debug here');
      if (state.currentDataset === dataset) {
        return;
      }
      state.loadingDataset = true;
      state.errorLoadingDataset = false;
      var oldSession = getters.currentSession;
      const newSession = dataset.session;
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
        state.currentDataset = dataset;
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
      oldValue.datasets.forEach(dataset => {
        fileCache.delete(dataset._id);
        datasetCache.delete(dataset._id);
      });
      readDataQueue = [];
    }
    readDataQueue = newValue.datasets.map(dataset => {
      return loadFile(dataset._id);
    });
    if (store.getters.firstDatasetInNextSession) {
      readDataQueue.unshift(
        loadFile(store.getters.firstDatasetInNextSession._id)
      );
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
  var percentage =
    store.getters.currentSession.datasets.reduce((total, dataset) => {
      return total + (datasetCache.has(dataset._id) ? 1 : 0);
    }, 0) / store.getters.currentSession.datasets.length;
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
