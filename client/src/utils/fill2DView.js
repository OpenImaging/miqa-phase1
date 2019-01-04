
export default function fill2DView(view) {
  const viewName = view.getName();
  if (viewName === "default") return;

  const bounds = view.getRenderer().computeVisiblePropBounds();
  const dim = [
    (bounds[1] - bounds[0]) / 2,
    (bounds[3] - bounds[2]) / 2,
    (bounds[5] - bounds[4]) / 2
  ];
  const w = view.getContainer().clientWidth;
  const h = view.getContainer().clientHeight;
  const r = w / h;

  let x;
  let y;
  if (viewName === "x") {
    x = dim[1];
    y = dim[2];
  } else if (viewName === "y") {
    x = dim[0];
    y = dim[2];
  } else if (viewName === "z") {
    x = dim[0];
    y = dim[1];
  }
  if (r >= x / y) {
    // use width
    view.getCamera().setParallelScale(y + 1);
  } else {
    // use height
    view.getCamera().setParallelScale(x / r + 1);
  }
  view.resize();
}
