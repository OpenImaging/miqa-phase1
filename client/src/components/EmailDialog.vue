<script>
import { mapState, mapGetters, mapMutations } from "vuex";

export default {
  name: "EmailDialog",
  inject: ["girderRest"],
  props: {
    value: {
      type: Boolean,
      required: true
    }
  },
  data: () => ({
    to: "",
    subject: "",
    body: "",
    selectedScreenshots: [],
    valid: true,
    subjectRules: [v => !!v || "Subject is required"],
    toRules: [
      v => !!v || "To is required",
      v => /.+@.+/.test(v) || "Must be valid email address"
    ]
  }),
  computed: {
    ...mapState(["screenshots"]),
    ...mapGetters(["currentDataset"])
  },
  watch: {
    currentDataset(value) {
      if (value) {
        this.initialize();
      }
    }
  },
  methods: {
    ...mapMutations([]),
    initialize() {
      if (this.$refs.form) {
        this.$refs.form.reset();
      }
      this.selectedScreenshots = [];
      this.body = `Hi,

Regarding ${location.href}

`;
    },
    toggleScreenshotSelection(screenshot) {
      let index;
      if ((index = this.selectedScreenshots.indexOf(screenshot)) === -1) {
        this.selectedScreenshots.push(screenshot);
      } else {
        this.selectedScreenshots.splice(index, 1);
      }
    },
    async send() {
      if (!this.$refs.form.validate()) {
        return;
      }
      await this.girderRest.post(`miqa_email`, {
        to: this.to,
        subject: this.subject,
        body: this.body,
        screenshots: this.screenshots.filter(
          screenshot => this.selectedScreenshots.indexOf(screenshot) !== -1
        )
      });
    },
    close() {}
  }
};
</script>

<template>
  <v-dialog
    :value="value"
    @input="$emit('input', $event)"
    lazy
    max-width="60%">
    <v-form @submit.prevent="send" ref="form">
      <v-card>
        <v-card-title
          class="headline grey lighten-4">
          Send email
          <v-spacer />
          <v-btn small icon class="ma-0" @click="$emit('input', false)">
            <v-icon>close</v-icon>
          </v-btn>
        </v-card-title>
        <v-container grid-list-sm class="py-0">
          <v-layout>
            <v-flex>
              <v-text-field
                v-model="to"
                label="To"
                placeholder=" "
                name="miqa_email"
                type="email"
                browser-autocomplete="on"
                :rules="toRules"
                required
              />
            </v-flex>
          </v-layout>
          <v-layout>
            <v-flex>
              <v-text-field
                v-model="subject"
                label="Subject"
                placeholder=" "
                name="miqa_subject"
                browser-autocomplete="on"
                :rules="subjectRules"
                required
              />
            </v-flex>
          </v-layout>
          <v-layout>
            <v-flex>
              <v-textarea label="Body" rows="6"
                v-model="body"></v-textarea>
            </v-flex>
          </v-layout>
          <template v-if="screenshots.length">
            <div class="caption">Include screenshots</div>
            <v-layout class="screenshot-row" d-block>
              <v-flex d-inline-block v-for="(screenshot, index) of screenshots" :key="index">
                <v-card class="screenshot"
                  @click="toggleScreenshotSelection(screenshot)"
                  :style="{ borderColor: selectedScreenshots.indexOf(screenshot) === -1?'transparent': $vuetify.theme.primary }">
                  <v-img
                    :src="screenshot.dataURL"
                    aspect-ratio="1"></v-img>
                  <v-card-text class="text-truncate">
                    <v-tooltip top>
                      <span slot="activator">{{screenshot.name}}</span>
                      <span>{{screenshot.name}}</span>
                    </v-tooltip>
                  </v-card-text>
                </v-card>
              </v-flex>
            </v-layout>
          </template>
        </v-container>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            flat
            type="submit">
            Send
          </v-btn>
        </v-card-actions>
    </v-card>
    </v-form>
  </v-dialog>
</template>

<style lang="scss" scoped>
.caption {
  color: rgba(0, 0, 0, 0.54);
}

.screenshot-row {
  overflow-x: auto;

  .screenshot {
    width: 160px;
    border: 2px solid transparent;
  }
}
</style>
