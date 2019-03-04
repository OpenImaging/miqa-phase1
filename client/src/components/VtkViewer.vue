<script>
import { mapState, mapGetters, mapMutations } from "vuex";

import fill2DView from "../utils/fill2DView";
import { cleanDatasetName } from "@/utils/helper";

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
    ...mapState(["proxyManager"]),
    ...mapGetters(["currentDataset"]),
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
        default:
          return "";
      }
    },
    keyboardBindings() {
      switch (this.name) {
        case "z":
          return ["q", "w"];
        case "x":
          return ["a", "s"];
        case "y":
          return ["z", "x"];
        default:
          return "";
      }
    }
  },
  watch: {
    slice(value) {
      this.representation.setSlice(value);
    },
    view(view, oldView) {
      this.cleanup();
      oldView.setContainer(null);
      this.initialize();
    }
  },
  beforeDestroy() {
    this.cleanup();
  },
  mounted() {
    this.initialize();
  },
  methods: {
    ...mapMutations(["setCurrentScreenshot"]),
    initialize() {
      this.view.setContainer(this.$refs.viewer);
      this.view.resize();
      fill2DView(this.view);
      if (this.name !== "default") {
        this.slice = this.representation.getSlice();
        this.modifiedSubscription = this.representation.onModified(() => {
          this.slice = this.representation.getSlice();
        });
      }
    },
    cleanup() {
      if (this.modifiedSubscription) {
        this.modifiedSubscription.unsubscribe();
      }
    },
    increaseSlice() {
      var slice = Math.min(
        (this.slice += this.sliceDomain.step),
        this.sliceDomain.max
      );
      this.slice = slice;
    },
    decreaseSlice() {
      var slice = Math.max(
        (this.slice -= this.sliceDomain.step),
        this.sliceDomain.min
      );
      this.slice = slice;
    },
    async takeScreenshot() {
      var dataURL = await this.view.captureImage();
      this.setCurrentScreenshot({
        name:
          cleanDatasetName(this.currentDataset.name) + " " + this.displayName,
        dataURL
      });
    }
  },
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
    <div class="header"
      :class="name"
      v-if="name !== 'default'">
      <v-layout align-center>
        <v-slider
          class="slice-slider mt-0 mx-4"
          hide-details
          :min="sliceDomain.min"
          :max="sliceDomain.max"
          :step="sliceDomain.step"
          v-model="slice"
          v-mousetrap="[
            { bind: keyboardBindings[1], handler: increaseSlice },
            { bind: keyboardBindings[0], handler: decreaseSlice }
          ]"
        ></v-slider>
        <div class="slice caption px-2">{{ slice | roundSlice }} mm</div>
      </v-layout>
    </div>
    <div ref="viewer" class="viewer"></div>
    <v-toolbar class="toolbar elevation-0" dark color="black" dense>
      <div class="indicator body-2" :class="name">{{ displayName }}</div>
      <v-spacer></v-spacer>
      <v-btn icon @click="takeScreenshot">
        <v-icon>add_a_photo</v-icon>
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
      width: 85px;
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
    flex: 1 1 0px;
    position: relative;
    background: linear-gradient(#3a3a3a, #1d1d1d);
    overflow-y: hidden;
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
