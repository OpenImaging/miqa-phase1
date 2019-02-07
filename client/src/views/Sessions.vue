<script>
import { mapActions } from "vuex";

import UserButton from "@/components/girder/UserButton";
import SessionsView from "../components/SessionsView";
import CSVImporter from "../components/CSVImporter";
import NavigationTabs from "@/components/NavigationTabs";

export default {
  name: "sessions",
  components: {
    UserButton,
    CSVImporter,
    SessionsView,
    NavigationTabs
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
    <v-toolbar app>
      <v-toolbar-title class="ml-0 pl-3">
        <span>MIQA</span>
      </v-toolbar-title>
      <NavigationTabs />
      <v-spacer></v-spacer>
      <UserButton
        @user="girderRest.logout()" />
    </v-toolbar>
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
