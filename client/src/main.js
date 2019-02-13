import Vue from "vue";
import AsyncComputed from "vue-async-computed";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import Girder, { RestClient } from "@girder/components/src";
import { API_URL, STATIC_PATH } from "./constants";

import vMousetrap from "vue-utilities/v-mousetrap";
import snackbarService from "vue-utilities/snackbar-service";
import girder from "./girder";

import "vuetify/dist/vuetify.min.css";

// import proxyConfigGenerator from './store/proxyConfigGenerator';

Vue.use(AsyncComputed);
Vue.use(Girder);
Vue.use(vMousetrap);
Vue.use(snackbarService);

girder.rest = new RestClient({ apiRoot: API_URL });

import config from "itk/itkConfig";
config.itkModulesPath = STATIC_PATH + config.itkModulesPath;

// console.log(store);
window.store = store;

Vue.config.productionTip = true;

girder.rest.fetchUser().then(() => {
  new Vue({
    router,
    store,
    render: h => h(App),
    provide: { girderRest: girder.rest }
  })
    .$mount("#app")
    .$snackbarAttach();
});
