import Vue from 'vue';
import Vuex from 'vuex';
import vtkProxyManager from 'vtk.js/Sources/Proxy/Core/ProxyManager';
import _ from 'lodash';

import ReaderFactory from '../utils/ReaderFactory';
import '../utils/ParaViewGlanceReaders';
import Presets from '../vtk/ColorMaps';

import { proxy } from '../vtk';
import { getView } from '../vtk/viewManager';
import proxyConfigGenerator from './proxyConfigGenerator';

import { API_URL } from '../constants';
import girder from '../girder';

Vue.use(Vuex);

// const proxyManager = vtkProxyManager.newInstance({ proxyConfiguration: proxy });
// window.proxyManager = proxyManager;
// console.log(proxyManager);

// let view = getView(proxyManager, DEFAULT_VIEW_TYPE);
// console.log(view);

const store = new Vuex.Store({
  state: {
    drawer: true,
    proxyManager: null,
    sessionTree: null,
    vtkViews: [],
    proxyManagerCache: {},
    proxyManagerCacheList: [],
    currentDataset: null,
    loadingDataset: false,
  },
  getters: {
    nextDataset(state) {
      if (!state.currentDataset || !state.sessionTree) {
        return;
      }
      let takeNext = false;
      for (let batch of state.sessionTree) {
        for (let session of batch.sessions) {
          for (let dataset of session.datasets) {
            if (dataset === state.currentDataset) {
              takeNext = true;
              continue;
            }
            if (takeNext) {
              return dataset;
            }
          }
        }
      }
    },
    previousDataset(state) {
      let previousDataset = null;
      if (!state.currentDataset || !state.sessionTree) {
        return;
      }
      for (let batch of state.sessionTree) {
        for (let session of batch.sessions) {
          for (let dataset of session.datasets) {
            if (dataset === state.currentDataset) {
              return previousDataset;
            }
            previousDataset = dataset;
          }
        }
      }
    },
    currentSesssionDatasets(state) {
      if (!state.currentDataset || !state.sessionTree) {
        return;
      }
      for (let batch of state.sessionTree) {
        for (let session of batch.sessions) {
          for (let dataset of session.datasets) {
            if (dataset === state.currentDataset) {
              return session.datasets;
            }
          }
        }
      }
    }
  },
  mutations: {
    setDrawer(state, value) {
      state.drawer = value;
    }
  },
  actions: {
    async loadSessions({ state }) {
      let { data: sessionTree } = await girder.rest.get('miqa/sessions');
      state.sessionTree = sessionTree;
    },
    // async setDataset({ state, dispatch }, dataset) {
    //   let dataset = await dispatch('cacheDataset', dataset);
    //   store.dispatch('swapToDataset', dataset);
    //   state.currentDataset = dataset;
    // },
    cacheDataset({ commit, dispatch, state, getters }, dataset) {
      var cached = state.proxyManagerCache[dataset._id];
      if (cached) {
        if (!cached.then) {
          return Promise.resolve();
        }
        else {
          return cached;
        }
      }
      let url = `${API_URL}/item/${dataset._id}/download`;
      var proxyManager = vtkProxyManager.newInstance({ proxyConfiguration: proxy });
      var config = proxyConfigGenerator(url);
      var caching = proxyManager
        .loadState(config, {
          datasetHandler(ds) {
            // if (ds.vtkClass) {
            // return vtk(ds);
            // }
            return ReaderFactory.downloadDataset(ds.name, ds.url)
              .then((file) => {
                return ReaderFactory.loadFiles([file]);
              })
              .then((readers) => readers[0])
              .then(({ dataset, reader }) => {
                if (reader && reader.getOutputData) {
                  const newDS = reader.getOutputData();
                  newDS.set(ds, true); // Attach remote data origin
                  return newDS;
                }
                if (dataset && dataset.isA) {
                  dataset.set(ds, true); // Attach remote data origin
                  return dataset;
                }
                if (reader && reader.setProxyManager) {
                  reader.setProxyManager(proxyManager);
                  return null;
                }
                throw new Error('Invalid dataset');
              })
              .catch((e) => {
                // more meaningful error
                const moreInfo = `Dataset doesn't exist or adblock/firewall prevents access.`;
                if ('xhr' in e) {
                  const { xhr } = e;
                  throw new Error(
                    `${xhr.statusText} (${xhr.status}): ${moreInfo}`
                  );
                }
                throw new Error(`${e.message} (${moreInfo})`);
              });
          },
        }).then((userData) => {
          // this.replaceState(merge(state, appState.userData));
          // merge(state, appState.userData);

          // Wait for the layout to be done (nextTick is not enough)
          return new Promise((resolve, reject) => {
            setTimeout(() => {
              proxyManager.modified();

              resolve();
            }, 100)
          });
        }).then(() => {
          console.log('pushed');
          Vue.set(state.proxyManagerCache, dataset._id, proxyManager);
          state.proxyManagerCacheList.push(dataset);
          if (state.proxyManagerCacheList.length > 4) {
            let dataset = state.proxyManagerCacheList.shift();
            Vue.delete(state.proxyManagerCache, dataset._id);
          }
          return proxyManager;
        });
      Vue.set(state.proxyManagerCache, dataset._id, caching);
      return caching;
    },
    async swapToDataset({ commit, dispatch, state, getters }, dataset) {
      state.loadingDataset = true;
      // if (!state.proxyManagerCache[dataset._id]) {
      await dispatch('cacheDataset', dataset);
      // }
      state.currentDataset = dataset;
      let proxyManager = state.proxyManagerCache[dataset._id];

      function change() {
        prepareProxyManager(proxyManager);
        state.proxyManager = proxyManager;
        state.vtkViews = proxyManager.getViews();
        state.loadingDataset = false;
      }
      // Give progress inidicator a chance to show if proxy views are not ready, even though it will be blocked so it won't animate
      if (proxyManager.getViews().length) {
        change();
      } else {
        setTimeout(() => {
          change();
        }, 0);
      }
    }
  },
  // getters: {
  //   vtkViews(state, getters) {
  //     if (!state.views || !state.views.viewOrder) {
  //       return [];
  //     }
  //     return state.views.viewOrder
  //       .filter((v, i) => i < state.views.viewCount)
  //       .map((type) => getView(state.proxyManager, type))
  //   }
  // }
});



store.watch((state, getters) => getters.nextDataset, _.debounce((nextDataset) => {
  console.log('caching next dataset');
  if (nextDataset) {
    store.dispatch('cacheDataset', nextDataset);
  }
  // console.log(nextDataset);
}, 1500));

store.watch((state, getters) => getters.previousDataset, _.debounce((previousDataset) => {
  console.log('caching previous dataset');
  if (previousDataset) {
    store.dispatch('cacheDataset', previousDataset);
  }
}, 3000));

function prepareProxyManager(proxyManager) {
  if (!proxyManager.getViews().length) {
    var update = () => {
      proxyManager.autoAnimateViews();
    }

    ["View2D_Z:z", "View2D_X:x", "View2D_Y:y"].forEach(type => {
      let view = getView(proxyManager, type);
      view.getRepresentations().forEach(representation => {
        representation.onModified(update);
      });
    });
  }
}


// http://jsperf.com/typeofvar
function typeOf(o) {
  return {}.toString
    .call(o)
    .slice(8, -1)
    .toLowerCase();
}

// quick object merge using Vue.set
/* eslint-disable no-param-reassign */
function merge(dst, src) {
  const keys = Object.keys(src);
  for (let i = 0; i < keys.length; ++i) {
    const key = keys[i];
    if (typeOf(dst[key]) === 'object' && typeOf(src[key]) === 'object') {
      Vue.set(dst, key, merge(dst[key], src[key]));
    } else {
      Vue.set(dst, key, src[key]);
    }
  }
  return dst;
}
/* eslint-enable no-param-reassign */

export default store;
