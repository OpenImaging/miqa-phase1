import Mousetrap from "mousetrap";
import _ from "lodash";

function bind(el, value, bindElement) {
  var mousetrap = new Mousetrap(bindElement ? el : undefined);
  el.mousetrap = mousetrap;
  if (!_.isArray(value)) {
    value = [value];
  }
  value.forEach(({ bind, handler, disabled }) => {
    const handlerType = typeof handler;
    if (!disabled) {
      if (handlerType === "function") {
        mousetrap.bind(bind, function() {
          handler.apply(this, [el, ...arguments]);
        });
      } else if (handlerType === "object") {
        Object.keys(handler).forEach(eventType => {
          const eventHandler = handler[eventType];
          mousetrap.bind(
            bind,
            function() {
              eventHandler.apply(this, [el, ...arguments]);
            },
            eventType
          );
        });
      }
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
