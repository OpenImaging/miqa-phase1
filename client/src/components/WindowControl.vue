<script>
import { mapState, mapGetters } from "vuex";

export default {
  name: "WindowControl",
  data: () => ({
    active: {
      width: 100,
      widthDomain: {
        min: 0,
        max: 100,
        step: 1
      },
      level: 0,
      levelDomain: {
        min: -50,
        max: 50,
        step: 1
      }
    },
    default: {
      width: 100,
      widthDomain: {
        min: 0,
        max: 100,
        step: 1
      },
      level: 0,
      levelDomain: {
        min: -50,
        max: 50,
        step: 1
      }
    }
  }),
  computed: {
    ...mapState(["proxyManager", "loadingDataset"]),
    ...mapGetters(["currentDataset"]),
    representation() {
      return this.currentDataset && this.proxyManager.getRepresentations()[0];
    },
    windowWidthDomain() {
      return this.representation.getPropertyDomainByName("windowWidth");
    },
    windowLevelDomain() {
      return this.representation.getPropertyDomainByName("windowLevel");
    },
    validatedMinWidth: {
      get: function() {
        return this.active.widthDomain.min;
      },
      set: function(val) {
        if (val < 0) {
          this.active.widthDomain.min = 0;
        } else {
          this.active.widthDomain.min = val;
        }
      }
    },
    userDefinedValues: {
      get: function() {
        // return (
        //   this.active.width !== this.default.width ||
        //   this.active.widthDomain.min !== this.default.widthDomain.min ||
        //   this.active.widthDomain.max !== this.default.widthDomain.max ||
        //   this.active.widthDomain.step !== this.default.widthDomain.step ||
        //   this.active.level !== this.default.level ||
        //   this.active.levelDomain.min !== this.default.levelDomain.min ||
        //   this.active.levelDomain.max !== this.default.levelDomain.max ||
        //   this.active.levelDomain.step !== this.default.levelDomain.step
        // );
        if (this.active.width !== this.default.width) {
          console.log(`width mismatch: ${this.active.width} - ${this.default.width}`);
          return true;
        } else if (this.active.widthDomain.min !== this.default.widthDomain.min) {
          console.log(`width domain min mismatch: ${this.active.widthDomain.min} - ${this.default.widthDomain.min}`);
          return true;
        } else if (this.active.widthDomain.max !== this.default.widthDomain.max) {
          console.log(`width domain max mismatch: ${this.active.widthDomain.max} - ${this.default.widthDomain.max}`);
          return true;
        } else if (this.active.widthDomain.step !== this.default.widthDomain.step) {
          console.log(`width domain step mismatch: ${this.active.widthDomain.step} - ${this.default.widthDomain.step}`);
          return true;
        } else if (this.active.level !== this.default.level) {
          console.log(`level mismatch: ${this.active.level} - ${this.default.level}`);
          return true;
        } else if (this.active.levelDomain.min !== this.default.levelDomain.min) {
          console.log(`level domain min mismatch: ${this.active.levelDomain.min} - ${this.default.levelDomain.min}`);
          return true;
        } else if (this.active.levelDomain.max !== this.default.levelDomain.max) {
          console.log(`level domain max mismatch: ${this.active.levelDomain.max} - ${this.default.levelDomain.max}`);
          return true;
        } else if (this.active.levelDomain.step !== this.default.levelDomain.step) {
          console.log(`level domain step mismatch: ${this.active.levelDomain.step} - ${this.default.levelDomain.step}`);
          return true;
        }
        return false;
      },
      set: function (newValue) {
        if (!newValue) {
          this.active.width = this.default.width;
          this.active.widthDomain.min = this.default.widthDomain.min;
          this.active.widthDomain.max = this.default.widthDomain.max;
          this.active.widthDomain.step = this.default.widthDomain.step;
          this.active.level = this.default.level;
          this.active.levelDomain.min = this.default.levelDomain.min;
          this.active.levelDomain.max = this.default.levelDomain.max;
          this.active.levelDomain.step = this.default.levelDomain.step;
        }
      }
    },
  },
  watch: {
    currentDataset() {
      const userDefs = this.userDefinedValues;
      console.log(`currentDataset changed, user is ${userDefs ? 'IN' : 'NOT IN'} control`);
      this.updateDefaults();
      if (!userDefs) {
        console.log('setting active values to match defaults of new dataset');
        this.updateActive();
      }
      console.log('taking component width/level and setting them on the repr');
      this.representation.setWindowWidth(this.active.width);
      this.representation.setWindowLevel(this.active.level);
    },
    'active.width': function (value) {
      console.log(`Watcher: active width = ${value}`);
      if (value !== this.representation.getWindowWidth()) {
        this.representation.setWindowWidth(value);
      }
    },
    'active.level': function (value) {
      console.log(`Watcher: active level = ${value}`);
      if (value !== this.representation.getWindowLevel()) {
        this.representation.setWindowLevel(value);
      }
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
    updateDefaults() {
      console.log('Updating default values');
      const widthDomain = this.representation.getPropertyDomainByName("windowWidth");
      const levelDomain = this.representation.getPropertyDomainByName("windowLevel");

      this.default.widthDomain.min = widthDomain.min;
      this.default.widthDomain.max = widthDomain.max;
      this.default.widthDomain.step = widthDomain.step;
      this.default.levelDomain.min = levelDomain.min;
      this.default.levelDomain.max = levelDomain.max;
      this.default.levelDomain.step = levelDomain.step;

      this.default.level = this.representation.getWindowLevel();
      this.default.width = this.representation.getWindowWidth();
    },
    updateActive() {
      console.log('Updating active values');
      this.active.widthDomain.min = this.default.widthDomain.min;
      this.active.widthDomain.max = this.default.widthDomain.max;
      this.active.widthDomain.step = this.default.widthDomain.step;
      this.active.levelDomain.min = this.default.levelDomain.min;
      this.active.levelDomain.max = this.default.levelDomain.max;
      this.active.levelDomain.step = this.default.levelDomain.step;

      this.active.width = this.default.width;
      this.active.level = this.default.level;
    },
    bindWindow() {
      console.log("WindowControl bindWindow: subscribe representation 'modified'");
      this.updateDefaults();
      this.updateActive();
      this.modifiedSubscription = this.representation.onModified(() => {
        if (!this.loadingDataset && !this.userDefinedValues) {
          console.log('repr modified, UPDATE');
          this.updateActive();
        } else {
          console.log(`repr modified, IGNORE (loading = ${
            this.loadingDataset
          }, userDefined = ${this.userDefinedValues})`);
        }
      });
    },
    increaseWindowWidth() {
      var windowWidth = Math.min(
        (this.active.width +=
          (this.active.widthDomain.max - this.active.widthDomain.min) / 30),
        this.active.widthDomain.max
      );
      this.active.width = windowWidth;
    },
    decreaseWindowWidth() {
      var windowWidth = Math.max(
        (this.active.width -=
          (this.active.widthDomain.max - this.active.widthDomain.min) / 30),
        this.active.widthDomain.min
      );
      this.windowWidth = windowWidth;
    },
    increaseWindowLevel() {
      var windowLevel = Math.min(
        (this.active.level +=
          (this.active.levelDomain.max - this.active.levelDomain.min) / 30),
        this.active.levelDomain.max
      );
      this.active.level = windowLevel;
    },
    decreaseWindowLevel() {
      var windowLevel = Math.max(
        (this.active.level -=
          (this.active.levelDomain.max - this.active.levelDomain.min) / 30),
        this.active.levelDomain.min
      );
      this.active.level = windowLevel;
    },
    validateWindowWidth(val) {
      console.log(`blur: ${val}`);
    }
  }
};
</script>

<template>
  <div class="component">
    <v-container>
      <v-row align="center" class="headerRow">
        <v-col class="pb-1 pt-0">
          <div class="componentLabel">Window Controls</div>
        </v-col>
        <v-col class="pb-1 pt-0">
          <div>
            <v-switch
              v-model="userDefinedValues"
              label="User Defined Values"
            ></v-switch>
          </div>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="3" align-self="center" class="pb-1 pt-0">
          <div>Width</div>
        </v-col>
        <v-col cols="9" class="pb-1 pt-0">
          <v-text-field
            class="mt-0"
            hide-details
            single-line
            solo
            dense
            type="number"
            v-model="active.width"
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="3" class="pb-1 pt-0">
          <v-text-field
            class="mt-0"
            hide-details
            single-line
            solo
            dense
            type="number"
            v-model="validatedMinWidth"
          ></v-text-field>
        </v-col>
        <v-col align-self="end" cols="6" class="pb-1 pt-0">
          <v-slider
            hide-details
            thumb-label
            :thumb-size="48"
            :min="active.widthDomain.min"
            :max="active.widthDomain.max"
            :step="active.widthDomain.step"
            v-model="active.width"
            v-mousetrap="[
              { bind: ']', handler: increaseWindowWidth },
              { bind: '[', handler: decreaseWindowWidth }
            ]"
          ></v-slider>
        </v-col>
        <v-col cols="3" class="pb-1 pt-0">
          <v-text-field
            class="mt-0"
            hide-details
            single-line
            solo
            dense
            type="number"
            v-model="active.widthDomain.max"
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="3" align-self="center" class="pb-1 pt-0">
          <div>Level</div>
        </v-col>
        <v-col cols="9" class="pb-1 pt-0">
          <v-text-field
            class="mt-0"
            hide-details
            single-line
            solo
            dense
            type="number"
            v-model="active.level"
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="3" class="pb-1 pt-0">
          <v-text-field
            class="mt-0"
            hide-details
            single-line
            solo
            dense
            type="number"
            v-model="active.levelDomain.min"
          ></v-text-field>
        </v-col>
        <v-col align-self="end" cols="6" class="pb-1 pt-0">
          <v-slider
            hide-details
            thumb-label
            :thumb-size="48"
            :min="active.levelDomain.min"
            :max="active.levelDomain.max"
            :step="active.levelDomain.step"
            v-model="active.level"
            v-mousetrap="[
              { bind: ']', handler: increaseWindowLevel },
              { bind: '[', handler: decreaseWindowLevel }
            ]"
          ></v-slider>
        </v-col>
        <v-col cols="3" class="pb-1 pt-0">
          <v-text-field
            class="mt-0"
            hide-details
            single-line
            solo
            dense
            type="number"
            v-model="active.levelDomain.max"
          ></v-text-field>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<style lang="scss">
.noTopPad {
  padding-top: 3px;
  padding-bottom: 3px;
}

.componentLabel {
  font-weight: bold;
  text-align: left;
}

.headerRow {
  max-height: 60px;
}
</style>
