<script>
import _ from "lodash";

import {
  NavigationFailureType,
  isNavigationFailure
} from "vue-router/src/util/errors";
import Layout from "@/components/Layout.vue";
import { mapState, mapActions, mapGetters, mapMutations } from "vuex";

import NavbarTitle from "@/components/NavbarTitle";
import UserButton from "@/components/girder/UserButton";
import DataImportExport from "../components/DataImportExport";
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
    NavbarTitle,
    UserButton,
    Layout,
    DataImportExport,
    SessionsView,
    WindowControl,
    ScreenshotDialog,
    EmailDialog,
    KeyboardShortcutDialog,
    NavigationTabs
  },
  inject: ["girderRest", "userLevel"],
  data: () => ({
    newNote: "",
    rating: null,
    reviewer: "",
    reviewChanged: false,
    unsavedDialog: false,
    unsavedDialogResolve: null,
    emailDialog: false,
    editingNoteDialog: false,
    editingNote: "",
    showNotePopup: false,
    keyboardShortcutDialog: false,
    scanning: false,
    direction: "forward",
    advanceTimeoutId: null,
    nextAnimRequest: null
  }),
  computed: {
    ...mapState([
      "currentDatasetId",
      "vtkViews",
      "loadingDataset",
      "errorLoadingDataset",
      "drawer",
      "screenshots",
      "sessionCachedPercentage",
      "sessionDatasets"
    ]),
    ...mapGetters([
      "nextDataset",
      "getDataset",
      "currentDataset",
      "currentSession",
      "previousDataset",
      "firstDatasetInPreviousSession",
      "firstDatasetInNextSession",
      "getSiteDisplayName"
    ]),
    currentSessionDatasets() {
      return this.sessionDatasets[this.currentSession.id];
    },
    note() {
      if (this.currentSession && this.currentSession.meta) {
        return this.currentSession.meta.note;
      } else {
        return "";
      }
    },
    noteSegments() {
      if (this.currentSession && this.note) {
        return this.note.split(/[\r\n]+/g);
      } else {
        return [];
      }
    },
    lastNoteTruncated() {
      const segments = this.noteSegments;
      if (segments.length > 0) {
        const lastSeg = segments.slice(-1)[0];
        console.log(`last note: ${lastSeg}`);
        return `${lastSeg.substring(0, 32)}...`;
      }
      return "";
    }
  },
  async created() {
    this.debouncedDatasetSliderChange = _.debounce(
      this.debouncedDatasetSliderChange,
      30
    );
    await Promise.all([this.loadSessions(), this.loadSites()]);
    var datasetId = this.$route.params.datasetId;
    var dataset = this.getDataset(datasetId);
    if (dataset) {
      await this.swapToDataset(dataset);
    } else {
      this.$router.replace("/").catch(this.handleNavigationError);
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
    let toDataset = this.getDataset(to.params.datasetId);
    let result = await this.beforeLeaveSession(toDataset);
    next(result);
    if (result && toDataset) {
      this.swapToDataset(toDataset);
    }
  },
  async beforeRouteLeave(to, from, next) {
    let result = await this.beforeLeaveSession();
    next(result);
  },
  methods: {
    ...mapMutations(["setDrawer"]),
    ...mapActions(["loadSessions", "loadSites", "swapToDataset"]),
    cleanDatasetName,
    handleNavigationError(fail) {
      let failureType = "unknown";
      if (isNavigationFailure(fail, NavigationFailureType.redirected)) {
        failureType = "redirected";
      } else if (isNavigationFailure(fail, NavigationFailureType.aborted)) {
        failureType = "aborted";
      } else if (isNavigationFailure(fail, NavigationFailureType.cancelled)) {
        failureType = "cancelled";
      } else if (isNavigationFailure(fail, NavigationFailureType.duplicated)) {
        failureType = "duplicated";
      }
      this.scanning = false;
      console.log(`Caught navigation error (${failureType})`);
    },
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
      var { data: folder } = await this.girderRest.get(
        `folder/${this.currentSession.folderId}`
      );
      var { meta } = folder;
      this.newNote = "";
      this.rating = folder.meta.rating;
      this.reviewer = folder.meta.reviewer;
      this.currentSession.meta = meta;
    },
    async save() {
      var user = this.girderRest.user;
      var initial =
        user.firstName.charAt(0).toLocaleUpperCase() +
        user.lastName.charAt(0).toLocaleUpperCase();
      var date = new Date().toISOString().slice(0, 10);
      var note = "";
      if (this.newNote.trim()) {
        note =
          (this.note ? this.note + "\n" : "") +
          `${initial}(${date}): ${this.newNote}`;
      } else {
        note = this.note;
      }
      var meta = {
        ...this.currentSession.meta,
        ...{
          note,
          rating: this.rating !== undefined ? this.rating : null,
          reviewer: user.firstName + " " + user.lastName
        }
      };
      await this.girderRest.put(
        `folder/${this.currentSession.folderId}/metadata?allowNull=true`,
        meta
      );
      this.newNote = "";
      this.currentSession.meta = meta;
      this.reviewer = meta.reviewer;
      this.reviewChanged = false;
    },
    enableEditHistroy() {
      this.editingNoteDialog = true;
      this.editingNote = this.note;
    },
    async saveNoteHistory() {
      var meta = {
        ...this.currentSession.meta,
        ...{
          note: this.editingNote
        }
      };
      await this.girderRest.put(
        `folder/${this.currentSession.folderId}/metadata?allowNull=true`,
        meta
      );
      this.currentSession.meta = meta;
      this.editingNoteDialog = false;
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
      this.newNote = e.target.value;
    },
    async ratingChanged() {
      if (!this.rating) {
        this.reviewChanged = true;
        return;
      }
      await this.save();
      if (this.firstDatasetInNextSession) {
        var currentDatasetId = this.currentDatasetId;
        this.$router
          .push(this.firstDatasetInNextSession)
          .catch(this.handleNavigationError);
        this.$snackbar({
          text: "Proceeded to next session",
          button: "Go back",
          timeout: 6000,
          immediate: true,
          callback: () => {
            this.$router
              .push(currentDatasetId)
              .catch(this.handleNavigationError);
          }
        });
      }
    },
    focusNote(el, e) {
      this.$refs.note.focus();
      e.preventDefault();
    },
    debouncedDatasetSliderChange(index) {
      var datasetId = this.currentSessionDatasets[index];
      this.$router.push(datasetId).catch(this.handleNavigationError);
    },
    updateImage() {
      if (this.direction === "back") {
        this.$router
          .push(this.previousDataset ? this.previousDataset : "")
          .catch(this.handleNavigationError);
      } else {
        this.$router
          .push(this.nextDataset ? this.nextDataset : "")
          .catch(this.handleNavigationError);
      }
    },
    advanceLoop() {
      if (this.scanning) {
        this.updateImage();
        this.nextAnimRequest = window.requestAnimationFrame(this.advanceLoop);
      }
    },
    handleMouseDown(direction) {
      if (!this.scanning) {
        this.scanning = true;
        this.direction = direction;
        this.updateImage();
        const self = this;
        this.advanceTimeoutId = window.setTimeout(function() {
          window.requestAnimationFrame(self.advanceLoop);
        }, 500);
      }
    },
    handleMouseUp() {
      this.scanning = false;
      if (this.advanceTimeoutId !== null) {
        window.clearTimeout(this.advanceTimeoutId);
        this.advanceTimeoutId = null;
      }
      if (this.nextAnimRequest !== null) {
        window.cancelAnimationFrame(this.nextAnimRequest);
        this.nextAnimRequest = null;
      }
    }
  }
};
</script>

<template>
  <v-layout class="dataset" fill-height column>
    <v-app-bar app dense>
      <NavbarTitle />
      <NavigationTabs />
      <v-spacer></v-spacer>
      <v-btn icon class="mr-4" @click="keyboardShortcutDialog = true">
        <v-icon>keyboard</v-icon>
      </v-btn>
      <v-btn
        icon
        class="mr-4"
        @click="emailDialog = true"
        :disabled="!currentDataset"
      >
        <v-badge :value="screenshots.length" right>
          <span slot="badge" dark>{{ screenshots.length }}</span>
          <v-icon>email</v-icon>
        </v-badge>
      </v-btn>
      <UserButton @user="girderRest.logout()" />
    </v-app-bar>
    <v-navigation-drawer
      app
      temporary
      width="350"
      :value="drawer"
      @input="setDrawer($event)"
    >
      <div class="sessions-bar">
        <v-toolbar dense flat max-height="48px">
          <v-toolbar-title>Sessions</v-toolbar-title>
        </v-toolbar>
        <DataImportExport v-if="userLevel.value <= 2" />
        <SessionsView class="mt-1" minimal />
      </div>
    </v-navigation-drawer>
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
    <template v-if="currentDataset">
      <v-flex class="layout-container">
        <Layout />
        <v-layout
          v-if="errorLoadingDataset"
          align-center
          justify-center
          fill-height
        >
          <div class="title">Error loading this dataset</div>
        </v-layout>
      </v-flex>
      <v-flex shrink class="bottom">
        <v-container fluid grid-list-sm class="pa-2">
          <v-layout>
            <v-flex
              xs4
              class="mx-2"
              style="display:flex;flex-direction:column;"
            >
              <v-layout align-center>
                <v-flex shrink>
                  <v-btn
                    fab
                    small
                    class="primary--text my-0 elevation-2 smaller"
                    :disabled="!previousDataset"
                    v-on:mousedown="handleMouseDown('back')"
                    v-on:mouseup="handleMouseUp()"
                    v-mousetrap="{
                      bind: 'left',
                      disabled:
                        !previousDataset || unsavedDialog || loadingDataset,
                      handler: {
                        keydown: function() {
                          handleMouseDown('back');
                        },
                        keyup: handleMouseUp
                      }
                    }"
                  >
                    <v-icon>keyboard_arrow_left</v-icon>
                  </v-btn>
                </v-flex>
                <v-flex style="text-align: center;">
                  <span
                    >{{ currentDataset.index + 1 }} of
                    {{ currentSessionDatasets.length }}</span
                  >
                </v-flex>
                <v-flex shrink>
                  <v-btn
                    fab
                    small
                    class="primary--text my-0 elevation-2 smaller"
                    :disabled="!nextDataset"
                    v-on:mousedown="handleMouseDown('forward')"
                    v-on:mouseup="handleMouseUp()"
                    v-mousetrap="{
                      bind: 'right',
                      disabled: !nextDataset || unsavedDialog || loadingDataset,
                      handler: {
                        keydown: function() {
                          handleMouseDown('forward');
                        },
                        keyup: handleMouseUp
                      }
                    }"
                  >
                    <v-icon>chevron_right</v-icon>
                  </v-btn>
                </v-flex>
              </v-layout>
              <v-layout align-center>
                <v-flex class="ml-3 mr-1">
                  <v-slider
                    class="dataset-slider"
                    hide-details
                    always-dirty
                    thumb-label
                    thumb-size="28"
                    :min="1"
                    :max="
                      currentSessionDatasets.length === 1
                        ? 2
                        : currentSessionDatasets.length
                    "
                    :disabled="currentSessionDatasets.length === 1"
                    :height="24"
                    :value="currentDataset.index + 1"
                    @input="debouncedDatasetSliderChange($event - 1)"
                  ></v-slider>
                </v-flex>
                <v-flex shrink>
                  {{ Math.round(sessionCachedPercentage * 100) }}%
                </v-flex>
              </v-layout>
              <v-layout align-center class="bottom-row">
                <v-flex shrink>
                  <v-btn
                    fab
                    small
                    class="primary--text mb-0 elevation-2 smaller"
                    :disabled="!firstDatasetInPreviousSession"
                    :to="
                      firstDatasetInPreviousSession
                        ? firstDatasetInPreviousSession
                        : ''
                    "
                  >
                    <v-icon>fast_rewind</v-icon>
                  </v-btn>
                </v-flex>
                <v-spacer />
                <v-flex shrink>
                  <v-btn
                    fab
                    small
                    class="primary--text mb-0 elevation-2 smaller"
                    :disabled="!firstDatasetInNextSession"
                    :to="
                      firstDatasetInNextSession ? firstDatasetInNextSession : ''
                    "
                  >
                    <v-icon>fast_forward</v-icon>
                  </v-btn>
                </v-flex>
              </v-layout>
            </v-flex>
            <v-flex xs4 class="mx-2">
              <v-container class="pa-0">
                <v-row>
                  <v-col cols="12" class="pb-1 pt-0">
                    <v-container class="pa-0">
                      <v-row>
                        <v-col cols="3" class="pb-1 pt-0">
                          Site
                        </v-col>
                        <v-col cols="9" class="pb-1 pt-0 justifyRight">
                          {{ getSiteDisplayName(currentSession.meta.site) }}
                        </v-col>
                      </v-row>
                      <v-row>
                        <v-col cols="3" class="pb-1 pt-0">
                          Experiment
                        </v-col>
                        <v-col cols="9" class="pb-1 pt-0 justifyRight">
                          <a
                            :href="
                              `/xnat/app/action/DisplayItemAction/search_value/${currentSession.meta.experimentId}/search_element/  xnat:mrSessionData/      search_field/xnat:mrSessionData.ID`
                            "
                            target="_blank"
                            >{{ currentSession.meta.experimentId }}</a
                          >
                        </v-col>
                      </v-row>
                      <v-row>
                        <v-col cols="3" class="pb-1 pt-0">
                          Session
                        </v-col>
                        <v-col cols="9" class="pb-1 pt-0 justifyRight">
                          {{ currentSession.name }}
                        </v-col>
                      </v-row>
                    </v-container>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col class="pb-1 pt-0" cols="10">
                    Note history: {{ lastNoteTruncated }}
                  </v-col>
                  <v-col class="pb-1 pt-0" cols="1">
                    <v-menu
                      v-model="showNotePopup"
                      :close-on-content-click="false"
                      :nudge-right="250"
                      offset-y
                      open-on-hover
                      top
                      left
                      ref="historyMenu"
                    >
                      <template v-slot:activator="{ on }">
                        <v-btn
                          text
                          small
                          icon
                          :disabled="noteSegments.length < 1"
                          class="ma-0"
                          v-on="on"
                          v-mousetrap="{
                            bind: 'h',
                            handler: () => (showNotePopup = !showNotePopup)
                          }"
                          ><v-icon>arrow_drop_up</v-icon></v-btn
                        >
                      </template>
                      <v-card>
                        <v-card-text class="note-history">
                          <pre>{{ note }}</pre>
                        </v-card-text>
                      </v-card>
                    </v-menu>
                  </v-col>
                  <v-col class="pb-1 pt-0" cols="1">
                    <v-btn
                      text
                      small
                      icon
                      class="ma-0"
                      :disabled="userLevel.value > 1"
                      @click="enableEditHistroy"
                      ><v-icon style="font-size: 18px;">edit</v-icon></v-btn
                    >
                  </v-col>
                </v-row>
                <v-row class="pb-1 pt-1">
                  <v-col cols="11" class="pb-1 pt-0 pr-0">
                    <v-text-field
                      class="note-field"
                      label="Note"
                      solo
                      hide-details
                      @blur="setNote($event)"
                      @input="reviewChanged = true"
                      :value="this.newNote"
                      ref="note"
                      v-mousetrap="{ bind: 'n', handler: focusNote }"
                      v-mousetrap.element="{
                        bind: 'esc',
                        handler: () => $refs.note.blur()
                      }"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="1" class="pb-1 pt-0">
                    <v-tooltip top>
                      <template v-slot:activator="{ on }">
                        <v-btn
                          text
                          icon
                          small
                          color="grey"
                          class="my-0"
                          :disabled="!reviewChanged"
                          v-on="on"
                          @click="loadSessionMeta"
                        >
                          <v-icon>undo</v-icon>
                        </v-btn>
                      </template>
                      <span>Revert</span>
                    </v-tooltip>
                  </v-col>
                </v-row>
                <v-row no-gutters class="pb-1">
                  <v-col cols="6" class="pb-1 pt-0" v-if="userLevel.value <= 2">
                    <v-btn-toggle
                      class="buttons"
                      v-model="rating"
                      @change="ratingChanged"
                    >
                      <v-btn
                        v-if="userLevel.value <= 1"
                        text
                        small
                        value="bad"
                        color="red"
                        :disabled="!newNote && !note"
                        v-mousetrap="{
                          bind: 'b',
                          handler: () => setRating('bad')
                        }"
                        >Bad</v-btn
                      >
                      <v-btn
                        text
                        small
                        value="questionable"
                        color="orange"
                        :disabled="!newNote && !note"
                        ><b>?</b></v-btn
                      >
                      <v-btn
                        text
                        small
                        value="good"
                        color="green"
                        v-mousetrap="{
                          bind: 'g',
                          handler: () => setRating('good')
                        }"
                        >Good</v-btn
                      >
                      <v-btn
                        text
                        small
                        value="usableExtra"
                        color="light-green"
                        v-mousetrap="{
                          bind: 'u',
                          handler: () => setRating('usableExtra')
                        }"
                        >Extra</v-btn
                      >
                    </v-btn-toggle>
                  </v-col>
                  <v-col cols="4" class="pb-1 pt-0">
                    <v-text-field
                      class="small"
                      label="Reviewer"
                      solo
                      disabled
                      hide-details
                      :value="reviewer"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="2" class="pb-1 pt-0">
                    <v-btn
                      color="primary"
                      class="ma-0"
                      style="height: 36px"
                      small
                      :disabled="!reviewChanged"
                      @click="save"
                      v-mousetrap="{ bind: 'alt+s', handler: save }"
                    >
                      Save
                      <v-icon right>save</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>
            </v-flex>
            <v-flex xs4 class="mx-2">
              <WindowControl v-if="vtkViews.length" class="py-0" />
            </v-flex>
          </v-layout>
        </v-container>
      </v-flex>
    </template>
    <v-layout
      v-if="!currentDataset && !loadingDataset"
      align-center
      justify-center
      fill-height
    >
      <div class="title">Select a session</div>
    </v-layout>
    <v-dialog v-model="unsavedDialog" persistent max-width="400">
      <v-card>
        <v-card-title class="title">Review is not saved</v-card-title>
        <v-card-text>Do you want save before continue?</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            text
            color="primary"
            @click="unsavedDialogYes"
            v-mousetrap="{ bind: 'y', handler: el => el.focus() }"
            >Yes</v-btn
          >
          <v-btn
            text
            color="primary"
            @click="unsavedDialogNo"
            v-mousetrap="{ bind: 'n', handler: el => el.focus() }"
            >no</v-btn
          >
          <v-btn
            text
            @click="unsavedDialogCancel"
            v-mousetrap="{ bind: 'esc', handler: unsavedDialogCancel }"
            >Cancel</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="editingNoteDialog" max-width="600">
      <v-card>
        <v-card-text>
          <v-textarea
            label="Edit note history"
            filled
            hide-details
            no-resize
            :rows="12"
            v-model.lazy="editingNote"
          ></v-textarea
        ></v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text color="primary" @click="saveNoteHistory">
            Save
          </v-btn>
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

  .experiment-note {
    max-width: 250px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .loading-indicator-container {
    background: #ffffff57;
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 1;
  }

  .layout-container {
    position: relative;
  }

  .v-btn.smaller {
    height: 35px;
    width: 35px;
  }

  .bottom {
    > .container {
      position: relative;
    }

    .buttons {
      width: 100%;

      .v-btn {
        height: 36px;
        opacity: 1;
        flex: 1;
      }
    }
  }
}
</style>

<style lang="scss">
.justifyRight {
  text-align: right;
}

.dataset {
  .v-text-field.small .v-input__control {
    min-height: 36px !important;
  }

  .note-field .v-input__control {
    min-height: 36px !important;
  }

  .v-input--slider.dataset-slider {
    margin-top: 0;
  }
}

.v-card__text.note-history {
  width: 500px;
  max-height: 400px;
  overflow-y: auto;

  pre {
    white-space: pre-wrap;
    font-family: inherit;
    overflow-y: auto;
  }
}
</style>
