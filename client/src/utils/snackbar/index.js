import Snackbar from "./Snackbar";

export default function install(Vue) {
  var SnackbarComponent = Vue.extend(Snackbar);
  var component = new SnackbarComponent();
  Vue.prototype.$snackbarAttach = function() {
    var div = document.createElement("div");
    this.$el.appendChild(div);
    component.$mount(div);
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
}
