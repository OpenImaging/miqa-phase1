<script>
export default {
  name: "JSONConfig",
  inject: ["girderRest"],
  data: () => ({
    importpath: "",
    exportpath: "",
    changed: false,
    importpathError: "",
    exportpathError: ""
  }),
  async created() {
    var { data: result } = await this.girderRest.get("miqa_setting/datapath");
    this.importpath = result.importpath;
    this.exportpath = result.exportpath;
  },
  methods: {
    async save() {
      if (!this.$refs.form.validate()) {
        return;
      }
      try {
        await this.girderRest.post("miqa_setting/datapath", {
          importpath: this.importpath,
          exportpath: this.exportpath
        });
        this.changed = false;
      } catch (e) {
        var message = e.response.data.message;
        if (message.includes("import")) {
          this.importpathError = message;
        } else {
          this.exportpathError = message;
        }
        setTimeout(() => {
          this.importpathError = "";
          this.exportpathError = "";
        }, 3000);
      }
    }
  }
};
</script>

<template>
  <v-form ref="form" @submit.prevent="save">
    <v-layout wrap>
      <v-flex lg6 sm8 xs12>
        <v-text-field
          label="Import path"
          placeholder=" "
          v-model="importpath"
          @input="changed = true"
          autocomplete="on"
          name="miqa-json-importpath"
          :rules="[
            v => !!v || 'path is required',
            v =>
              v.endsWith('.json') ||
              v.endsWith('.csv') ||
              'Needs to be a json or csv file'
          ]"
          :error-messages="importpathError"
      /></v-flex>
      <v-flex lg6 sm8 xs12>
        <v-text-field
          label="Export path"
          placeholder=" "
          v-model="exportpath"
          @input="changed = true"
          autocomplete="on"
          name="miqa-json-exportpath"
          :rules="[
            v => !!v || 'path is required',
            v =>
              v.endsWith('.json') ||
              v.endsWith('.csv') ||
              'Needs to be a json file'
          ]"
          :error-messages="exportpathError"
      /></v-flex>
    </v-layout>
    <v-layout>
      <v-flex>
        <v-btn type="submit" color="primary" class="mx-0" :disabled="!changed">
          Save
        </v-btn>
      </v-flex>
    </v-layout>
  </v-form>
</template>

<style lang="scss" scoped></style>
