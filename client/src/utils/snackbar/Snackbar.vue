<template>
  <v-snackbar
    v-model="show"
    :bottom="true"
    :timeout="timeout">
    {{ text }}
    <v-btn
      v-if="callback"
      color="primary"
      flat
      @click="buttonClicked">
      {{ button }}
    </v-btn>
  </v-snackbar>
</template>

<script>
export default {
  name: "Snackbar",
  props: {},
  data: () => ({
    show: false,
    text: "",
    button: "",
    callback: null,
    timeout: 0
  }),
  methods: {
    buttonClicked() {
      this.callback();
      this.show = false;
    }
  }
};
</script>
