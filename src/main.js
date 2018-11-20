import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

console.log(store);

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
          "View3D:default": {
            "background": "linear-gradient(#333, #999)"
          }
        },
        "viewOrder": [
          "View3D:default",
          "View2D_Y:y",
          "View2D_X:x",
          "View2D_Z:z"
        ],
        "viewCount": 1
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
          "name": "Tooth.nrrd",
          "type": "vtkImageData",
          "dataset": {
            "name": "Tooth.nrrd",
            "url": "https://kitware.github.io/vtk-js-datasets/data/nrrd/tooth.nrrd"
          }
        }
      }
    ],
    "views": [
      {
        "id": "2",
        "group": "Views",
        "name": "View3D",
        "props": {
          "name": "default",
          "background": [
            0,
            0,
            0,
            0
          ],
          "orientationAxesVisibility": true,
          "presetToOrientationAxes": "default",
          "axis": 1,
          "orientation": -1,
          "viewUp": [
            0,
            0,
            1
          ]
        },
        "camera": {
          "position": [
            59.64408757817353,
            351.43683761826696,
            151.43217173739623
          ],
          "viewUp": [
            0.6086385846138,
            -0.19728314876556396,
            0.768530011177063
          ],
          "focalPoint": [
            51,
            46.5,
            80
          ]
        }
      }
    ],
    "representations": [
      {
        "source": "3",
        "view": "2",
        "props": {
          "colorBy": [
            "Scalars Tooth",
            "pointData",
            -1
          ],
          "volumeVisibility": true,
          "useShadow": true,
          "sampleDistance": 0.4,
          "edgeGradient": 0.61,
          "windowWidth": 255,
          "windowLevel": 127,
          "sliceVisibility": false,
          "xSlice": 51,
          "ySlice": 47,
          "zSlice": 80
        }
      }
    ],
    "fields": {
      "Scalars Tooth": {
        "lookupTable": {
          "mode": 0,
          "presetName": "Default (Cool to Warm)",
          "rgbPoints": [
            [
              0,
              0,
              0,
              0
            ],
            [
              1,
              1,
              1,
              1
            ]
          ],
          "hsvPoints": [
            [
              0,
              0,
              0,
              0
            ],
            [
              1,
              0,
              0,
              1
            ]
          ],
          "nodes": [
            {
              "x": 0,
              "r": 0,
              "g": 0,
              "b": 0,
              "midpoint": 0.5,
              "sharpness": 0
            },
            {
              "x": 1,
              "r": 1,
              "g": 1,
              "b": 1,
              "midpoint": 0.5,
              "sharpness": 0
            }
          ],
          "arrayName": "Scalars Tooth",
          "arrayLocation": "pointData",
          "dataRange": [
            0,
            255
          ]
        },
        "piecewiseFunction": {
          "mode": 0,
          "gaussians": [
            {
              "position": 0.5,
              "height": 1,
              "width": 0.5,
              "xBias": 0.5,
              "yBias": 0.5
            }
          ],
          "points": [
            [
              0,
              0
            ],
            [
              1,
              1
            ]
          ],
          "nodes": [
            {
              "x": 0,
              "y": 0,
              "midpoint": 0.5,
              "sharpness": 0
            },
            {
              "x": 1,
              "y": 1,
              "midpoint": 0.5,
              "sharpness": 0
            }
          ],
          "arrayName": "Scalars Tooth",
          "arrayLocation": "pointData",
          "dataRange": [
            0,
            255
          ]
        }
      }
    }
  });
}, 0);