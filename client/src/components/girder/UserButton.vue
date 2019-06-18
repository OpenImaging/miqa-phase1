<script>
export default {
  name: "UserButton",
  inject: ["girderRest"],
  computed: {
    initials() {
      const first = this.girderRest.user.firstName;
      const last = this.girderRest.user.lastName;
      return (
        first.charAt(0).toLocaleUpperCase() + last.charAt(0).toLocaleUpperCase()
      );
    }
  }
};
</script>

<template>
  <v-btn
    v-if="girderRest.user"
    icon
    color="grey lighten-1"
    class="user-avatar-btn"
    @click="$emit('user', girderRest.user)"
  >
    <v-avatar>
      {{ initials }}
    </v-avatar>
  </v-btn>
  <v-btn v-else flat @click="$emit('login')">
    Login
  </v-btn>
</template>

<style lang="scss">
button.user-avatar-btn .v-btn__content {
  height: inherit;
}
</style>
