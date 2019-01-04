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
  inject: ["girderRest"],
  data: () => ({
    note: "",
    rating: null,
    reviewer: "",
    reviewChanged: false,
    unsavedDialog: false,
    unsavedDialogResolve: null
  }),
  computed: {
    ...mapState(["loadingDataset", "drawer"]),
    ...mapGetters([
      "nextDataset",
      "currentDataset",
      "getDataset",
      "currentSession",
      "previousDataset"
    ])
  },
  async created() {
    await this.loadSessions();
    if (this.$route.params.datasetId) {
      try {
        await this.swapToDataset(this.$route.params.datasetId);
      } catch (ex) {
        this.$router.replace("/");
      }
    }
  },
  watch: {
    async currentSession(session, oldSession) {
      if (session === oldSession) {
        return;
      }
      let { data: folder } = await this.girderRest.get(
        `folder/${session.folderId}`
      );
      this.note = "";
      this.rating = null;
      this.reviewer = "";
      this.reviewChanged = false;
      if (folder.meta) {
        if (folder.meta.note) {
          this.note = folder.meta.note;
        }
        if (folder.meta.rating) {
          this.rating = folder.meta.rating;
        }
        if (folder.meta.reviewer) {
          this.reviewer = folder.meta.reviewer;
        }
      }
    }
  },
  async beforeRouteUpdate(to, from, next) {
    let toDataset = this.getDataset(to.params.datasetId);
    let result = await this.beforeLeaveSession(toDataset);
    next(result);
    if (result) {
      this.swapToDataset(to.params.datasetId);
    }
  },
  // beforeRouteLeave(to, from, next) {
  //   next();
  // },
  methods: {
    ...mapMutations(["setDrawer"]),
    ...mapActions(["loadSessions", "swapToDataset"]),
    async beforeLeaveSession(toDataset) {
      let currentDataset = this.currentDataset;
      if (
        currentDataset &&
        (!toDataset || toDataset.folderId !== this.currentDataset.folderId) &&
        this.reviewChanged
      ) {
        this.unsavedDialog = true;
        return await new Promise((resolve, reject) => {
          this.unsavedDialogResolve = resolve;
        });
      }
      return Promise.resolve(true);
    },
    async save() {
      let user = this.girderRest.user;
      let reviewer = user.firstName + " " + user.lastName;
      await this.girderRest.put(
        `folder/${this.currentSession.folderId}/metadata`,
        {
          note: this.note,
          rating: this.rating,
          reviewer
        }
      );
      this.reviewer = reviewer;
      this.reviewChanged = false;
    },
    async unsavedDialogYes() {
      await this.save();
      this.unsavedDialogResolve(true);
      this.unsavedDialog = false;
    },
    unsavedDialogNo() {
      this.unsavedDialogResolve(true);
      this.unsavedDialog = false;
    },
    unsavedDialogCancel() {
      this.unsavedDialogResolve(false);
      this.unsavedDialog = false;
    }
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
        <Layout/>
        <v-layout v-if="loadingDataset"
          class="loading-indicator-container"
          align-center justify-center row fill-height>
          <v-progress-circular
            color="primary"
            :width="4"
            :size="50"
            indeterminate
          ></v-progress-circular>
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
                    <v-textarea solo label="Note" rows="4" hide-details
                      v-model="note" @input="reviewChanged=true"></v-textarea>
                  </v-flex>
                </v-layout>
                <v-layout>
                  <v-flex xs5>
                    <v-text-field
                      class="small"
                      label="Reviewer"
                      solo
                      readonly
                      hide-details
                      :value="reviewer"></v-text-field>
                  </v-flex>
                  <v-flex xs7>
                    <v-btn-toggle class="buttons elevation-2"
                      v-model="rating" @change="reviewChanged=true">
                      <v-btn flat value="bad">Bad</v-btn>
                      <v-btn flat value="good">Good</v-btn>
                      <v-btn flat value="goodExtra">Good extra</v-btn>
                    </v-btn-toggle>
                  </v-flex>
                </v-layout>
                <v-layout align-center justify-space-between>
                  <v-spacer />
                  <v-btn
                    color="primary"
                    :disabled="!reviewChanged"
                    @click="save">
                    Save
                    <v-icon right>save</v-icon>
                  </v-btn>
                  <v-menu v-if="currentSession && currentSession.datasets.length>1"
                    offset-y>
                    <v-btn
                      slot="activator"
                      flat
                      icon
                      color="primary">
                      <v-icon>more_vert</v-icon>
                    </v-btn>
                    <v-list>
                      <v-list-tile
                        v-for="(dataset, index) in currentSession.datasets"
                        :key="index"
                        :to="dataset._id"
                        :class="{'primary--text':dataset===currentDataset}">
                        <v-list-tile-title>{{dataset.name}}</v-list-tile-title>
                      </v-list-tile>
                    </v-list>
                  </v-menu>
                  <v-btn fab small
                    class="primary--text elevation-2"
                    :disabled="!previousDataset"
                    :to="previousDataset?previousDataset._id:''">
                    <v-icon>keyboard_arrow_left</v-icon>
                  </v-btn>
                  <v-btn fab small
                    class="primary--text elevation-2"
                    :disabled="!nextDataset"
                    :to="nextDataset?nextDataset._id:''">
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
    <v-dialog v-model="unsavedDialog" persistent max-width="400">
      <v-card>
        <v-card-title class="title">Review is not saved</v-card-title>
        <v-card-text>Do you want save before continue?</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn flat color="primary" @click="unsavedDialogYes">Yes</v-btn>
          <v-btn flat color="primary" @click="unsavedDialogNo">no</v-btn>
          <v-btn flat @click="unsavedDialogCancel">Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
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

    .loading-indicator-container {
      background: #ffffff57;
      position: relative;
    }
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
