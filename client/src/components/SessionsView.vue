<script>
import { mapState, mapGetters, mapActions } from "vuex";
import { API_URL } from "../constants";

export default {
  name: "sessions-view",
  components: {},
  props: {
    minimal: {
      type: Boolean,
      default: false
    }
  },
  data: () => ({
    API_URL,
    deleteConfirmDialog: false,
    currentBatch: null,
    deletingBatch: false
  }),
  computed: {
    ...mapState(["batches", "sessionTreeCache", "sessionTree"]),
    ...mapGetters(["currentSession"])
  },
  methods: {
    ...mapActions(["loadSessionsByBatchId", "deleteBatch"]),
    loadSessions(batch) {
      if (!this.sessionTreeCache[batch._id]) {
        this.loadSessionsByBatchId(batch._id);
      }
    },
    async deleteCurrentBatch() {
      this.deletingBatch = true;
      await this.deleteBatch(this.currentBatch);
      this.deletingBatch = false;
      this.deleteConfirmDialog = false;
      // await
    }
  }
};
</script>

<template>
  <div class="sessions-view">
    <v-expansion-panel>
      <v-expansion-panel-content
        v-for="batch in batches"
        :key="batch._id"
        lazy
        @click.native="loadSessions(batch)"
      >
        <v-icon slot="actions">{{
          sessionTreeCache[batch._id] ? $vuetify.icons.expand : "refresh"
        }}</v-icon>
        <v-layout slot="header" align-center>
          {{ batch.name }}
          <v-btn
            v-if="!minimal"
            flat
            icon
            small
            :href="`${API_URL}/miqa/batch/${batch._id}/export`"
            @click.stop
          >
            <v-icon>attachment</v-icon>
          </v-btn>
          <v-spacer />
          <v-btn
            v-if="!minimal"
            flat
            icon
            small
            @click.stop="
              currentBatch = batch;
              deleteConfirmDialog = true;
            "
          >
            <v-icon>delete_outline</v-icon>
          </v-btn>
        </v-layout>
        <ul v-if="sessionTreeCache[batch._id]" class="experiment">
          <li
            v-for="experiment of sessionTreeCache[batch._id].experiments"
            class="body-2"
            :key="experiment.folderId"
          >
            {{ experiment.name }}
            <ul class="sessions">
              <li
                v-for="session of experiment.sessions"
                class="body-1"
                :key="session.folderId"
                :class="{ current: session === currentSession }"
              >
                <v-btn
                  class="ml-0 px-1"
                  href
                  flat
                  small
                  :to="session.datasets[0]._id"
                  active-class=""
                  >{{ session.name }}</v-btn
                >
                <v-icon small v-if="session.meta && session.meta.rating"
                  >check</v-icon
                >
              </li>
            </ul>
          </li>
        </ul>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-dialog
      v-model="deleteConfirmDialog"
      :persistent="deletingBatch"
      max-width="400"
    >
      <v-card>
        <v-card-title class="title">{{
          deletingBatch ? "Deleting..." : "Confirm delete"
        }}</v-card-title>
        <v-card-text>
          {{ currentBatch ? currentBatch.name : "" }}
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            v-if="!deletingBatch"
            flat
            @click="deleteConfirmDialog = false"
          >
            Cancel
          </v-btn>

          <v-btn
            color="primary"
            flat
            :loading="deletingBatch"
            @click="deleteCurrentBatch"
          >
            Yes
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style lang="scss" scoped>
.current {
  background: rgb(206, 206, 206);
}

ul.experiment {
  list-style: none;
}

ul.sessions {
  padding-left: 15px;
}
</style>
