<script>
import { mapActions } from "vuex";

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
  computed: {},
  async created() {
    await this.loadBatches();
  },
  methods: {
    ...mapActions(["loadBatches"])
  }
};
</script>

<template>
  <div class="sessions">
    <GenericNavigationBar />
    <v-container>
      <v-layout justify-center>
        <v-flex xl7 lg11>
          <v-layout>
            <CSVImporter />
          </v-layout>
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

<style lang="scss" scoped>
</style>
