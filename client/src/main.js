import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import Girder, { RestClient } from '@girder/components/src';
import { API_URL } from './constants';

import girder from './girder';

import 'vuetify/dist/vuetify.min.css'

// import proxyConfigGenerator from './store/proxyConfigGenerator';

Vue.use(Girder);

girder.rest = new RestClient({ apiRoot: API_URL });

// console.log(store);
window.store = store;

Vue.config.productionTip = true

girder.rest.fetchUser().then(() => {
  store.dispatch('loadSessions');

  new Vue({
    router,
    store,
    render: h => h(App),
    provide: { girderRest: girder.rest },
  }).$mount('#app');
});


// setTimeout(async () => {
//   // store.dispatch('loadState', proxyConfigGenerator('image.nii.gz'));
//   let proxyManager = await store.dispatch('cacheDataset', 'image.nii.gz');
//   store.dispatch('swapToDataset', { proxyManager });
// }, 0);

// setTimeout(async () => {
//   let proxyManager = await store.dispatch('cacheDataset', 'http://localhost:8081/api/v1/file/5c1070866cc2491028ad84d4/download?contentDisposition=inline');
//   store.dispatch('swapToDataset', { proxyManager });
// }, 2000);
