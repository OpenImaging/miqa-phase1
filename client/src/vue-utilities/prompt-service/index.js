import Prompt from "./Prompt";

export default function(vuetify) {
  return function install(Vue) {
    Prompt.vuetify = vuetify;
    var PromptComponent = Vue.extend(Prompt);
    var component = new PromptComponent();
    Vue.prototype.$promptAttach = function() {
      var div = document.createElement("div");
      this.$el.appendChild(div);
      component.$mount(div);
      return this;
    };
    Vue.prototype.$prompt = function({
      title,
      text,
      positiveButton = "Confirm",
      negativeButton = "Cancel",
      confirm = false
    } = {}) {
      var resolve;
      var p = new Promise(_resolve => {
        resolve = _resolve;
      });
      function set() {
        component.$data.title = title;
        component.$data.text = text;
        component.$data.positiveButton = positiveButton;
        component.$data.negativeButton = negativeButton;
        component.$data.confirm = confirm;
        component.$data.resolve = resolve;
        component.$data.show = true;
      }
      if (!component.$data.show) {
        set();
      } else {
        var unwatch = component.$watch("show", () => {
          unwatch();
          set();
        });
      }
      return p;
    };
    Vue.prototype.$prompt.hide = function() {
      component.$data.show = false;
    };
  };
}
