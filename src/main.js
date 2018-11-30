import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// console.log(store);
window.store = store;

Vue.config.productionTip = false

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')

setTimeout(() => {
  store.dispatch('loadState', {
    "userData": {
      "route": "app",
      "global": {
        "backgroundColor": "linear-gradient(#333, #999)",
        "orientationAxis": true,
        "orientationPreset": "default",
        "axisType": "arrow"
      },
      "views": {
        "viewData": {
        },
        "viewOrder": [
          "View3D:default",
          "View2D_Z:z",
          "View2D_Y:y",
          "View2D_X:x"
        ],
        "viewCount": 4
      }
    },
    "options": {
      "recycleViews": true
    },
    "sources": [
      {
        "id": "3",
        "group": "Sources",
        "name": "TrivialProducer",
        "props": {
          "name": "image.nii.gz",
          "type": "vtkImageData",
          "dataset": {
            "name": "image.nii.gz",
            "url": "http://localhost:8085/image.nii.gz"
          }
        }
      }
    ],
    "views": [
    ],
    "representations": [
    ],
    "fields": {
    }
  });
}, 0);