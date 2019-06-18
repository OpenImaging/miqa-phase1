<script>
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
  inject: ["girderRest"]
};
</script>

<template>
  <v-toolbar app dense>
    <NavbarTitle />
    <NavigationTabs />
    <v-spacer></v-spacer>
    <UserButton @user="girderRest.logout()" />
  </v-toolbar>
</template>
