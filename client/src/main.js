import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import Girder, { RestClient } from "@girder/components/src";
import { API_URL } from "./constants";

import vMousetrap from "./utils/vMousetrap";
import girder from "./girder";

import "vuetify/dist/vuetify.min.css";

// import proxyConfigGenerator from './store/proxyConfigGenerator';

Vue.use(Girder);
Vue.use(vMousetrap);

girder.rest = new RestClient({ apiRoot: API_URL });

// console.log(store);
window.store = store;

Vue.config.productionTip = true;

girder.rest.fetchUser().then(() => {
  new Vue({
    router,
    store,
    render: h => h(App),
    provide: { girderRest: girder.rest }
  }).$mount("#app");
});
