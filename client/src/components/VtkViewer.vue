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
    name() {
      return this.view.getName();
    },
    displayName() {
      switch (this.name) {
        case "x":
          return "Coronal";
        case "y":
          return "Sagittal";
        case "z":
          return "Axial";
      }
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
  methods: {},
  filters: {
    roundSlice: function(value) {
      if (!value) return "";
      return Math.round(value * 100) / 100;
    }
  }
};
</script>

<template>
  <div class="vtk-viewer">
    <div class="header" :class="name">
      <v-layout align-center>
      <v-slider
        class="slice-slider mt-0 mx-4"
        hide-details
        v-model="slice"
        :min="sliceDomain.min"
        :max="sliceDomain.max"
        :step="sliceDomain.step"
      ></v-slider>
      <div class="slice caption px-2">S: {{slice | roundSlice}} mm</div>
      </v-layout>
    </div>
    <div ref="viewer" class="viewer"></div>
    <v-toolbar class="toolbar" dark color="black" dense>
      <div class="indicator body-2" :class="name">{{displayName}}</div>
      <v-spacer></v-spacer>
      <v-btn icon>
        <v-icon>photo_camera</v-icon>
      </v-btn>
    </v-toolbar>
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
    .slice {
      height: 23px;
      line-height: 23px;
      color: white;
    }

    &.z {
      background-color: #ef5350;

      .slice {
        background-color: #b71c1c;
      }
    }

    &.x {
      background-color: #fdd835;

      .slice {
        background-color: #f9a825;
      }
    }

    &.y {
      background-color: #4caf50;

      .slice {
        background-color: #1b5e20;
      }
    }

    .slice {
    }
  }

  .toolbar {
    .indicator {
      &::before {
        content: " ";
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 6px;
        margin-right: 10px;
        position: relative;
        top: 1px;
      }

      &.z::before {
        background: #ef5350;
      }

      &.x::before {
        background: #fdd835;
      }

      &.y::before {
        background: #4caf50;
      }
    }
  }

  .viewer {
    flex: 1 0 auto;
    position: relative;
    background: linear-gradient(rgb(51, 51, 51), rgb(153, 153, 153));
  }
}
</style>

<style lang="scss">
.vtk-viewer {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;

  display: flex;
  flex-direction: column;

  .slice-slider .v-slider {
    height: 23px;
  }
}
</style>
