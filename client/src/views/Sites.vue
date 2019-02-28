<script>
import { mapState, mapActions } from "vuex";

import GenericNavigationBar from "@/components/GenericNavigationBar";
import SiteTableContactCell from "@/components/SiteTableContactCell";
import SiteTableDisplayNameCell from "@/components/SiteTableDisplayNameCell";

export default {
  name: "Sites",
  components: {
    GenericNavigationBar,
    SiteTableContactCell,
    SiteTableDisplayNameCell
  },
  inject: ["girderRest"],
  computed: {
    ...mapState(["sites"]),
    headers: () => [
      { text: "Site", value: "name" },
      { text: "Display Name", value: "displayName" },
      { text: "PI", value: "pi" },
      { text: "MRI Physicist", value: "mriPhysicist" },
      { text: "Technician", value: "technician" },
      { text: "lead RA", value: "leadRA" }
    ],
    items() {
      if (!this.sites) {
        return [];
      }
      return this.sites.map(site => ({
        site,
        name: site.name,
        displayName: site.meta ? site.meta.displayName : null,
        pi: site.meta ? site.meta.pi : [],
        mriPhysicist: site.meta ? site.meta.mriPhysicist : [],
        technician: site.meta ? site.meta.technician : [],
        leadRA: site.meta ? site.meta.leadRA : []
      }));
    }
  },
  created() {
    this.loadSites();
  },
  methods: {
    ...mapActions(["loadSites"]),
    async update(site, field, value) {
      if (!site.meta) {
        this.$set(site, "meta", {});
      }
      this.$set(site.meta, field, value);
      await this.girderRest.put(`item/${site._id}/metadata`, site.meta);
    }
  }
};
</script>

<template>
  <div class="sites">
    <GenericNavigationBar />
    <v-container>
      <v-layout justify-center>
        <v-flex>
          <v-data-table :headers="headers" :items="items" hide-actions>
            <template slot="items" slot-scope="{ item }">
              <td>{{ item.name }}</td>
              <SiteTableDisplayNameCell
                :value="item.displayName"
                @input="update(item.site, 'displayName', $event)"
              />
              <SiteTableContactCell
                :value="item.pi"
                @input="update(item.site, 'pi', $event)"
              />
              <SiteTableContactCell
                :value="item.mriPhysicist"
                @input="update(item.site, 'mriPhysicist', $event)"
              />
              <SiteTableContactCell
                :value="item.technician"
                @input="update(item.site, 'technician', $event)"
              />
              <SiteTableContactCell
                :value="item.leadRA"
                @input="update(item.site, 'leadRA', $event)"
              />
            </template>
          </v-data-table>
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<style lang="scss" scoped>
</style>
