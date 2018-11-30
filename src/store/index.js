import Vue from 'vue';
import Vuex from 'vuex';
import vtkProxyManager from 'vtk.js/Sources/Proxy/Core/ProxyManager';

import ReaderFactory from '../utils/ReaderFactory';
import '../utils/ParaViewGlanceReaders';
import Presets from '../vtk/ColorMaps';

import { proxy } from '../vtk';
import { getView } from '../vtk/viewManager';
// import { DEFAULT_VIEW_TYPE } from '../vtk/constants';

Vue.use(Vuex);

const proxyManager = vtkProxyManager.newInstance({ proxyConfiguration: proxy });
window.proxyManager = proxyManager;
// console.log(proxyManager);

// let view = getView(proxyManager, DEFAULT_VIEW_TYPE);
// console.log(view);

export default new Vuex.Store({
  state: {
    proxyManager,
    views: {},
    vtkViews: []
  },
  mutations: {

  },
  actions: {
    loadState({ commit, dispatch, state, getters }, appState) {
      // console.log(JSON.stringify(appState, null, 4));
      return state.proxyManager
        .loadState(appState, {
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
                  reader.setProxyManager(state.proxyManager);
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
        })
        .then((userData) => {
          // this.replaceState(merge(state, appState.userData));
          merge(state, appState.userData);

          // Wait for the layout to be done (nextTick is not enough)
          setTimeout(() => {
            // Advertise that state loading is done
            // commit(Mutations.LOADING_STATE, false);

            // Force update
            state.proxyManager.modified();

            // Activate visible view with a preference for the 3D one
            // const visibleViews = state.proxyManager
            //   .getViews()
            //   .filter((view) => view.getContainer());
            // const view3D = visibleViews.find(
            //   (view) => view.getProxyName() === 'View3D'
            // );
            // const viewToActivate = view3D || visibleViews[0];
            // if (viewToActivate) {
            //   viewToActivate.activate();
            // }

            // Make sure pre-existing view (not expected in state) have a representation
            state.proxyManager
              .getSources()
              .forEach(state.proxyManager.createRepresentationInAllViews);

            state.views.viewOrder.forEach(type => {
              state.vtkViews.push(getView(state.proxyManager, type));
            })
          }, 100);
        });
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