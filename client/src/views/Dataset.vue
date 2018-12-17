<script>
import Layout from "@/components/Layout.vue";
import { mapState, mapActions, mapGetters, mapMutations } from "vuex";

import SessionsView from "@/components/SessionsView";

export default {
  name: "dataset",
  components: {
    Layout,
    SessionsView
  },
  computed: {
    ...mapState(["loadingDataset", "drawer", "currentDataset"]),
    ...mapGetters(["nextDataset", "previousDataset", "currentSesssionDatasets"])
  },
  methods: {
    ...mapMutations(["setDrawer"]),
    ...mapActions(["swapToDataset"])
  }
};
</script>

<template>
  <div class="dataset">
    <v-navigation-drawer app :value="drawer" @input="setDrawer($event)" fixed temporary>
      <SessionsView />
    </v-navigation-drawer>
    <template v-if="currentDataset">
      <div class="layout-container">
        <Layout v-if="!loadingDataset" />
        <v-layout v-else align-center justify-center row fill-height>
          <v-flex xs3>
            <v-progress-linear :indeterminate="true"></v-progress-linear>
          </v-flex>
        </v-layout>
      </div>
      <div class="bottom">
        <v-container fluid grid-list-md>
          <v-layout>
            <v-flex xs6>
              <v-container fluid grid-list-md>
                <v-layout>
                  <v-flex>
                    <div class="subheading">Window setup</div>
                  </v-flex>
                </v-layout>
                <v-layout>
                  <v-flex>
                    <v-slider
                      label="Window"
                      :max="255"
                      :min="0"
                      :step="1"
                      :value="128"
                      hide-details
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
                      :value="255"
                    ></v-text-field>
                  </v-flex>
                </v-layout>
                <v-layout>
                  <v-flex>
                    <v-slider
                      label="Level"
                      :max="255"
                      :min="0"
                      :step="1"
                      :value="150"
                      hide-details
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
                      :value="128"
                    ></v-text-field>
                  </v-flex>
                </v-layout>
              </v-container>
            </v-flex>
            <v-flex xs6>
              <v-container fluid grid-list-sm>
                <v-layout>
                  <v-flex>
                    <v-textarea solo label="Add note" rows="4" hide-details></v-textarea>
                  </v-flex>
                </v-layout>
                <v-layout>
                  <v-flex xs5>
                    <v-text-field
                      class="small"
                      label="Reviewer name"
                      solo
                      hide-details></v-text-field>
                  </v-flex>
                  <v-flex xs7>
                    <v-btn-toggle mandatory class="buttons">
                      <v-btn flat value="good">Good</v-btn>
                      <v-btn flat value="bad">Bad</v-btn>
                      <v-btn flat value="unsure">Unsure</v-btn>
                    </v-btn-toggle>
                  </v-flex>
                </v-layout>
                <v-layout align-center justify-space-between>
                  <v-btn
                    color="primary">
                    Save
                    <v-icon right>save</v-icon>
                  </v-btn>
                  <v-spacer />
                  <v-menu offset-y>
                    <v-btn
                      slot="activator"
                      flat
                      icon
                      color="primary">
                      <v-icon>more_vert</v-icon>
                    </v-btn>
                    <v-list>
                      <v-list-tile
                        v-for="(dataset, index) in currentSesssionDatasets"
                        :key="index"
                        @click="swapToDataset(dataset)"
                        :class="{'primary--text':dataset===currentDataset}">
                        <v-list-tile-title>{{dataset.name}}</v-list-tile-title>
                      </v-list-tile>
                    </v-list>
                  </v-menu>
                  <v-btn fab small
                    class="primary--text elevation-2"
                    :disabled="!previousDataset"
                    @click="swapToDataset(previousDataset)"
                    >
                    <v-icon>keyboard_arrow_left</v-icon>
                  </v-btn>
                  <v-btn fab small
                    class="primary--text elevation-2"
                    :disabled="!nextDataset"
                    @click="swapToDataset(nextDataset)">
                    <v-icon>keyboard_arrow_right</v-icon>
                  </v-btn>
                </v-layout>
              </v-container>
            </v-flex>
          </v-layout>
        </v-container>
      </div>
    </template>
    <template v-else>
      <v-layout align-center justify-center row fill-height >
        <div class="title">Select a dataset</div>
      </v-layout>
    </template>
  </div>
</template>

<style lang="scss" scoped>
.dataset {
  display: flex;
  flex-direction: column;
  height: 100%;

  .layout-container {
    flex: 1 1 0%;
    position: relative;
  }

  .bottom {
    > .container {
      position: relative;

      &::before {
        content: " ";
        position: absolute;
        top: 1px;
        bottom: 0;
        left: 0;
        right: 50%;
        background: white;
      }
    }

    .buttons {
      width: 100%;
      height: 40px;

      .v-btn {
        height: 100%;
        width: 33.333%;
      }
    }
  }
}
</style>

<style lang="scss">
.v-text-field.small .v-input__control {
  min-height: 40px !important;
}
</style>
