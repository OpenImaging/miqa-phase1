import Vue from 'vue'
import Router from 'vue-router'
import Sessions from './views/Sessions.vue'
import Dataset from './views/Dataset.vue'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/sessions',
      name: 'sessions',
      component: Sessions
    },
    {
      path: '/',
      name: 'dataset',
      component: Dataset
    }
  ]
})
