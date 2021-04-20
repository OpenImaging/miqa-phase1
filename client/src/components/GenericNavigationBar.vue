<script>
import { mapActions } from "vuex";

import NavbarTitle from "@/components/NavbarTitle";
import UserButton from "@/components/girder/UserButton";
import NavigationTabs from "@/components/NavigationTabs";
import SessionTimer from "@/components/SessionTimer";

export default {
  name: "GenericNavigationBar",
  components: {
    NavbarTitle,
    UserButton,
    NavigationTabs,
    SessionTimer
  },
  inject: ["girderRest"],
  methods: {
    ...mapActions(["logout"])
  }
};
</script>

<template>
  <v-app-bar app dense>
    <NavbarTitle />
    <NavigationTabs />
    <v-spacer></v-spacer>
    <SessionTimer />
    <UserButton @user="logout()" />
  </v-app-bar>
</template>
