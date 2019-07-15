<script>
import iqmMeta from "../utils/iqmMeta";

export default {
  name: "MetricsDisplay",
  props: {
    iqm: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      selectedMetric: Object.keys(iqmMeta)[0]
    };
  },
  computed: {
    iqmMeta: () => iqmMeta,
    selectItems() {
      return this.iqm.map(metric => {
        var key = Object.keys(metric)[0];
        return {
          value: key,
          text: iqmMeta[key].display
        };
      });
    },
    values() {
      if (!this.selectedMetric) {
        return [];
      }
      var metric = this.iqm.find(metric => metric[this.selectedMetric]);
      var value = metric[this.selectedMetric];
      if (!Array.isArray(value)) {
        return [
          {
            key: this.selectedMetric,
            value
          }
        ];
      } else {
        return value.map(subValueObject => {
          var sub = Object.keys(subValueObject)[0];
          return {
            key: sub,
            value: subValueObject[sub]
          };
        });
      }
    }
  }
};
</script>

<template>
  <v-card width="400">
    <v-card-title>
      Metrics
    </v-card-title>
    <v-card-text class="pt-0">
      <v-container fluid class="pa-0" grid-list-md>
        <v-layout>
          <v-flex style="width: 250px;" shrink>
            <v-select
              v-model="selectedMetric"
              :items="selectItems"
              :hint="iqmMeta[selectedMetric].fullname"
              persistent-hint
            />
          </v-flex>
        </v-layout>
        <v-layout>
          <v-flex>
            <ul>
              <li v-for="({ key, value }, i) of values" :key="i">
                {{ key }}: {{ value }}
              </li>
            </ul>
          </v-flex>
        </v-layout>
        <v-layout v-if="selectedMetric">
          <v-flex v-html="iqmMeta[selectedMetric].description"> </v-flex>
        </v-layout>
      </v-container>
    </v-card-text>
  </v-card>
</template>
