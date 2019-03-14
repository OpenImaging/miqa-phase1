<script>
import Layout from "@/components/Layout.vue";
import { mapState, mapActions, mapGetters, mapMutations } from "vuex";

import UserButton from "@/components/girder/UserButton";
import SessionsView from "@/components/SessionsView";
import WindowControl from "@/components/WindowControl";
import ScreenshotDialog from "@/components/ScreenshotDialog";
import EmailDialog from "@/components/EmailDialog";
import KeyboardShortcutDialog from "@/components/KeyboardShortcutDialog";
import NavigationTabs from "@/components/NavigationTabs";
import { cleanDatasetName } from "@/utils/helper";

export default {
  name: "dataset",
  components: {
    UserButton,
    Layout,
    SessionsView,
    WindowControl,
    ScreenshotDialog,
    EmailDialog,
    KeyboardShortcutDialog,
    NavigationTabs
  },
  inject: ["girderRest"],
  data: () => ({
    note: "",
    rating: null,
    reviewer: "",
    reviewChanged: false,
    unsavedDialog: false,
    unsavedDialogResolve: null,
    emailDialog: false,
    keyboardShortcutDialog: false
  }),
  computed: {
    ...mapState(["vtkViews", "loadingDataset", "drawer", "screenshots"]),
    ...mapGetters([
      "nextDataset",
      "currentDataset",
      "getDataset",
      "currentSession",
      "previousDataset",
      "firstDatasetInPreviousSession",
      "firstDatasetInNextSession",
      "getSiteDisplayName"
    ])
  },
  async created() {
    await Promise.all([this.loadBatches(), this.loadSites()]);
    var datasetId = this.$route.params.datasetId;
    if (datasetId) {
      await this.loadAndSetSessionsByDatasetId(datasetId);
      try {
        await this.swapToDataset(datasetId);
        if (this.currentSession) {
          this.note = this.currentSession.meta.note;
          this.rating = this.currentSession.meta.rating;
          this.reviewer = this.currentSession.meta.reviewer;
        }
      } catch (ex) {
        this.$router.replace("/");
      }
    } else {
      this.setDrawer(true);
    }
  },
  watch: {
    currentSession(session, oldSession) {
      if (session === oldSession) {
        return;
      }
      if (session) {
        this.loadSessionMeta();
      }
    }
  },
  async beforeRouteUpdate(to, from, next) {
    this.selectSessionTreeByDataset(to.params.datasetId);
    let toDataset = this.getDataset(to.params.datasetId);
    let result = await this.beforeLeaveSession(toDataset);
    next(result);
    if (result) {
      this.swapToDataset(to.params.datasetId);
    }
  },
  async beforeRouteLeave(to, from, next) {
    let result = await this.beforeLeaveSession();
    next(result);
  },
  methods: {
    ...mapMutations(["setDrawer", "selectSessionTreeByDataset"]),
    ...mapActions([
      "loadBatches",
      "loadSites",
      "loadAndSetSessionsByDatasetId",
      "swapToDataset"
    ]),
    cleanDatasetName,
    async beforeLeaveSession(toDataset) {
      let currentDataset = this.currentDataset;
      if (
        currentDataset &&
        (!toDataset || toDataset.folderId !== this.currentDataset.folderId) &&
        this.reviewChanged
      ) {
        this.unsavedDialog = true;
        return await new Promise(resolve => {
          this.unsavedDialogResolve = resolve;
        });
      }
      return Promise.resolve(true);
    },
    // Load from the server again to get the latest
    async loadSessionMeta() {
      this.reviewChanged = false;
      let { data: folder } = await this.girderRest.get(
        `folder/${this.currentSession.folderId}`
      );
      var { meta } = folder;
      this.note = folder.meta.note;
      this.rating = folder.meta.rating;
      this.reviewer = folder.meta.reviewer;
      this.currentSession.meta = meta;
    },
    async save() {
      let user = this.girderRest.user;
      var meta = {
        ...this.currentSession.meta,
        ...{
          note: this.note,
          rating: this.rating !== undefined ? this.rating : null,
          reviewer: user.firstName + " " + user.lastName
        }
      };
      await this.girderRest.put(
        `folder/${this.currentSession.folderId}/metadata?allowNull=true`,
        meta
      );
      this.currentSession.meta = meta;
      this.reviewer = meta.reviewer;
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
    },
    setRating(rating) {
      if (rating !== this.rating) {
        this.rating = rating;
        this.ratingChanged();
      }
    },
    setNote(e) {
      this.note = e.target.value;
    },
    async ratingChanged() {
      if (!this.rating) {
        this.reviewChanged = true;
        return;
      }
      await this.save();
      if (this.firstDatasetInNextSession) {
        var currentDatasetId = this.currentDataset._id;
        this.$router.push(this.firstDatasetInNextSession._id);
        this.$snackbar({
          text: "Proceeded to next session",
          button: "Go back",
          timeout: 6000,
          immediate: true,
          callback: () => {
            this.$router.push(currentDatasetId);
          }
        });
      }
    },
    focusNote(el, e) {
      this.$refs.note.focus();
      e.preventDefault();
    }
  }
};
</script>

<template>
  <v-layout class="dataset" fill-height column>
    <v-toolbar app>
      <v-toolbar-side-icon
        @click.stop="setDrawer(!drawer)"
      ></v-toolbar-side-icon>
      <v-toolbar-title class="ml-0 pl-3">
        <span>MIQA</span>
      </v-toolbar-title>
      <NavigationTabs />
      <v-spacer></v-spacer>
      <v-btn icon class="mr-4" @click="keyboardShortcutDialog = true">
        <v-icon>keyboard</v-icon>
      </v-btn>
      <v-btn icon class="mr-4" @click="emailDialog = true">
        <v-badge :value="screenshots.length" right>
          <span slot="badge" dark>{{ screenshots.length }}</span>
          <v-icon>email</v-icon>
        </v-badge>
      </v-btn>
      <UserButton @user="girderRest.logout()" />
    </v-toolbar>
    <v-navigation-drawer
      app
      temporary
      width="350"
      :value="drawer"
      @input="setDrawer($event)"
    >
      <div class="sessions-bar">
        <v-toolbar dense flat>
          <v-toolbar-title>Sessions</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn icon to="sessions">
            <v-icon>open_in_new</v-icon>
          </v-btn>
        </v-toolbar>
        <SessionsView class="mt-1" minimal />
      </div>
    </v-navigation-drawer>
    <template v-if="currentDataset">
      <v-flex class="layout-container">
        <Layout />
        <v-layout
          v-if="loadingDataset"
          class="loading-indicator-container"
          align-center
          justify-center
          row
          fill-height
        >
          <v-progress-circular
            color="primary"
            :width="4"
            :size="50"
            indeterminate
          ></v-progress-circular>
        </v-layout>
      </v-flex>
      <v-flex shrink class="bottom">
        <v-container fluid grid-list-md class="py-3 px-2">
          <v-layout>
            <v-flex shrink style="flex-basis: 140px" class="mx-2">
              <v-layout align-center fill-height column>
                <v-flex class="pt-0">
                  <v-btn
                    fab
                    small
                    class="primary--text elevation-2 mt-0"
                    :disabled="!previousDataset"
                    :to="previousDataset ? previousDataset._id : ''"
                    v-mousetrap="{
                      bind: 'left',
                      disabled:
                        !previousDataset || unsavedDialog || loadingDataset,
                      handler: () =>
                        $router.push(previousDataset ? previousDataset._id : '')
                    }"
                  >
                    <v-icon>keyboard_arrow_left</v-icon>
                  </v-btn>
                  <v-btn
                    fab
                    small
                    class="primary--text elevation-2 mt-0"
                    :disabled="!nextDataset"
                    :to="nextDataset ? nextDataset._id : ''"
                    v-mousetrap="{
                      bind: 'right',
                      disabled: !nextDataset || unsavedDialog || loadingDataset,
                      handler: () =>
                        $router.push(nextDataset ? nextDataset._id : '')
                    }"
                  >
                    <v-icon>chevron_right</v-icon>
                  </v-btn>
                </v-flex>
                <v-flex shrink class="pb-0">
                  <v-btn
                    fab
                    small
                    class="primary--text elevation-2 mb-0"
                    :disabled="!firstDatasetInPreviousSession"
                    :to="
                      firstDatasetInPreviousSession
                        ? firstDatasetInPreviousSession._id
                        : ''
                    "
                  >
                    <v-icon>first_page</v-icon>
                  </v-btn>
                  <v-btn
                    fab
                    small
                    class="primary--text elevation-2 mb-0"
                    :disabled="!firstDatasetInNextSession"
                    :to="
                      firstDatasetInNextSession
                        ? firstDatasetInNextSession._id
                        : ''
                    "
                  >
                    <v-icon>last_page</v-icon>
                  </v-btn>
                </v-flex>
              </v-layout>
            </v-flex>
            <v-flex xs8 class="mx-2">
              <v-layout align-center justify-center class="subheading">
                <v-flex style="line-height: 36px">
                  {{ getSiteDisplayName(currentSession.meta.site) }},
                  <a
                    :href="
                      `/xnat/app/action/DisplayItemAction/search_value/${
                        currentSession.meta.experimentId
                      }/search_element/xnat:mrSessionData/search_field/xnat:mrSessionData.ID`
                    "
                    target="_blank"
                    >{{ currentSession.meta.experimentId }}</a
                  >
                  (<a
                    :href="
                      `/redcap/redcap_v8.4.0/DataEntry/record_home.php?pid=20&arm=1&id=${
                        currentSession.meta.experimentId2
                      }`
                    "
                    target="_blank"
                    >{{ currentSession.meta.experimentId2 }}</a
                  >),
                  {{ currentSession.meta.scanType }}
                </v-flex>
                <v-tooltip top v-if="reviewChanged">
                  <v-btn
                    slot="activator"
                    flat
                    icon
                    color="grey"
                    class="my-0"
                    @click="loadSessionMeta"
                  >
                    <v-icon>undo</v-icon>
                  </v-btn>
                  <span>Revert</span>
                </v-tooltip>
                <v-flex shrink v-if="currentSession.datasets.length > 1">
                  <span
                    >{{ cleanDatasetName(currentDataset.name) }} of
                    {{ currentSession.datasets.length }}</span
                  >
                  <v-menu offset-y top max-height="400" min-width="100" auto>
                    <v-btn
                      slot="activator"
                      flat
                      icon
                      color="primary"
                      class="my-0"
                    >
                      <v-icon>more_vert</v-icon>
                    </v-btn>
                    <v-list>
                      <v-list-tile
                        v-for="(dataset, index) in currentSession.datasets"
                        :key="index"
                        :to="dataset._id"
                        :class="{
                          'primary--text': dataset === currentDataset
                        }"
                      >
                        <v-list-tile-title>{{
                          cleanDatasetName(dataset.name)
                        }}</v-list-tile-title>
                      </v-list-tile>
                    </v-list>
                  </v-menu>
                </v-flex>
              </v-layout>
              <v-layout>
                <v-flex>
                  <v-textarea
                    solo
                    label="Note"
                    rows="3"
                    hide-details
                    @blur="setNote($event)"
                    @input="reviewChanged = true"
                    :value="this.note"
                    ref="note"
                    v-mousetrap="{ bind: 'n', handler: focusNote }"
                    v-mousetrap.element="{
                      bind: 'esc',
                      handler: () => $refs.note.blur()
                    }"
                  ></v-textarea>
                </v-flex>
              </v-layout>
              <v-layout>
                <v-flex>
                  <v-btn-toggle
                    class="buttons elevation-2"
                    v-model="rating"
                    @change="ratingChanged"
                  >
                    <v-btn
                      flat
                      value="bad"
                      color="red"
                      :disabled="!note"
                      v-mousetrap="{
                        bind: 'b',
                        handler: () => setRating('bad')
                      }"
                      >Bad</v-btn
                    >
                    <v-btn
                      flat
                      value="good"
                      color="green"
                      v-mousetrap="{
                        bind: 'g',
                        handler: () => setRating('good')
                      }"
                      >Good</v-btn
                    >
                    <v-btn
                      flat
                      value="usableExtra"
                      color="light-green"
                      v-mousetrap="{
                        bind: 'e',
                        handler: () => setRating('usableExtra')
                      }"
                      >Usable extra</v-btn
                    >
                  </v-btn-toggle>
                </v-flex>
                <v-flex shrink>
                  <v-text-field
                    class="small"
                    label="Reviewer"
                    solo
                    disabled
                    hide-details
                    :value="reviewer"
                  ></v-text-field>
                </v-flex>
                <v-flex shrink>
                  <v-btn
                    color="primary"
                    class="ma-0"
                    style="height: 40px"
                    :disabled="!reviewChanged"
                    @click="save"
                    v-mousetrap="{ bind: 'alt+s', handler: save }"
                  >
                    Save
                    <v-icon right>save</v-icon>
                  </v-btn>
                </v-flex>
              </v-layout>
            </v-flex>
            <v-flex xs4 class="mx-2 ml-3">
              <WindowControl v-if="vtkViews.length" class="py-0" />
            </v-flex>
          </v-layout>
        </v-container>
      </v-flex>
    </template>
    <v-layout v-else align-center justify-center row fill-height>
      <div class="title" v-if="!loadingDataset">Select a dataset</div>
    </v-layout>
    <v-dialog v-model="unsavedDialog" lazy persistent max-width="400">
      <v-card>
        <v-card-title class="title">Review is not saved</v-card-title>
        <v-card-text>Do you want save before continue?</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            flat
            color="primary"
            @click="unsavedDialogYes"
            v-mousetrap="{ bind: 'y', handler: el => el.focus() }"
            >Yes</v-btn
          >
          <v-btn
            flat
            color="primary"
            @click="unsavedDialogNo"
            v-mousetrap="{ bind: 'n', handler: el => el.focus() }"
            >no</v-btn
          >
          <v-btn
            flat
            @click="unsavedDialogCancel"
            v-mousetrap="{ bind: 'esc', handler: unsavedDialogCancel }"
            >Cancel</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
    <ScreenshotDialog />
    <EmailDialog v-model="emailDialog" :note="note" />
    <KeyboardShortcutDialog v-model="keyboardShortcutDialog" />
  </v-layout>
</template>

<style lang="scss" scoped>
.dataset {
  .sessions-bar {
    display: flex;
    flex-direction: column;
    height: 100%;

    .sessions-view {
      overflow: auto;
    }
  }

  .layout-container {
    position: relative;

    .loading-indicator-container {
      background: #ffffff57;
      position: relative;
    }
  }

  .bottom {
    > .container {
      position: relative;
    }

    .buttons {
      width: 100%;

      .v-btn {
        height: 40px;
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
