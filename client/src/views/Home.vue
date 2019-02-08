<script>
import Layout from "@/components/Layout.vue";

export default {
  name: "home",
  components: {
    Layout
  }
};
</script>

<template>
  <v-content>
    <div class="home">
      <div class="layout">
        <Layout/>
      </div>
      <div class="bottom">
        <v-container fluid grid-list-md>
          <v-layout>
            <v-flex xs6>
              <v-container fluid grid-list-md>
                <v-layout>
                  <v-flex>
                    <div class="subheading">Window setup</div>
                  </v-flex>
                </v-layout>
                <v-layout>
                  <v-flex>
                    <v-slider
                      label="Window"
                      :max="255"
                      :min="0"
                      :step="1"
                      :value="128"
                      hide-details
                    ></v-slider>
                  </v-flex>
                  <v-flex
                    shrink
                    style="width: 60px">
                    <v-text-field
                      class="mt-0"
                      hide-details
                      single-line
                      type="number"
                      :value="255"
                    ></v-text-field>
                  </v-flex>
                </v-layout>
                <v-layout>
                  <v-flex>
                    <v-slider
                      label="Level"
                      :max="255"
                      :min="0"
                      :step="1"
                      :value="150"
                      hide-details
                    ></v-slider>
                  </v-flex>
                  <v-flex
                    shrink
                    style="width: 60px">
                    <v-text-field
                      class="mt-0"
                      hide-details
                      single-line
                      type="number"
                      :value="128"
                    ></v-text-field>
                  </v-flex>
                </v-layout>
              </v-container>
            </v-flex>
            <v-flex xs6>
              <v-container fluid grid-list-sm>
                <v-layout>
                  <v-flex>
                    <v-textarea solo label="Add note" rows="4" hide-details></v-textarea>
                  </v-flex>
                </v-layout>
                <v-layout>
                  <v-flex xs5>
                    <v-text-field
                      class="small"
                      label="Reviewer name"
                      solo
                      hide-details></v-text-field>
                  </v-flex>
                  <v-flex xs7>
                    <v-btn-toggle mandatory class="buttons">
                      <v-btn flat value="good">Good</v-btn>
                      <v-btn flat value="bad">Bad</v-btn>
                      <v-btn flat value="unsure">Unsure</v-btn>
                    </v-btn-toggle>
                  </v-flex>
                </v-layout>
                <v-layout align-center justify-space-between>
                  <v-flex>
                      <v-btn fab small class="primary--text elevation-2">
                        <v-icon>keyboard_arrow_left</v-icon>
                      </v-btn>
                      <v-btn flat>
                        Previous Scan
                      </v-btn>
                  </v-flex>
                  <v-flex>
                    <v-btn
                      color="primary">
                      Save
                      <v-icon right>save</v-icon>
                    </v-btn>
                  </v-flex>
                  <v-flex>
                      <v-btn flat>
                        Next Scan
                      </v-btn>
                      <v-btn fab small class="primary--text elevation-2">
                        <v-icon>keyboard_arrow_right</v-icon>
                      </v-btn>
                  </v-flex>
                </v-layout>
              </v-container>
            </v-flex>
          </v-layout>
        </v-container>
      </div>
    </div>
  </v-content>
</template>

<style lang="scss" scoped>
.home {
  display: flex;
  flex-direction: column;
  height: 100%;

  .layout {
    flex: 1 0 auto;
    position: relative;
  }

  .bottom {
    > .container {
      position: relative;

      &::before {
        content: ' ';
        position: absolute;
        top: 1px;
        bottom: 0;
        left: 0;
        right: 50%;
        background: white;
      }
    }

    .buttons {
      width: 100%;
      height: 40px;

      .v-btn {
        height: 100%;
        width: 33.333%;
      }
    }
  }
}
</style>

<style lang="scss">
.v-text-field.small .v-input__control {
  min-height: 40px !important;
}
</style>

