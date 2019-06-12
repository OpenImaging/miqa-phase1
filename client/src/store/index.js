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
    currentDatasetId: null,
    loadingDataset: false,
    errorLoadingDataset: false,
    currentScreenshot: null,
    screenshots: [],
    sites: null,
    sessionCachedPercentage: 0
  },
  getters: {
    currentDataset(state, getters) {
      if (!state.currentDatasetId || !getters.allDatasets) {
        return;
      }
      return getters.allDatasets.find(
        dataset => dataset._id === state.currentDatasetId
      );
    },
    allDatasets(state) {
      if (!state.sessionTree) {
        return;
      }
      return _.flatMap(state.sessionTree, experiment => {
        return _.flatMap(experiment.sessions, session => session.datasets);
      });
    },
    allDatasetIds(state, getters) {
      if (!getters.allDatasets) {
        return [];
      }
      return getters.allDatasets.map(dataset => dataset._id);
    },
    previousDataset(state, getters) {
      if (!getters.currentDataset || !getters.allDatasets) {
        return;
      }
      var index = getters.allDatasets.indexOf(getters.currentDataset);
      return getters.allDatasets.slice(index - 1, index)[0];
    },
    nextDataset(state, getters) {
      if (!getters.currentDataset || !getters.allDatasets) {
        return;
      }
      var index = getters.allDatasets.indexOf(getters.currentDataset);
      return getters.allDatasets.slice(index + 1, index + 2)[0];
    },
    // nextNextDataset(state, getters) {
    //   if (!getters.currentDataset || !getters.allDatasets) {
    //     return;
    //   }
    //   var index = getters.allDatasets.indexOf(getters.currentDataset);
    //   return getters.allDatasets.slice(index + 2, index + 3)[0];
    // },
    getDataset(state, getters) {
      return function(datasetId) {
        if (!datasetId || !getters.allDatasets) {
          return;
        }
        return getters.allDatasets.find(dataset => dataset._id === datasetId);
      };
    },
    currentSession(state, getters) {
      if (!getters.currentDataset || !state.sessionTree) {
        return;
      }
      for (let experiment of state.sessionTree) {
        for (let session of experiment.sessions) {
          for (let dataset of session.datasets) {
            if (dataset === getters.currentDataset) {
              return session;
            }
          }
        }
      }
    },
    firstDatasetInPreviousSession(state, getters) {
      if (!getters.currentDataset || !state.sessionTree) {
        return;
      }
      let takeNext = false;
      for (let i = state.sessionTree.length - 1; i >= 0; i--) {
        let experiment = state.sessionTree[i];
        for (let j = experiment.sessions.length - 1; j >= 0; j--) {
          let session = experiment.sessions[j];
          for (let dataset of session.datasets) {
            if (takeNext) {
              return dataset;
            }
            if (dataset === getters.currentDataset) {
              takeNext = true;
              break;
            }
          }
        }
      }
    },
    firstDatasetInNextSession(state, getters) {
      if (!getters.currentDataset || !state.sessionTree) {
        return;
      }
      let takeNext = false;
      for (let experiment of state.sessionTree) {
        for (let session of experiment.sessions) {
          for (let dataset of session.datasets) {
            if (takeNext) {
              return dataset;
            }
            if (dataset === getters.currentDataset) {
              takeNext = true;
              break;
            }
          }
        }
      }
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
      var temp = state.currentDatasetId;
      // Use side effect to get the new session, logically correct but should be improved
      state.currentDatasetId = dataset["_id"];
      var newSession = getters.currentSession;
      // Use currentDataset to detect the change of proxyManager, logically correct but should be improved
      state.currentDatasetId = temp;
      var newProxyManager = false;
      if (oldSession !== newSession && state.proxyManager) {
        // At this moment. use new proxyManger between session could avoid a not showing issue.
        // However maybe unnecessary
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
        state.currentDatasetId = dataset["_id"];
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
    return { id, fileP: Promise.resolve(fileCache.get(id)) };
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
