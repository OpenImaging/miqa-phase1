<script>
import _ from "lodash";
import { mapState, mapGetters, mapMutations } from "vuex";

import EmailRecipientCombobox from "./EmailRecipientCombobox";

export default {
  name: "EmailDialog",
  components: {
    EmailRecipientCombobox
  },
  inject: ["girderRest"],
  props: {
    value: {
      type: Boolean,
      required: true
    },
    note: {
      type: String,
      default: ""
    }
  },
  data: () => ({
    initialized: false,
    to: [],
    cc: [],
    bcc: [],
    toCandidates: [],
    ccCandidates: [],
    bccCandidates: [],
    showCC: false,
    showBCC: false,
    subject: "",
    body: "",
    selectedScreenshots: [],
    valid: true,
    sending: false
  }),
  computed: {
    ...mapState(["screenshots"]),
    ...mapGetters(["currentDataset", "currentSession", "siteMap"])
  },
  watch: {
    currentDataset(value) {
      if (value) {
        this.initialize();
      }
    },
    value(value) {
      if (value && !this.initialized) {
        this.initialize();
      }
    },
    note(value) {
      if (value) {
        this.initialize();
      }
    }
  },
  methods: {
    ...mapMutations(["removeScreenshot"]),
    initialize() {
      if (this.$refs.form) {
        this.$refs.form.resetValidation();
      }
      if (!this.currentSession) {
        return;
      }
      this.selectedScreenshots = [];
      this.toCandidates = [];
      this.ccCandidates = [];
      this.bccCandidates = [];
      var site = this.siteMap[this.currentSession.meta.site];
      if (site && site.meta) {
        for (let key in site.meta) {
          if (_.isArray(site.meta[key])) {
            for (let contact of site.meta[key]) {
              switch (contact.mode) {
                case "to":
                  this.toCandidates.push(contact);
                  break;
                case "cc":
                  this.ccCandidates.push(contact);
                  break;
                case "bcc":
                  this.bccCandidates.push(contact);
                  break;
              }
            }
          }
        }
      }
      this.to = this.toCandidates.map(c => c.name);
      this.cc = this.ccCandidates.map(c => c.name);
      this.bcc = this.bccCandidates.map(c => c.name);
      this.showCC = !!this.cc.length;
      this.showBCC = !!this.bcc.length;
      var experiment = `Regarding ${this.currentSession.meta.experimentId} (${
        this.currentSession.meta.experimentId2
      }), ${this.currentSession.name}`;
      this.subject = experiment;
      this.body = `${experiment}

${location.href}

${this.note}
`;
      this.initialized = true;
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
      var toAddresses = this.to.map(recipient => {
        var candidate = this.toCandidates.find(c => c.name === recipient);
        return candidate ? candidate.email : recipient;
      });
      var ccAddresses = this.cc.map(recipient => {
        var candidate = this.ccCandidates.find(c => c.name === recipient);
        return candidate ? candidate.email : recipient;
      });
      var bccAddresses = this.bcc.map(recipient => {
        var candidate = this.bccCandidates.find(c => c.name === recipient);
        return candidate ? candidate.email : recipient;
      });
      this.sending = true;
      await this.girderRest.post(`miqa_email`, {
        to: toAddresses,
        cc: ccAddresses,
        bcc: bccAddresses,
        subject: this.subject,
        body: this.body,
        screenshots: this.screenshots.filter(
          screenshot => this.selectedScreenshots.indexOf(screenshot) !== -1
        )
      });
      this.sending = false;
      this.$emit("input", false);
      this.initialized = false;
    }
  }
};
</script>

<template>
  <v-dialog :value="value" @input="$emit('input', $event)" max-width="60%">
    <v-form @submit.prevent="send" ref="form">
      <v-card>
        <v-card-title class="headline grey lighten-4">
          Send email
          <v-spacer />
          <v-btn small icon class="ma-0" @click="$emit('input', false)">
            <v-icon>close</v-icon>
          </v-btn>
        </v-card-title>
        <v-container grid-list-sm class="py-0">
          <v-layout align-center>
            <v-flex>
              <EmailRecipientCombobox
                label="to"
                v-model="to"
                :candidates="toCandidates.map(c => c.name)"
                :required="!(to.length + cc.length + bcc.length)"
              />
            </v-flex>
            <v-flex shrink>
              <a class="px-2" v-if="!showCC" @click="showCC = true">cc</a>
              <a class="px-2" v-if="!showBCC" @click="showBCC = true">bcc</a>
            </v-flex>
          </v-layout>
          <v-layout v-if="showCC">
            <v-flex>
              <EmailRecipientCombobox
                label="cc"
                v-model="cc"
                :candidates="ccCandidates.map(c => c.name)"
                :required="!(to.length + cc.length + bcc.length)"
              />
            </v-flex>
          </v-layout>
          <v-layout v-if="showBCC">
            <v-flex>
              <EmailRecipientCombobox
                label="bcc"
                v-model="bcc"
                :candidates="bccCandidates.map(c => c.name)"
                :required="!(to.length + cc.length + bcc.length)"
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
                :rules="[v => !!v || 'Subject is required']"
                required
              />
            </v-flex>
          </v-layout>
          <v-layout>
            <v-flex>
              <v-textarea label="Body" rows="8" v-model="body"></v-textarea>
            </v-flex>
          </v-layout>
          <template v-if="screenshots.length">
            <div class="caption">Include screenshots</div>
            <v-layout class="screenshot-row">
              <v-flex
                v-for="(screenshot, index) of screenshots"
                :key="index"
                shrink
              >
                <v-hover #default="{ hover }">
                  <v-card
                    class="screenshot"
                    @click="toggleScreenshotSelection(screenshot)"
                    :style="{
                      borderColor:
                        selectedScreenshots.indexOf(screenshot) === -1
                          ? 'transparent'
                          : $vuetify.theme.primary
                    }"
                  >
                    <v-img :src="screenshot.dataURL" aspect-ratio="1"></v-img>
                    <v-card-text class="text-truncate">
                      <v-tooltip top>
                        <span slot="activator">{{ screenshot.name }}</span>
                        <span>{{ screenshot.name }}</span>
                      </v-tooltip>
                    </v-card-text>
                    <v-fade-transition>
                      <v-btn
                        v-if="hover"
                        @click.stop="removeScreenshot(screenshot)"
                        fab
                        small
                        color="primary"
                        class="close"
                      >
                        <v-icon>close</v-icon>
                      </v-btn>
                    </v-fade-transition>
                  </v-card>
                </v-hover>
              </v-flex>
            </v-layout>
          </template>
        </v-container>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" flat :loading="sending" type="submit">
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

    .v-btn.close {
      height: 25px;
      width: 25px;
      position: absolute;
      top: 0;
      right: 0;

      .v-icon {
        font-size: 14px;
      }
    }
  }
}
</style>
