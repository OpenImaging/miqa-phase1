import Vue from "vue";
import Router from "vue-router";

import girder from "./girder";
import Settings from "./views/Settings.vue";
import Dataset from "./views/Dataset.vue";
import Login from "./views/Login.vue";
import Metrics from "./views/Metrics.vue";

Vue.use(Router);

function beforeEnter(to, from, next) {
  if (!girder.rest.user) {
    next("/login");
  } else {
    next();
  }
}

function beforeEnterAdmin(to, from, next) {
  if (!girder.rest.user) {
    next("/login");
  } else {
    if (!girder.rest.user.admin) {
      next("/");
    } else {
      next();
    }
  }
}

export default new Router({
  routes: [
    {
      path: "/login",
      name: "login",
      component: Login
    },
    {
      path: "/settings",
      name: "settings",
      component: Settings,
      beforeEnter: beforeEnterAdmin
    },
    {
      path: "/metrics",
      name: "metrics",
      component: Metrics,
      beforeEnter: beforeEnterAdmin
    },
    // Order matters
    {
      path: "/:datasetId?",
      name: "dataset",
      component: Dataset,
      beforeEnter
    },
    {
      path: "*",
      redirect: "/"
    }
  ]
});
