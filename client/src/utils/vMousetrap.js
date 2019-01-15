import Mousetrap from "mousetrap";
import _ from "lodash";

function bind(el, value, bindElement) {
  var mousetrap = new Mousetrap(bindElement ? el : undefined);
  el.mousetrap = mousetrap;
  if (!_.isArray(value)) {
    value = [value];
  }
  value.forEach(({ bind, handler, disabled }) => {
    if (!disabled) {
      mousetrap.bind(bind, function() {
        handler.apply(this, [el, ...arguments]);
      });
    }
  });
}

function unbind(el) {
  el.mousetrap.reset();
}

export default function install(Vue) {
  Vue.directive("mousetrap", {
    inserted(el, { value, modifiers }) {
      bind(el, value, modifiers.element);
    },
    update(el, { value, modifiers }) {
      unbind(el);
      bind(el, value, modifiers.element);
    },
    unbind(el) {
      unbind(el);
    }
  });
}
