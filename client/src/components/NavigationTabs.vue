<script>
import { mapState } from "vuex";

import { GIRDER_URL } from "../constants";

export default {
  name: "NavigationTabs",
  data: () => ({
    GIRDER_URL
  }),
  computed: {
    ...mapState(["currentDatasetId"])
  }
};
</script>

<template>
  <v-tabs
    class="navigation-tabs ml-3"
    icons-and-text
    :height='64'
    color="transparent">
      <v-tab
        :to="`/${currentDatasetId?currentDatasetId:''}`">
        Dataset
        <v-icon>explore</v-icon>
      </v-tab>
      <v-tab
        to="/sessions">
        batch
        <v-icon>list</v-icon>
      </v-tab>
      <v-tab
        :href="GIRDER_URL"
        target="_blank">
        Girder
        <v-icon>open_in_new</v-icon>
      </v-tab>
  </v-tabs>
</template>

<style lang="scss">
.v-toolbar .navigation-tabs.v-tabs {
  width: unset;

  .v-tabs__container--icons-and-text .v-tabs__div {
    min-width: 120px;
  }
}
</style>
