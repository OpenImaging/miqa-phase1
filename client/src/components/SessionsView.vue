<script>
import { mapState, mapGetters } from "vuex";
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
    API_URL
  }),
  computed: {
    ...mapState([
      "experiments",
      "experimentIds",
      "experimentSessions",
      "sessions",
      "sessionDatasets",
      "sessionsModifiedTime",
      "datasets"
    ]),
    ...mapGetters(["currentSession"]),
    orderedExperiments() {
      const allExperiments = this.experiments;
      return this.experimentIds.map(expId => allExperiments[expId]);
    },
    loadingIcon() {
      return this.loadingExperiment
        ? "mdi-progress-clock"
        : "mdi-check-circle-outline";
    },
    loadingIconColor() {
      return this.loadingExperiment ? "red" : "green";
    }
  },
  methods: {
    sessionsForExperiment(expId) {
      const expSessionIds = this.experimentSessions[expId];
      const allSessions = this.sessions;
      return expSessionIds.map(sessionId => allSessions[sessionId]);
    },
    getIdOfFirstDatasetInSession(sessionId) {
      return this.sessionDatasets[sessionId][0];
    },
    ratingToLabel(rating) {
      switch (rating) {
        case "questionable":
          return "Q";
        case "good":
          return "G";
        case "bad":
          return "B";
        case "usableExtra":
          return "E";
      }
    }
  }
};
</script>

<template>
  <div class="sessions-view">
    <ul
      class="experiment"
      v-if="orderedExperiments && orderedExperiments.length"
    >
      <li
        v-for="experiment of orderedExperiments"
        class="body-2"
        :key="`e.${experiment.id}`"
      >
        {{ experiment.name }}
        <ul class="sessions">
          <li
            v-for="session of sessionsForExperiment(experiment.id)"
            class="body-1"
            :key="`s.${session.id}-${sessionsModifiedTime}`"
            :class="{
              current: session === currentSession,
              cached: session.cached
            }"
          >
            <v-btn
              class="ml-0 px-1 session-name"
              href
              text
              small
              :to="getIdOfFirstDatasetInSession(session.id)"
              active-class=""
              >{{ session.name
              }}<span small v-if="session.meta && session.meta.rating"
                >&nbsp;&nbsp;({{ ratingToLabel(session.meta.rating) }})</span
              ></v-btn
            >
          </li>
        </ul>
      </li>
    </ul>
    <div v-else class="text-xs-center body-2">No imported sessions</div>
  </div>
</template>

<style lang="scss" scoped>
.current {
  background: rgb(206, 206, 206);
}

li.cached {
  list-style-type: disc;
}

ul.experiment {
  list-style: none;
}

ul.sessions {
  padding-left: 15px;
}
</style>

<style lang="scss">
.sessions-view .session-name .v-btn__content {
  text-transform: none;
}
</style>
