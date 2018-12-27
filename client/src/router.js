import Vue from 'vue'
import Router from 'vue-router'

import girder from './girder'
import Sessions from './views/Sessions.vue'
import Dataset from './views/Dataset.vue'
import Login from './views/Login.vue'


Vue.use(Router)

function beforeEnter(to, from, next) {
  if (!girder.rest.user) {
    next('/login');
  } else {
    next();
  }
}

export default new Router({
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/sessions',
      name: 'sessions',
      component: Sessions,
      beforeEnter
    },
    {
      path: '/',
      name: 'dataset',
      component: Dataset,
      beforeEnter
    }, {
      path: '*',
      redirect: '/'
    }
  ]
})
