<script>
import UserButton from "@/components/girder/UserButton";
import NavigationTabs from "@/components/NavigationTabs";

export default {
  name: "GenericNavigationBar",
  components: {
    UserButton,
    NavigationTabs
  },
  inject: ["girderRest"]
};
</script>

<template>
  <v-toolbar app dense>
    <v-toolbar-title>
      <span>MIQA</span>
    </v-toolbar-title>
    <NavigationTabs />
    <v-spacer></v-spacer>
    <UserButton @user="girderRest.logout()" />
  </v-toolbar>
</template>
