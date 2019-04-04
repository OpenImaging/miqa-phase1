<script>
import _ from "lodash";

import Layout from "@/components/Layout.vue";
import { mapState, mapActions, mapGetters, mapMutations } from "vuex";

import UserButton from "@/components/girder/UserButton";
import CSVImportExport from "../components/CSVImportExport";
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
    CSVImportExport,
    SessionsView,
    WindowControl,
    ScreenshotDialog,
    EmailDialog,
    KeyboardShortcutDialog,
    NavigationTabs
  },
  inject: ["girderRest"],
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
    sliderTempValue: 0
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
    ]),
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
    }
  },
  async created() {
    this.datasetSliderChange = _.throttle(this.datasetSliderChange, 50);
    this.debouncedDatasetSliderChange = _.debounce(
      this.debouncedDatasetSliderChange,
      1000
    );
    await Promise.all([this.loadSessions(), this.loadSites()]);
    var datasetId = this.$route.params.datasetId;
    var dataset = this.getDataset(datasetId);
    if (dataset) {
      await this.swapToDataset(dataset);
    } else {
      this.$router.replace("/");
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
    },
    datasetSliderChange(index) {
      this.sliderTempValue = index;
      this.debouncedDatasetSliderChange(index);
    },
    debouncedDatasetSliderChange(index) {
      this.sliderTempValue = null;
      var dataset = this.currentSession.datasets[index];
      this.$router.push(dataset._id);
    }
  }
};
</script>

<template>
  <v-layout class="dataset" fill-height column>
    <v-toolbar app dense>
      <v-toolbar-title>
        <span>MIQA</span>
      </v-toolbar-title>
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
        </v-toolbar>
        <CSVImportExport />
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
        <v-container fluid grid-list-sm class="pa-2">
          <v-layout>
            <v-flex shrink class="mx-2" style="display:flex;flex-direction:column;">
              <v-layout align-center>
                <v-flex shrink>
                  <v-btn
                    fab
                    small
                    class="primary--text my-0 elevation-2 smaller"
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
                </v-flex>
                <v-flex style="width:140px; text-align: center;">
                  <span
                    >{{
                      sliderTempValue
                        ? sliderTempValue + 1
                        : currentSession.datasets.indexOf(currentDataset) + 1
                    }}
                    of {{ currentSession.datasets.length }}</span
                  >
                </v-flex>
                <v-flex shrink>
                  <v-btn
                    fab
                    small
                    class="primary--text my-0 elevation-2 smaller"
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
              </v-layout>
              <v-layout align-center>
                <v-flex class="ml-4">
                  <v-slider
                    class="dataset-slider"
                    hide-details
                    always-dirty
                    :min="0"
                    :max="
                      currentSession.datasets.length === 1
                        ? 1
                        : currentSession.datasets.length - 1
                    "
                    :disabled="currentSession.datasets.length === 1"
                    :height="24"
                    :value="currentSession.datasets.indexOf(currentDataset)"
                    @input="datasetSliderChange"
                  ></v-slider>
                </v-flex>
                <v-flex shrink>
                  <v-menu
                    offset-y
                    top
                    max-height="400"
                    min-width="100"
                    auto
                    :disabled="currentSession.datasets.length === 1"
                  >
                    <v-btn
                      slot="activator"
                      flat
                      icon
                      small
                      color="primary"
                      class="my-0"
                      :disabled="currentSession.datasets.length === 1"
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
              <v-layout class="bottom-row">
                <v-flex shrink>
                  <v-btn
                    fab
                    small
                    class="primary--text mb-0 elevation-2 smaller"
                    :disabled="!firstDatasetInPreviousSession"
                    :to="
                      firstDatasetInPreviousSession
                        ? firstDatasetInPreviousSession._id
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
                      firstDatasetInNextSession
                        ? firstDatasetInNextSession._id
                        : ''
                    "
                  >
                    <v-icon>fast_forward</v-icon>
                  </v-btn>
                </v-flex>
              </v-layout>
            </v-flex>
            <v-flex xs8 class="mx-2">
              <v-layout align-center justify-center class="body-2">
                <v-flex>
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
                  {{ currentSession.name }}
                </v-flex>
                <v-spacer />
                <v-flex
                  shrink
                  class="experiment-note"
                  v-if="currentSession.meta.experimentNote"
                >
                  <v-tooltip top>
                    <span slot="activator">{{
                      currentSession.meta.experimentNote
                    }}</span>
                    {{ currentSession.meta.experimentNote }}
                  </v-tooltip>
                </v-flex>
              </v-layout>
              <v-layout align-center v-if="noteSegments.length">
                <v-flex shrink>
                  Note history: {{ noteSegments.slice(-1)[0] }}
                </v-flex>
                <v-flex shrink class="pa-0" v-if="noteSegments.length > 1">
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
                        flat
                        small
                        icon
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
                </v-flex>
                <v-flex
                  shrink
                  class="pa-0"
                  v-if="girderRest.user && girderRest.user.admin"
                >
                  <v-btn flat small icon class="ma-0" @click="enableEditHistroy"
                    ><v-icon style="font-size: 18px;">edit</v-icon></v-btn
                  >
                </v-flex>
              </v-layout>
              <div v-else style="height:28px;"></div>
              <v-layout align-center>
                <v-flex>
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
                </v-flex>
                <v-flex shrink v-if="reviewChanged">
                  <v-tooltip top>
                    <v-btn
                      slot="activator"
                      flat
                      icon
                      small
                      color="grey"
                      class="my-0"
                      @click="loadSessionMeta"
                    >
                      <v-icon>undo</v-icon>
                    </v-btn>
                    <span>Revert</span>
                  </v-tooltip>
                </v-flex>
              </v-layout>
              <v-layout>
                <v-flex>
                  <v-btn-toggle
                    class="buttons"
                    v-model="rating"
                    @change="ratingChanged"
                  >
                    <v-btn
                      flat
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
                      flat
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
                      flat
                      small
                      value="usableExtra"
                      color="light-green"
                      v-mousetrap="{
                        bind: 'u',
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
                    style="height: 36px"
                    small
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
            <v-flex xs4 class="mx-2">
              <WindowControl v-if="vtkViews.length" class="py-0" />
            </v-flex>
          </v-layout>
        </v-container>
      </v-flex>
    </template>
    <v-layout v-else align-center justify-center row fill-height>
      <div class="title" v-if="!loadingDataset">Select a session</div>
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
    <v-dialog v-model="editingNoteDialog" lazy max-width="600">
      <v-card>
        <v-card-text>
          <v-textarea
            label="Edit note history"
            box
            hide-details
            no-resize
            :rows="12"
            v-model.lazy="editingNote"
          ></v-textarea
        ></v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn flat color="primary" @click="saveNoteHistory">
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

  .layout-container {
    position: relative;

    .loading-indicator-container {
      background: #ffffff57;
      position: relative;
    }
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

        &:nth-child(1) {
          width: 30%;
        }

        &:nth-child(2) {
          width: 30%;
        }

        &:nth-child(3) {
          width: 40%;
        }
      }
    }
  }
}
</style>

<style lang="scss">
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
