<script>
import { mapState, mapGetters } from "vuex";

import VtkViewer from "./VtkViewer.vue";

export default {
  name: "layout",
  components: {
    VtkViewer
  },
  computed: {
    ...mapGetters(["vtkViews"])
  }
};
</script>

<template>
  <div class="layout">
    <VtkViewer
        v-for="(vtkView, index) in vtkViews"
        :key="index"
        :view="vtkView"/>
  </div>
</template>

<style scoped>
.layout {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
}
</style>