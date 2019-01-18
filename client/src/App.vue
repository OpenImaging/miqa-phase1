<script>
export default {
  name: "App",
  components: {},
  inject: ["girderRest"],
  computed: {},
  watch: {
    "girderRest.user"(user) {
      if (!user) {
        this.$router.push("/login");
      }
    }
  },
  methods: {}
};
</script>

<template>
  <v-app id="app">
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
