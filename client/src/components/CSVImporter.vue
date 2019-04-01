<script>
import { mapActions } from "vuex";

import FileSelector from "./FileSelector";

export default {
  name: "CSVImporter",
  components: {
    FileSelector
  },
  inject: ["girderRest"],
  data: () => ({
    csvFile: null,
    csvFilename: "",
    importing: false
  }),
  methods: {
    importCSV() {
      if (!this.csvFile) {
        return;
      }
      var reader = new FileReader();
      reader.onload = async e => {
        this.importing = true;
        try {
          var { data: result } = await this.girderRest.post(
            `miqa/csv?filename=${this.csvFilename}`,
            e.target.result,
            {
              headers: {
                "Content-Type": "text/csv"
              }
            }
          );
          this.importing = false;
          this.$snackbar({
            text: `Import finished. 
          With ${result.success} rows succeeded and ${result.failed} failed.`,
            timeout: 6000
          });
        } catch (ex) {
          this.importing = false;
          this.$snackbar({
            text: "Import failed. Refer console for detail."
          });
          console.error(ex.response);
        }
      };
      reader.readAsText(this.csvFile);
    }
  }
};
</script>

<template>
  <v-flex align-center class="csv-row">
    <FileSelector
      class="file-selector"
      label="CSV file"
      accept=".csv"
      v-model="csvFilename"
      @file="csvFile = $event"
    />
    <v-btn color="primary" @click="importCSV" :loading="importing"
      >Import</v-btn
    >
  </v-flex>
</template>

<style lang="scss" scoped>
.csv-row {
  display: flex;

  .file-selector {
    flex-grow: 1;
  }
}
</style>
