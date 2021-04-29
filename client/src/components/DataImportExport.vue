<script>
import { mapActions } from "vuex";

export default {
  name: "DataImportExport",
  components: {},
  inject: ["girderRest"],
  data: () => ({
    importEnabled: false,
    exportEnabled: false,
    importing: false,
    importDialog: false,
    importErrorText: "",
    importErrors: false
  }),
  async created() {
    var { data: result } = await this.girderRest.get(
      "miqa_setting/import-export-enabled"
    );
    this.importEnabled = result.import;
    this.exportEnabled = result.export;
  },
  methods: {
    ...mapActions(["loadSessions"]),
    async importData() {
      this.importing = true;
      this.importErrorText = "";
      this.importErrors = false;
      try {
        var { data: result } = await this.girderRest.post("miqa/data/import");
        this.importing = false;
        if (result.errorMsg) {
          this.importErrorText = `${result.success} scans succeeded, ${result.failed} failed.\n\n${result.errorMsg}`;
          this.importErrors = true;
        } else {
          this.$snackbar({
            text: `Import finished.
            With ${result.success} scans succeeded and ${result.failed} failed.`,
            timeout: 6000
          });
        }
        this.loadSessions();
      } catch (ex) {
        this.importing = false;
        this.$snackbar({
          text: "Import failed. Refer to server logs for details."
        });
        console.error(ex.response);
      }
      this.importDialog = false;
    },
    async exportData() {
      await this.girderRest.get("miqa/data/export");
      this.$prompt({
        title: "Export",
        text: "Saved data to file successfully.",
        positiveButton: "Ok"
      });
    }
  }
};
</script>

<template>
  <div>
    <v-btn
      text
      color="primary"
      @click="importDialog = true"
      :disabled="!importEnabled"
      >Import</v-btn
    >
    <v-btn text color="primary" @click="exportData" :disabled="!exportEnabled"
      >Export</v-btn
    >
    <v-dialog v-model="importDialog" width="500" :persistent="importing">
      <v-card>
        <v-card-title class="title">
          Import
        </v-card-title>
        <v-card-text>
          Import data would delete outdated records from the system, do you want
          to continue?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="importDialog = false" :disabled="importing"
            >Cancel</v-btn
          >
          <v-btn text color="primary" @click="importData" :loading="importing"
            >Import</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="importErrors" content-class="import-error-dialog">
      <v-card>
        <v-card-title class="title">Import Errors Encountered</v-card-title>
        <v-card-text class="console-format">
          {{ importErrorText }}
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="importErrors = false">
            Ok
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style lang="scss">
.import-error-dialog {
  position: relative;
  width: 100%;
  margin: 48px;
}
.console-format {
  white-space: pre-wrap;
  font-family: monospace;
}
</style>
