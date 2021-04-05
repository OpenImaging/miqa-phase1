<script>
import { mapActions } from "vuex";

import NavbarTitle from "@/components/NavbarTitle";
import UserButton from "@/components/girder/UserButton";
import NavigationTabs from "@/components/NavigationTabs";

export default {
  name: "GenericNavigationBar",
  components: {
    NavbarTitle,
    UserButton,
    NavigationTabs
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
    <UserButton @user="logout()" />
  </v-app-bar>
</template>
