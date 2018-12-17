<script>
import { mapState, mapMutations } from "vuex";

export default {
  name: "App",
  computed: {
    ...mapState(["drawer"])
  },
  methods: {
    ...mapMutations(["setDrawer"])
  }
};
</script>

<template>
  <v-app id="app">
    <v-toolbar app>
      <v-toolbar-side-icon @click.stop="setDrawer(!drawer)"></v-toolbar-side-icon>
      <v-toolbar-title class="ml-0 pl-3">
        <span>MIQA</span>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-toolbar-items class="hidden-sm-and-down">
        <v-btn flat>Screenshots</v-btn>
        <v-btn icon>
          <v-icon>person</v-icon>
        </v-btn>
      </v-toolbar-items>
    </v-toolbar>
    <v-content>
      <router-view/>
    </v-content>
  </v-app>
</template>

<style lang="scss">
html {
  overflow-y: auto !important;
}
</style>
