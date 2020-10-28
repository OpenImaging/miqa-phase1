import Snackbar from "./Snackbar";

export default function(vuetify) {
  return function install(Vue) {
    Snackbar.vuetify = vuetify;
    var SnackbarComponent = Vue.extend(Snackbar);
    var component = new SnackbarComponent();
    Vue.prototype.$snackbarAttach = function(options) {
      if (options) {
        component.$data.options = options;
      }
      var div = document.createElement("div");
      this.$el.appendChild(div);
      component.$mount(div);
      return this;
    };
    Vue.prototype.$snackbar = function({
      text,
      button,
      callback,
      timeout,
      immediate
    }) {
      function set() {
        component.$data.text = text;
        component.$data.button = button;
        component.$data.callback = callback;
        component.$data.timeout = timeout || 2000;
        component.$data.show = true;
      }
      if (!component.$data.show) {
        set();
      } else {
        if (immediate) {
          component.$data.show = false;
          setTimeout(set, 0);
        } else {
          var unwatch = component.$watch("show", () => {
            unwatch();
            set();
          });
        }
      }
    };
    Vue.prototype.$snackbar.hide = function() {
      component.$data.show = false;
    };
    Vue.prototype.$snackbar.setOptions = function(options) {
      component.$data.options = options;
    };
  };
}
