<script>
import { mapActions } from "vuex";
import { GirderAuthentication } from "@girder/components/src";

export default {
  name: "Login",
  components: {
    GirderAuthentication
  },
  inject: ["girderRest"],
  data() {
    return {
      form: "login",
      userDialog: true
    };
  },
  methods: {
    ...mapActions(["startSessionTimer"])
  },
  watch: {
    "girderRest.user"(user) {
      if (user) {
        this.$router.push("/");
        this.startSessionTimer();
      }
    }
  }
};
</script>

<template>
  <v-container>
    <v-dialog :value="userDialog" persistent max-width="500px">
      <GirderAuthentication :register="true" />
    </v-dialog>
  </v-container>
</template>
