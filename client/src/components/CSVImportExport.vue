<script>
import { mapActions } from "vuex";

export default {
  name: "CSVImportExport",
  components: {},
  inject: ["girderRest"],
  data: () => ({
    importEnabled: false,
    exportEnabled: false,
    importing: false,
    importDialog: false
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
    async importCSV() {
      this.importing = true;
      try {
        var { data: result } = await this.girderRest.post("miqa/csv/import");
        this.importing = false;
        this.$snackbar({
          text: `Import finished.
          With ${result.success} rows succeeded and ${result.failed} failed.`,
          timeout: 6000
        });
        this.loadSessions();
      } catch (ex) {
        this.importing = false;
        this.$snackbar({
          text: "Import failed. Refer console for detail."
        });
        console.error(ex.response);
      }
      this.importDialog = false;
    },
    async exportCSV() {
      await this.girderRest.get("miqa/csv/export");
      this.$prompt({
        title: "Export",
        text: "Saved data to csv file successfully.",
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
    <v-btn text color="primary" @click="exportCSV" :disabled="!exportEnabled"
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
          <v-btn text color="primary" @click="importCSV" :loading="importing"
            >Import</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style lang="scss" scoped></style>
