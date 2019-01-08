<script>
import { mapState } from "vuex";

export default {
  name: "WindowControl",
  data: () => ({
    windowWidth: 0,
    windowLevel: 0
  }),
  computed: {
    ...mapState(["proxyManager"]),
    representation() {
      return this.proxyManager.getRepresentations()[0];
    },
    windowWidthDomain() {
      return this.representation.getPropertyDomainByName("windowWidth");
    },
    windowLevelDomain() {
      return this.representation.getPropertyDomainByName("windowLevel");
    }
  },
  watch: {
    windowWidth(value) {
      this.representation.setWindowWidth(value);
    },
    windowLevel(value) {
      this.representation.setWindowLevel(value);
    },
    proxyManager() {
      this.modifiedSubscription.unsubscribe();
      this.bindWindow();
    }
  },
  created() {
    this.bindWindow();
  },
  beforeDestroy() {
    this.modifiedSubscription.unsubscribe();
  },
  methods: {
    bindWindow() {
      this.windowWidth = this.representation.getWindowWidth();
      this.windowLevel = this.representation.getWindowLevel();
      this.modifiedSubscription = this.representation.onModified(() => {
        this.windowWidth = this.representation.getWindowWidth();
        this.windowLevel = this.representation.getWindowLevel();
      });
    }
  }
};
</script>

<template>
  <v-container fluid grid-list-md>
    <v-layout>
      <v-flex>
        <div class="subheading">Window setup</div>
      </v-flex>
    </v-layout>
    <v-layout>
      <v-flex>
        <v-slider
          class="mr-4"
          hide-details
          label="Window"
          :min="windowWidthDomain.min"
          :max="windowWidthDomain.max"
          :step="windowWidthDomain.step"
          v-model="windowWidth"
        ></v-slider>
      </v-flex>
      <v-flex
        shrink
        style="width: 60px">
        <v-text-field
          class="mt-0"
          hide-details
          single-line
          type="number"
          v-model="windowWidth"
        ></v-text-field>
      </v-flex>
    </v-layout>
    <v-layout>
      <v-flex>
        <v-slider
          class="mr-4"
          hide-details
          label="Level"
          :min="windowLevelDomain.min"
          :max="windowLevelDomain.max"
          :step="windowLevelDomain.step"
          v-model="windowLevel"
        ></v-slider>
      </v-flex>
      <v-flex
        shrink
        style="width: 60px">
        <v-text-field
          class="mt-0"
          hide-details
          single-line
          type="number"
          v-model="windowLevel"
        ></v-text-field>
      </v-flex>
    </v-layout>
  </v-container>
</template>
