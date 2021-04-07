<script>
import { mapActions, mapMutations } from "vuex";
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
    ...mapActions(["startLoginMonitor", "logout"]),
    ...mapMutations(["setResponseInterceptor"])
  },
  watch: {
    "girderRest.user"(user) {
      if (user) {
        this.$router.push("/");
        this.startLoginMonitor();
        const self = this;
        const interceptor = this.girderRest.interceptors.response.use(
          response => response,
          error => {
            if (error.response.status === 401) {
              self
                .$prompt({
                  title: "Session Expired",
                  text: "Your session has expired and you will be logged out",
                  positiveButton: "Ok"
                })
                .then(() => {
                  self.logout();
                });
            } else {
              return Promise.reject(error);
            }
          }
        );
        this.setResponseInterceptor(interceptor);
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
