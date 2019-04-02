<script>
import { mapState, mapMutations } from "vuex";

import { GIRDER_URL } from "../constants";

export default {
  name: "NavigationTabs",
  inject: ["girderRest"],
  data: () => ({
    GIRDER_URL
  }),
  computed: {
    ...mapState(["currentDatasetId"])
  },
  methods: {
    ...mapMutations(["setDrawer"]),
    datasetTabClick() {
      this.setDrawer(true);
    }
  }
};
</script>

<template>
  <v-tabs class="navigation-tabs ml-3" color="transparent">
    <v-tab
      :to="`/${currentDatasetId ? currentDatasetId : ''}`"
      @click="datasetTabClick"
    >
      <v-icon>view_column</v-icon>
      Sessions
    </v-tab>
    <v-tab to="/settings" v-if="girderRest.user && girderRest.user.admin">
      <v-icon>settings</v-icon>
      Settings
    </v-tab>
    <v-tab
      v-if="girderRest.user && girderRest.user.admin"
      :href="GIRDER_URL"
      target="_blank"
    >
      <v-icon>open_in_new</v-icon>
      Girder
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
