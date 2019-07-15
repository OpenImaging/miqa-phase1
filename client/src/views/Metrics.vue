<script>
import { mapGetters, mapActions } from "vuex";
import { GChart } from "vue-google-charts";

import GenericNavigationBar from "@/components/GenericNavigationBar";
import iqmMeta from "../utils/iqmMeta";

export default {
  name: "Metrics",
  components: {
    GenericNavigationBar,
    GChart
  },
  data() {
    return {
      chartsReady: false
    };
  },
  computed: {
    iqmMeta: () => iqmMeta,
    ...mapGetters(["allDatasets"]),
    allDatasetWithIQM() {
      if (!this.allDatasets) {
        return [];
      }
      return this.allDatasets.filter(
        dataset => dataset.meta && dataset.meta.iqm
      );
    },
    iqmMetricsTables() {
      if (!this.allDatasetWithIQM.length) {
        return [];
      }
      return this.allDatasetWithIQM[0].meta.iqm.map((metric, index) => {
        var key = Object.keys(metric)[0];
        return {
          key,
          ...this.calculateDataTableArrayAndOptions(
            key,
            this.allDatasetWithIQM.map(
              dataset => Object.values(dataset.meta.iqm[index])[0]
            )
          )
        };
      });
    }
  },
  async created() {
    if (!this.allDatasets || !this.allDatasets.length) {
      this.loadSessions();
    }
  },
  methods: {
    ...mapActions(["loadSessions"]),
    calculateDataTableArrayAndOptions(key, values) {
      var headers = ["Category"];
      var rows = [];
      var options = {
        title: iqmMeta[key].fullname,
        width: "100%",
        height: "300",
        hAxis: {
          baseline: 0,
          baselineColor: "transparent",
          minValue: -1,
          maxValue: undefined,
          ticks: [],
          gridlines: { color: "transparent" }
        },
        legend: "none",
        tooltip: { trigger: "selection" }
      };
      if (!Array.isArray(values[0])) {
        headers.push(key, { type: "string", role: "tooltip" });
        // options.width = '400';
        options.numberOfSeries = 1;
        options.hAxis.maxValue = 4;
        options.hAxis.ticks.push({ v: 0, f: key });
        values.forEach(value => {
          rows.push([
            Math.floor(Math.random() * 12) * 0.05,
            value,
            `${key}: ${value}`
          ]);
        });
      } else {
        let numberOfSubs = values[0].length;
        options.numberOfSeries = numberOfSubs;
        // options.width = 200 + 100 * numberOfSubs;
        options.hAxis.maxValue = numberOfSubs * 2;
        values[0].forEach((subValueObject, i) => {
          var sub = Object.keys(subValueObject)[0];
          headers.push(sub, { type: "string", role: "tooltip" });
          options.hAxis.ticks.push({ v: i * 2, f: `${key}_${sub}` });
        });
        values.forEach(subValueObjects => {
          subValueObjects.forEach((subValueObject, i) => {
            var sub = Object.keys(subValueObject)[0];
            var value = subValueObject[sub];
            var row = [
              Math.floor(Math.random() * 12) * 0.05 + i * 2,
              ...new Array(numberOfSubs * 2).fill(null)
            ];
            row[1 + i * 2] = value;
            row[2 + i * 2] = `${key}_${sub}: ${value}`;
            rows.push(row);
          });
        });
      }
      return {
        values: [headers, ...rows],
        options
      };
    },
    getFlexSize(table) {
      var { numberOfSeries } = table.options;
      var size = Math.round(numberOfSeries * 1.5 + 2);
      size = size > 12 ? 12 : size;
      return size;
    },
    onChartReady(chart, table) {
      this.chartsReady = true;
      chart.setAction({
        id: "sample",
        text: "See dataset",
        action: () => {
          var { row } = chart.getSelection()[0];
          var { numberOfSeries } = table.options;
          var datasetIndex = Math.floor(row / numberOfSeries);
          var dataset = this.allDatasetWithIQM[datasetIndex];
          this.$router.push(dataset._id);
        }
      });
    }
  }
};
</script>

<template>
  <div class="metrics">
    <GenericNavigationBar />
    <v-container grid-list-lg>
      <div class="subheading">
        Metrics
      </div>
      <v-layout wrap>
        <v-flex
          v-for="(table, i) of iqmMetricsTables"
          :key="i"
          v-bind="{ [`lg${getFlexSize(table)}`]: true }"
        >
          <GChart
            type="ScatterChart"
            :data="table.values"
            :options="table.options"
            @ready="onChartReady($event, table)"
          />
          <div
            v-if="chartsReady"
            v-html="iqmMeta[table.key].description"
            style="background-color:white;"
          ></div>
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>
