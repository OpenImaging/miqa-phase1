<script>
import { mapActions } from "vuex";

import UserButton from "@/components/girder/UserButton";
import SessionsView from "../components/SessionsView";

export default {
  name: "sessions",
  components: {
    UserButton,
    SessionsView
  },
  inject: ["girderRest"],
  computed: {},
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
    <v-toolbar app>
      <v-toolbar-title class="ml-0 pl-3">
        <span>MIQA</span>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <UserButton
        @user="girderRest.logout()" />
    </v-toolbar>
    <SessionsView class="mt-2" />
  </div>
</template>

<style lang="scss" scoped>
</style>
