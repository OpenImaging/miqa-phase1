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
    ...mapState(["sessionTree"]),
    ...mapGetters(["currentSession"])
  },
  methods: {}
};
</script>

<template>
  <div class="sessions-view">
    <ul class="experiment">
      <li
        v-for="experiment of sessionTree"
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
