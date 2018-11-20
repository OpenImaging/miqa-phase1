<script>
export default {
  name: "vtkViewer",
  components: {},
  props: {
    view: {
      required: true
    }
  },
  mounted() {
    // console.log(this.$refs.viewer);
    this.view.setContainer(this.$refs.viewer);
    this.resize();
  },
  methods: {
    resize() {
      this.view.resize();
    }
  }
};
</script>

<template>
<div ref="viewer" class="vtk-viewer">

</div>
</template>

<style lang="scss" scoped>
.vtk-viewer {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
}
</style>