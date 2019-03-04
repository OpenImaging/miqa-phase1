<script>
import { mapState } from "vuex";

import VtkViewer from "./VtkViewer.vue";

export default {
  name: "layout",
  components: {
    VtkViewer
  },
  data: () => ({
    show3D: false
  }),
  computed: {
    ...mapState(["vtkViews"]),
    filteredViews() {
      if (this.show3D) {
        return this.vtkViews;
      } else {
        return this.vtkViews.slice(0, -1);
      }
    }
  },
  watch: {
    show3D() {
      // TODO: better mechanism
      setTimeout(() => {
        this.vtkViews.forEach(vtkView => {
          vtkView.resize();
        });
      });
    }
  }
};
</script>

<template>
  <div class="my-layout">
    <div class="view" v-for="(vtkView, index) in filteredViews" :key="index">
      <VtkViewer :view="vtkView" />
    </div>
    <div class="drawer-handle" @click="show3D = !show3D">
      <v-icon>{{ show3D ? "arrow_right" : "arrow_left" }}</v-icon>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.my-layout {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;

  .view {
    position: relative;
    flex: 1 0 0px;

    border: 1.5px solid white;
    border-top: none;
    border-bottom: none;

    &:first-child {
      border-left: none;
    }

    &:last-child {
      border-right: none;
    }
  }

  .drawer-handle {
    flex: 1 0 0px;
    max-width: 10px;
    display: flex;
    cursor: default;

    &:hover {
      background: #ccc;
    }

    .v-icon {
      position: relative;
      left: -8px;
    }
  }
}
</style>
