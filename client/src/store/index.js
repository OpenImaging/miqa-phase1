import Vue from "vue";
import Vuex from "vuex";
import vtkProxyManager from "vtk.js/Sources/Proxy/Core/ProxyManager";
import _ from "lodash";

import ReaderFactory from "../utils/ReaderFactory";
import "../utils/registerReaders";

import { proxy } from "../vtk";
import { getView } from "../vtk/viewManager";
import proxyConfigGenerator from "./proxyConfigGenerator";

import { API_URL } from "../constants";
import girder from "../girder";

const PRELOAD_SIZE = 6;
const CACHE_SIZE = PRELOAD_SIZE + 6;
const CACHE_DELAY_INTERVAL = 1500;

Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    drawer: false,
    batches: null,
    sessionTreeCache: {},
    sessionTree: null,
    proxyManager: null,
    vtkViews: [],
    proxyManagerCache: {},
    pendingCaching: new Map(),
    currentDatasetId: null,
    loadingDataset: false,
    currentScreenshot: null,
    screenshots: []
  },
  getters: {
    currentDataset(state) {
      if (!state.currentDatasetId || !state.sessionTree) {
        return;
      }
      for (let experiment of state.sessionTree.experiments) {
        for (let session of experiment.sessions) {
          for (let dataset of session.datasets) {
            if (dataset._id === state.currentDatasetId) {
              return dataset;
            }
          }
        }
      }
    },
    allDatasets(state) {
      if (!state.sessionTree) {
        return;
      }
      return _.flatMap(state.sessionTree.experiments, experiment => {
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
    nextNextDataset(state, getters) {
      if (!getters.currentDataset || !getters.allDatasets) {
        return;
      }
      var index = getters.allDatasets.indexOf(getters.currentDataset);
      return getters.allDatasets.slice(index + 2, index + 3)[0];
    },
    getDataset(state) {
      return function(datasetId) {
        if (!datasetId || !state.sessionTree) {
          return;
        }
        for (let experiment of state.sessionTree.experiments) {
          for (let session of experiment.sessions) {
            for (let dataset of session.datasets) {
              if (dataset._id === datasetId) {
                return dataset;
              }
            }
          }
        }
      };
    },
    currentSession(state, getters) {
      if (!getters.currentDataset || !state.sessionTree) {
        return;
      }
      for (let experiment of state.sessionTree.experiments) {
        for (let session of experiment.sessions) {
          for (let dataset of session.datasets) {
            if (dataset === getters.currentDataset) {
              return session;
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
      for (let experiment of state.sessionTree.experiments) {
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
    selectSessionTreeByDataset(state, datasetId) {
      var sessionTree = tryFindSessionTreeByDatasetId(state, datasetId);
      state.sessionTree = sessionTree;
    }
  },
  actions: {
    async loadBatches({ state }) {
      let { data: batches } = await girder.rest.get("miqa/batch");
      state.batches = batches;
    },
    async loadSessionsByBatchId({ state }, batchId) {
      let { data: sessionTree } = await girder.rest.get(
        `miqa/batch/${batchId}/sessions`
      );
      var matchingBatch = _.find(
        state.batches,
        batch => batch._id === sessionTree.batch._id
      );
      if (matchingBatch) {
        Vue.set(state.sessionTreeCache, matchingBatch._id, sessionTree);
      }
    },
    async loadAndSetSessionsByDatasetId({ state }, datasetId) {
      var sessionTree = tryFindSessionTreeByDatasetId(state, datasetId);
      if (sessionTree) {
        state.sessionTree = sessionTree;
      } else {
        let { data: sessionTree } = await girder.rest.get(
          `miqa/dataset/${datasetId}/sessions`
        );
        var matchingBatch = _.find(
          state.batches,
          batch => batch._id === sessionTree.batch._id
        );
        if (matchingBatch) {
          Vue.set(state.sessionTreeCache, matchingBatch._id, sessionTree);
        }
        state.sessionTree = sessionTree;
      }
    },
    cacheDataset({ state }, dataset) {
      var cached = state.proxyManagerCache[dataset._id];
      if (cached) {
        if (!cached.then) {
          return Promise.resolve();
        } else {
          return cached;
        }
      }
      let url = `${API_URL}/item/${dataset._id}/download`;
      var proxyManager = vtkProxyManager.newInstance({
        proxyConfiguration: proxy
      });
      var config = proxyConfigGenerator(url);
      var caching = proxyManager
        .loadState(config, {
          datasetHandler(ds) {
            return ReaderFactory.downloadDataset(girder.rest, ds.name, ds.url)
              .then(file => {
                return ReaderFactory.loadFiles([file]).then(
                  readers => readers[0]
                );
              })
              .then(({ reader }) => {
                if (reader && reader.getOutputData) {
                  const newDS = reader.getOutputData();
                  newDS.set(ds, true); // Attach remote data origin
                  return newDS;
                }
                throw new Error("Invalid dataset");
              })
              .catch(e => {
                // more meaningful error
                const moreInfo = `Dataset doesn't exist or adblock/firewall prevents access.`;
                if ("xhr" in e) {
                  const { xhr } = e;
                  throw new Error(
                    `${xhr.statusText} (${xhr.status}): ${moreInfo}`
                  );
                }
                throw new Error(`${e.message} (${moreInfo})`);
              });
          }
        })
        .then(() => {
          evictProxyManagerCache();
          Vue.set(state.proxyManagerCache, dataset._id, proxyManager);
          return proxyManager;
        });
      Vue.set(state.proxyManagerCache, dataset._id, caching);
      return caching;
    },
    async swapToDataset({ dispatch, state, getters }, datasetId) {
      state.loadingDataset = true;
      state.currentDatasetId = datasetId;
      let dataset = getters.currentDataset;
      if (!dataset) {
        throw new Error(`dataset id doesn't exist`);
      }
      await dispatch("cacheDataset", dataset);
      let proxyManager = state.proxyManagerCache[dataset._id];

      function change() {
        state.proxyManager = proxyManager;
        state.vtkViews = proxyManager.getViews();
        state.loadingDataset = false;
      }
      if (proxyManager.getViews().length) {
        change();
      } else {
        // Give progress inidicator a chance to show if proxy views are not ready
        setTimeout(() => {
          prepareProxyManager(proxyManager);
          change();
        }, 0);
      }
    }
  }
});

store.watch(
  (state, getters) => [getters.currentDataset, getters.allDatasets],
  ([currentDataset, allDatasets]) => {
    if (!currentDataset || !allDatasets) {
      return;
    }
    var state = store.state;
    var currentDatasetIndex = allDatasets.indexOf(currentDataset);
    var datasetsToCache = allDatasets.slice(
      currentDatasetIndex + 1,
      currentDatasetIndex + 1 + PRELOAD_SIZE
    );
    state.pendingCaching.forEach(value => {
      clearTimeout(value);
    });
    state.pendingCaching.clear();

    shrinkUnnecessaryProxyManager();

    var queue = 0;
    datasetsToCache.forEach(async dataset => {
      if (dataset._id in state.proxyManagerCache) {
        if (
          dataset === store.getters.nextDataset ||
          dataset === store.getters.nextNextDataset
        ) {
          if (state.proxyManagerCache[dataset._id].then) {
            await state.proxyManagerCache[dataset._id];
          }
          prepareProxyManager(state.proxyManagerCache[dataset._id]);
        }
        return;
      }
      clearTimeout(state.pendingCaching.get(dataset._id));
      state.pendingCaching.set(
        dataset._id,
        setTimeout(async () => {
          state.pendingCaching.delete(dataset._id);
          var proxyManger = await store.dispatch("cacheDataset", dataset);
          if (
            dataset === store.getters.nextDataset ||
            dataset === store.getters.nextNextDataset
          ) {
            prepareProxyManager(proxyManger);
          }
        }, queue++ * CACHE_DELAY_INTERVAL)
      );
    });
  }
);

store.watch(
  (state, getters) => getters.previousDataset,
  dataset => {
    if (!dataset) {
      return;
    }
    var state = store.state;
    clearTimeout(state.pendingCaching.get(dataset._id));
    state.pendingCaching.set(
      dataset._id,
      setTimeout(() => {
        state.pendingCaching.delete(dataset._id);
        store.dispatch("cacheDataset", dataset);
      }, 4000)
    );
  }
);

// Helper for debugging cache
// store.watch(
//   state => state.proxyManagerCache,
//   proxyManagerCache => {
//     var allDatasetIds = store.getters.allDatasetIds;
//     console.log(
//       _.sortBy(Object.keys(proxyManagerCache), datasetId =>
//         allDatasetIds.indexOf(datasetId)
//       ).map(
//         datasetId =>
//           "" +
//           allDatasetIds.indexOf(datasetId) +
//           (proxyManagerCache[datasetId].then
//             ? ":loading"
//             : proxyManagerCache[datasetId].getViews().length
//             ? ":prepared"
//             : "") +
//           (datasetId === store.state.currentDatasetId ? ":current" : "")
//       )
//     );
//   },
//   { deep: true }
// );

function prepareProxyManager(proxyManager) {
  if (!proxyManager.getViews().length) {
    var update = () => {
      proxyManager.renderAllViews();
      // proxyManager.autoAnimateViews();
    };
    ["View2D_Z:z", "View2D_X:x", "View2D_Y:y"].forEach(type => {
      let view = getView(proxyManager, type);
      view.setOrientationAxesVisibility(false);
      view.getRepresentations().forEach(representation => {
        representation.onModified(update);
      });
    });
  }
}

function shrinkProxyManager(proxyManager) {
  if (!proxyManager.then) {
    proxyManager.getViews().forEach(view => {
      view.setContainer(null);
      proxyManager.deleteProxy(view);
    });
  }
}

function evictProxyManagerCache() {
  var { state, getters } = store;
  var cachedDatasetIds = Object.keys(state.proxyManagerCache);
  // console.log(cachedDatasetIds);
  if (cachedDatasetIds.length > CACHE_SIZE) {
    var allDatasetIds = getters.allDatasetIds;
    var currentDatasetIndex = allDatasetIds.indexOf(state.currentDatasetId);
    cachedDatasetIds = cachedDatasetIds.filter(datasetId => {
      var index = allDatasetIds.indexOf(datasetId);
      index = index === -1 ? null : index;
      // don't evict current and previous dataset
      return index !== currentDatasetIndex && index !== currentDatasetIndex - 1;
    });
    // sort by left and right of current dataset then by distance to current dataset
    cachedDatasetIds = _.sortBy(cachedDatasetIds, datasetId => {
      var d = allDatasetIds.indexOf(datasetId) - currentDatasetIndex;
      // use property of reciprocal function
      return d < 0 ? d : 1 / d;
    });
    // evict the lowerest ranked dataset
    shrinkProxyManager(state.proxyManagerCache[cachedDatasetIds[0]]);
    Vue.delete(state.proxyManagerCache, cachedDatasetIds[0]);
  }
}

function shrinkUnnecessaryProxyManager() {
  var { state, getters } = store;
  Object.keys(state.proxyManagerCache)
    .filter(datasetId => !state.proxyManagerCache[datasetId].then)
    .filter(
      datasetId =>
        datasetId !== getters.currentDataset._id &&
        (!getters.previousDataset ||
          datasetId !== getters.previousDataset._id) &&
        (!getters.nextDataset || datasetId !== getters.nextDataset._id) &&
        (!getters.nextNextDataset || datasetId !== getters.nextNextDataset._id)
    )
    .forEach(datasetId => {
      shrinkProxyManager(state.proxyManagerCache[datasetId]);
    });
}

function tryFindSessionTreeByDatasetId(state, datasetId) {
  for (var sessionTree of Object.values(state.sessionTreeCache)) {
    for (let experiment of sessionTree.experiments) {
      for (let session of experiment.sessions) {
        for (let dataset of session.datasets) {
          if (dataset._id === datasetId) {
            return sessionTree;
          }
        }
      }
    }
  }
}

export default store;
