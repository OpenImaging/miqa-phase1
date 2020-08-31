<script>
export default {
  name: "App",
  components: {},
  inject: ["girderRest"],
  provide() {
    return { userLevel: this.userLevel };
  },
  data: () => ({
    userLevel: { value: null }
  }),
  watch: {
    "girderRest.user"(user) {
      if (!user) {
        this.$router.push("/login");
      } else {
        this.setUserLevel();
      }
    }
  },
  created() {
    this.setUserLevel();
  },
  methods: {
    async setUserLevel() {
      if (!this.girderRest.user) {
        return;
      }
      this.userLevel.value = await this.getUserLevel();
    },
    async getUserLevel() {
      if (this.girderRest.user.admin) {
        return 0;
      }
      var roles = await Promise.all(
        this.girderRest.user.groups.map(async id => {
          var { data: group } = await this.girderRest.get(`group/${id}`);
          return group.name.toLowerCase();
        })
      );
      if (roles.indexOf("manager") !== -1) {
        return 1;
      }
      if (roles.indexOf("reviewer") !== -1) {
        return 2;
      }
      if (roles.indexOf("collaborator") !== -1) {
        return 3;
      }
      return null;
    }
  }
};
</script>

<template>
  <v-app id="app">
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<style lang="scss">
html {
  overflow-y: auto !important;
}
</style>
