<script>
import { mapState, mapGetters } from "vuex";

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
  <div class="layout">
    <div class="view" v-for="(vtkView, index) in vtkViews" :key="index">
      <VtkViewer :view="vtkView"/>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.layout {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;

  .view {
    position: relative;
    flex: 1 0 0px;
  }
}
</style>