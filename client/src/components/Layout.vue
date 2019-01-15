<script>
import { mapState } from "vuex";

import VtkViewer from "./VtkViewer.vue";

export default {
  name: "layout",
  components: {
    VtkViewer
  },
  computed: {
    ...mapState(["vtkViews"])
  }
};
</script>

<template>
  <div class="my-layout">
    <div class="view" v-for="(vtkView, index) in vtkViews" :key="Math.random(index)">
      <VtkViewer :view="vtkView"/>
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
  z-index: 0;

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
}
</style>
