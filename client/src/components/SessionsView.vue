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
  data: () => ({ API_URL }),
  computed: {
    ...mapState(["batches", "sessionTreeCache", "sessionTree"]),
    ...mapGetters(["currentSession"])
  },
  methods: {
    ...mapActions(["loadSessionsByBatchId"]),
    loadSessions(batch) {
      if (!this.sessionTreeCache[batch._id]) {
        this.loadSessionsByBatchId(batch._id);
      }
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
        @click.native="loadSessions(batch)">
        <v-icon slot="actions">{{sessionTreeCache[batch._id]?$vuetify.icons.expand:'refresh'}}</v-icon>
        <div slot="header">{{batch.name}}
          <v-btn v-if="!minimal" flat icon small
            :href='`${API_URL}/miqa/batch/${batch._id}/export`'>
            <v-icon>attachment</v-icon>
          </v-btn>
        </div>
        <ul v-if="sessionTreeCache[batch._id]">
          <li v-for="experiment of sessionTreeCache[batch._id].experiments" class="body-2" :key="experiment.folderId">
            {{experiment.name}}
            <ul>
              <li v-for="(session) of experiment.sessions" class="body-1" :key="session.folderId" 
              :class="{current:session===currentSession}">
                <v-btn href flat small :to="session.datasets[0]._id" active-class="">{{session.name}}</v-btn>
                <!-- <ul>
                  <li v-for="(dataset) of session.datasets" :key="dataset._id" :class="{current:dataset._id===currentDatasetId}">
                    <v-btn href flat small :to="dataset._id" active-class="">{{dataset.name}}</v-btn>
                  </li>
                </ul> -->
              </li>
            </ul>
          </li>
        </ul>
      </v-expansion-panel-content>
    </v-expansion-panel>
  </div>
</template>

<style lang="scss" scoped>
.current {
  background: rgb(206, 206, 206);
}
</style>
