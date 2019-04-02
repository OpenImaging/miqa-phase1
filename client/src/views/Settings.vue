<script>
// import { mapState, mapActions } from "vuex";

import GenericNavigationBar from "@/components/GenericNavigationBar";
import CSVConfig from "@/components/CSVConfig";
import SiteConfig from "@/components/SiteConfig";

export default {
  name: "Settings",
  components: {
    GenericNavigationBar,
    CSVConfig,
    SiteConfig
  },
  inject: ["girderRest"],
  computed: {},
  created() {},
  methods: {}
};
</script>

<template>
  <div class="sites">
    <GenericNavigationBar />
    <v-container grid-list-md>
      <div class="subheading">
        CSV path
      </div>
      <v-layout>
        <v-flex>
          <CSVConfig />
        </v-flex>
      </v-layout>
      <div class="subheading mt-4">
        Sites
      </div>
      <v-layout justify-center>
        <v-flex>
          <SiteConfig />
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<style lang="scss" scoped></style>
