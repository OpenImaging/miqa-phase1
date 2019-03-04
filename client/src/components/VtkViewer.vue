<script>
import _ from "lodash";
import Vue from "vue";
import { mapState, mapGetters, mapMutations } from "vuex";
import vtkWidgetManager from "vtk.js/Sources/Widgets/Core/WidgetManager";
import vtkImageCroppingWidget from "vtk.js/Sources/Widgets/Widgets3D/ImageCroppingWidget";

import fill2DView from "../utils/fill2DView";
import { cleanDatasetName } from "@/utils/helper";

export default {
  name: "vtkViewer",
  components: {},
  inject: ["girderRest"],
  props: {
    view: {
      required: true
    }
  },
  data: () => ({
    slice: null,
    // helper to avoid size flickering
    resized: false,
    fullscreen: false,
    annotation: {
      drawing: false,
      widget: null,
      widgetManager: null,
      renderWindow: null,
      selectedAnnotation: null
    }
  }),
  computed: {
    ...mapState(["proxyManager", "sliceCache"]),
    ...mapGetters(["currentSession", "currentDataset"]),
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
          return ["q", "w", "e"];
        case "x":
          return ["a", "s", "d"];
        case "y":
          return ["z", "x", "c"];
        default:
          return "";
      }
    },
    annotations() {
      if (
        !this.currentDataset ||
        !this.currentDataset.meta ||
        !this.currentDataset.meta.annotations
      ) {
        return [];
      }
      return this.currentDataset.meta.annotations;
    }
  },
  watch: {
    slice(value) {
      if (value !== this.representation.getSlice()) {
        this.representation.setSlice(value);
        this.saveSlice({ name: this.name, value });
      }
    },
    view(view, oldView) {
      this.cleanup();
      oldView.setContainer(null);
      this.initializeSlice();
      this.initializeView();
    },
    annotations(value) {
      if (
        this.annotation.selectedAnnotation &&
        value.indexOf(this.annotation.selectedAnnotation) === -1
      ) {
        this.annotation.selectedAnnotation = null;
        this.tryCleanAnnotation();
      }
    },
    "annotation.selectedAnnotation": {
      deep: true,
      handler(value) {
        if (this.annotation.widget) {
          this.setResizedPlanes(this.annotation.widget, value.planes);
          this.annotation.renderWindow.render();
        }
      }
    }
  },
  created() {
    this.initializeSlice();
  },
  mounted() {
    this.initializeView();
  },
  beforeDestroy() {
    this.cleanup();
  },
  methods: {
    ...mapMutations(["saveSlice", "setCurrentScreenshot"]),
    initializeSlice() {
      var cachedSlice = this.sliceCache[this.name];
      if (this.name !== "default") {
        this.slice = cachedSlice ? cachedSlice : this.representation.getSlice();
        this.modifiedSubscription = this.representation.onModified(() => {
          this.slice = this.representation.getSlice();
        });
      } else {
        this.representation.setXSliceVisibility(true);
        this.representation.setYSliceVisibility(true);
        this.representation.setZSliceVisibility(true);
        this.representation.setVolumeVisibility(false);
      }
    },
    initializeView() {
      this.view.setContainer(this.$refs.viewer);
      fill2DView(this.view);
      setTimeout(() => {
        this.resized = true;
      });
    },
    cleanup() {
      this.tryCleanAnnotation();
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
        name: `${this.currentSession.meta.experimentId}/${
          this.currentSession.meta.experimentId2
        }/${cleanDatasetName(this.currentDataset.name)}/${this.displayName}`,
        dataURL
      });
    },
    toggleFullscreen() {
      this.fullscreen = !this.fullscreen;
      this.resized = false;
      Vue.nextTick(() => {
        fill2DView(this.view);
        setTimeout(() => {
          this.resized = true;
        });
      });
    },
    onWindowResize() {
      if (this.resized) {
        fill2DView(this.view);
      }
    },
    createAnnotationWidget(callback) {
      this.tryCleanAnnotation();

      var widget = vtkImageCroppingWidget.newInstance();
      widget.copyImageDataDescription(
        this.proxyManager.getActiveSource().getDataset()
      );
      widget.setFaceHandlesEnabled(false);
      widget.setEdgeHandlesEnabled(false);
      widget.setCornerHandlesEnabled(false);

      var renderer = this.view.getRenderer();
      var renderWindow = this.view.getRenderWindow();

      var widgetManager;
      // Currently, WidgetManager can not be removed from view. So, keeping the same instance
      if (!this.annotation.widgetManager) {
        widgetManager = vtkWidgetManager.newInstance();
        widgetManager.setRenderer(renderer);
        this.annotation.widgetManager = widgetManager;
      } else {
        widgetManager = this.annotation.widgetManager;
      }

      widgetManager.addWidget(widget);
      callback({ widget, widgetManager, renderer, renderWindow });

      renderWindow.render();

      this.annotation.widget = widget;
      this.annotation.renderWindow = renderWindow;
    },
    addAnnotation() {
      this.annotation.drawing = true;
      this.createAnnotationWidget(({ widget, widgetManager }) => {
        this.setResizedPlanes(widget);
        widgetManager.enablePicking();
        widget.setCornerHandlesEnabled(true);
      });
    },
    selectAnnotationHelper(e, annotation) {
      if (
        [
          "v-list__tile__title",
          "v-list__tile__content",
          "v-list__tile"
        ].indexOf(e.target.className) !== -1
      ) {
        this.selectAnnotation(annotation);
      }
    },
    selectAnnotation(annotation) {
      if (this.annotation.selectedAnnotation !== annotation) {
        this.createAnnotationWidget(({ widget, widgetManager }) => {
          this.setResizedPlanes(widget, annotation.planes);

          widgetManager.disablePicking();
        });
        this.annotation.selectedAnnotation = annotation;
      } else {
        this.tryCleanAnnotation();
      }
    },
    editAnnotation(annotation) {
      this.annotation.drawing = true;
      if (this.annotation.selectedAnnotation !== annotation) {
        this.annotation.selectedAnnotation = annotation;
        this.createAnnotationWidget(({ widget, widgetManager }) => {
          this.setResizedPlanes(widget, annotation.planes);

          widgetManager.enablePicking();
          widget.setCornerHandlesEnabled(true);
        });
      } else {
        this.annotation.widget.setCornerHandlesEnabled(true);
        this.annotation.widgetManager.enablePicking();
        this.annotation.renderWindow.render();
      }
    },
    deleteAnnotation(annotation) {
      this.annotations.splice(this.annotations.indexOf(annotation), 1);
      this.$snackbar({
        text: "Annotation deleted",
        button: "Undo",
        timeout: 8000,
        callback: () => {
          this.annotations.push(annotation);
          this.saveAnnotation();
        }
      });
      this.saveAnnotation();
    },
    tryCleanAnnotation() {
      if (this.annotation.widget) {
        this.annotation.widgetManager.removeWidget(this.annotation.widget);
        this.annotation.widgetManager.disablePicking();
        this.annotation.widget = null;
        this.annotation.renderWindow.render();
        this.annotation.renderWindow = null;
        this.annotation.selectedAnnotation = null;
      }
    },
    setResizedPlanes(widget, planes) {
      var initialPlanes = widget
        .getWidgetState()
        .getCroppingPlanes()
        .getPlanes();
      var newPlanes = (() => {
        if (!planes) {
          switch (this.name) {
            case "z":
              return [
                initialPlanes[1] / 10,
                initialPlanes[1] - initialPlanes[1] / 10,
                initialPlanes[3] / 10,
                initialPlanes[3] - initialPlanes[3] / 10,
                initialPlanes[4],
                initialPlanes[5]
              ];
            case "x":
              return [
                initialPlanes[0],
                initialPlanes[1],
                initialPlanes[3] / 10,
                initialPlanes[3] - initialPlanes[3] / 10,
                initialPlanes[5] / 10,
                initialPlanes[5] - initialPlanes[5] / 10
              ];
            case "y":
              return [
                initialPlanes[1] / 10,
                initialPlanes[1] - initialPlanes[1] / 10,
                initialPlanes[3],
                initialPlanes[4],
                initialPlanes[5] / 10,
                initialPlanes[5] - initialPlanes[5] / 10
              ];
            default:
              return initialPlanes;
          }
        } else {
          switch (this.name) {
            case "z":
              return [
                planes[0],
                planes[1],
                planes[2],
                planes[3],
                initialPlanes[4],
                initialPlanes[5]
              ];
            case "x":
              return [
                initialPlanes[0],
                initialPlanes[1],
                planes[2],
                planes[3],
                planes[4],
                planes[5]
              ];
            case "y":
              return [
                planes[0],
                planes[1],
                initialPlanes[2],
                initialPlanes[3],
                planes[4],
                planes[5]
              ];
            default:
              return planes;
          }
        }
      })();
      widget
        .getWidgetState()
        .getCroppingPlanes()
        .setPlanes(newPlanes);
    },
    updateSelectedAnnotation() {
      var planes = this.annotation.widget
        .getWidgetState()
        .getCroppingPlanes()
        .getPlanes();
      var existingPlanes = this.annotation.selectedAnnotation.planes;
      switch (this.name) {
        case "z":
          this.annotation.selectedAnnotation.planes = [
            planes[0],
            planes[1],
            planes[2],
            planes[3],
            existingPlanes[4],
            existingPlanes[5]
          ];
          break;
        case "x":
          this.annotation.selectedAnnotation.planes = [
            existingPlanes[0],
            existingPlanes[1],
            planes[2],
            planes[3],
            planes[4],
            planes[5]
          ];
          break;
        case "y":
          this.annotation.selectedAnnotation.planes = [
            planes[0],
            planes[1],
            existingPlanes[2],
            existingPlanes[3],
            planes[4],
            planes[5]
          ];
          break;
        case "default":
          this.annotation.selectedAnnotation.planes = planes;
      }
    },
    confirmAnnotationEditing() {
      this.annotation.drawing = false;
      this.annotation.widget.setCornerHandlesEnabled(false);
      this.annotation.widgetManager.disablePicking();
      this.annotation.renderWindow.render();

      if (!this.annotation.selectedAnnotation) {
        if (!this.currentDataset.meta) {
          this.$set(this.currentDataset, "meta", {});
        }
        if (!this.currentDataset.meta.annotations) {
          this.$set(this.currentDataset.meta, "annotations", []);
        }
        var max = _.max(
          this.currentDataset.meta.annotations.map(
            annotation => annotation.index
          )
        );
        var annotation = {
          index: max ? max + 1 : 1,
          planes: this.annotation.widget
            .getWidgetState()
            .getCroppingPlanes()
            .getPlanes()
        };
        this.currentDataset.meta.annotations.push(annotation);
        this.annotation.selectedAnnotation = annotation;
      } else {
        this.updateSelectedAnnotation();
      }
      this.saveAnnotation();
    },
    cancelAnnotationEditing() {
      this.annotation.drawing = false;
      this.tryCleanAnnotation();
    },
    async saveAnnotation() {
      await this.girderRest.put(
        `item/${this.currentDataset._id}/metadata?allowNull=true`,
        this.currentDataset.meta
      );
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
  <div class="vtk-viewer" :class="{ fullscreen }" v-resize="onWindowResize">
    <div class="header" :class="name" v-if="name !== 'default'">
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
    <div
      ref="viewer"
      class="viewer"
      :style="{ visibility: resized ? 'unset' : 'hidden' }"
    ></div>
    <v-toolbar class="toolbar" dark flat color="black" height="42">
      <div class="indicator body-2" :class="name">{{ displayName }}</div>
      <v-spacer></v-spacer>
      <v-menu offset-y top min-width="150">
        <template #activator="{ on }">
          <v-btn v-on="on" flat icon>
            <v-icon>crop</v-icon>
          </v-btn>
        </template>
        <v-list dense class="annotation-menu">
          <template v-if="!annotation.drawing">
            <v-hover
              #default="{hover}"
              v-for="annotationData of annotations"
              :key="annotationData.index"
            >
              <v-list-tile
                :class="{
                  'primary--text':
                    annotationData === annotation.selectedAnnotation
                }"
                @click="selectAnnotationHelper($event, annotationData)"
              >
                <v-list-tile-content>
                  <v-list-tile-title>{{
                    annotationData.index
                  }}</v-list-tile-title>
                </v-list-tile-content>
                <v-fade-transition>
                  <v-list-tile-action v-if="hover">
                    <v-btn icon @click.prevent="editAnnotation(annotationData)">
                      <v-icon color="grey">edit</v-icon>
                    </v-btn>
                  </v-list-tile-action>
                </v-fade-transition>
                <v-fade-transition>
                  <v-list-tile-action v-if="hover">
                    <v-btn
                      icon
                      @click.prevent="deleteAnnotation(annotationData)"
                    >
                      <v-icon color="grey">delete</v-icon>
                    </v-btn>
                  </v-list-tile-action>
                </v-fade-transition>
              </v-list-tile>
            </v-hover>
            <v-divider v-if="annotations.length" />
            <v-list-tile @click="addAnnotation">
              <v-list-tile-title>Add</v-list-tile-title>
            </v-list-tile>
          </template>
          <template v-else>
            <v-list-tile @click="confirmAnnotationEditing">
              <v-list-tile-title>Confirm</v-list-tile-title>
            </v-list-tile>
            <v-list-tile @click="cancelAnnotationEditing">
              <v-list-tile-title>Cancel</v-list-tile-title>
            </v-list-tile>
          </template>
        </v-list>
      </v-menu>
      <v-btn
        icon
        @click="toggleFullscreen"
        v-mousetrap="{ bind: keyboardBindings[2], handler: toggleFullscreen }"
      >
        <v-icon v-if="!fullscreen">fullscreen</v-icon>
        <v-icon v-else>fullscreen_exit</v-icon>
      </v-btn>
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
  background: linear-gradient(#3a3a3a, #1d1d1d);
  z-index: 0;

  display: flex;
  flex-direction: column;

  &.fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    z-index: 2;
  }

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
    overflow-y: hidden;
  }
}

.annotation-menu {
  .v-list__tile__action {
    min-width: 35px;
  }
}
</style>

<style lang="scss">
.vtk-viewer {
  .slice-slider .v-slider {
    height: 23px;
  }
}
</style>
