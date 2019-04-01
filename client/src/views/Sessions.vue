<script>
import { mapState, mapActions } from "vuex";

import GenericNavigationBar from "@/components/GenericNavigationBar";
import CSVImporter from "../components/CSVImporter";
import SessionsView from "../components/SessionsView";

export default {
  name: "Sessions",
  components: {
    GenericNavigationBar,
    CSVImporter,
    SessionsView
  },
  inject: ["girderRest"],
  computed: { ...mapState([]) },
  async created() {
    await this.loadSessions();
  },
  methods: {
    ...mapActions(["loadSessions"])
  }
};
</script>

<template>
  <div class="sessions">
    <GenericNavigationBar />
    <v-container>
      <v-layout justify-center>
        <v-flex xl6 lg10>
          <div class="subheading font-weight-medium">Create</div>
          <v-layout>
            <v-flex lg7 md8>
              <CSVImporter />
            </v-flex>
          </v-layout>
          <div class="subheading font-weight-medium mt-2">
            Sessions
          </div>
          <v-layout>
            <v-flex>
              <SessionsView class="mt-2" />
            </v-flex>
          </v-layout>
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<style lang="scss" scoped></style>
