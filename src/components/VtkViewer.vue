<script>
import { mapState, mapGetters } from "vuex";

export default {
  name: "vtkViewer",
  components: {},
  props: {
    view: {
      required: true
    }
  },
  data() {
    return {
      slice: null
    };
  },
  computed: {
    representation() {
      return this.proxyManager.getRepresentation(null, this.view);
    },
    sliceDomain() {
      return this.representation.getPropertyDomainByName("slice");
    },
    ...mapState(["proxyManager"])
  },
  watch: {
    slice(value) {
      this.representation.setSlice(value);
    }
  },
  created() {
    console.log(this.view);
    this.slice = this.representation.getSlice();
  },
  mounted() {
    this.view.setContainer(this.$refs.viewer);
    this.view.resize();
  },
  methods: {}
};
</script>

<template>
  <div class="vtk-viewer">
    <div class="header" :class="view.getName()">
      <v-slider
        class="mt-0 mx-4"
        hide-details
        v-model="slice"
        :min="sliceDomain.min"
        :max="sliceDomain.max"
        :step="sliceDomain.step"
      ></v-slider>
    </div>
    <div ref="viewer" class="viewer"></div>
  </div>
</template>

<style lang="scss" scoped>
.vtk-viewer {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;

  display: flex;
  flex-direction: column;

  .header {
    &.z {
      background-color: #e97363;
    }

    &.x {
      background-color: #f5e58d;
    }

    &.y {
      background-color: #91b87c;
    }
  }

  .viewer {
    flex: 1 0 auto;
    position: relative;
    background: linear-gradient(rgb(51, 51, 51), rgb(153, 153, 153));
  }
}
</style>