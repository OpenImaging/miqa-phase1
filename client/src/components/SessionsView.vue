<script>
import { mapState } from "vuex";
import { API_URL } from "../constants";

export default {
  name: "sessions-view",
  components: {},
  props: {
    minimal: {
      type: Boolean,
      default: false
    }
  },
  data: () => ({ API_URL }),
  computed: {
    ...mapState(["sessionTree", "currentDatasetId"])
  },
  methods: {}
};
</script>

<template>
  <div class="sessions-view">
    <ul>
      <li v-for="(batch) of sessionTree" class="body-2" :key="batch.folderId">
        {{batch.name}}
        <v-btn v-if="!minimal" flat icon small
          :href='`${API_URL}/result/${batch.folderId}`'>
          <v-icon>attachment</v-icon>
        </v-btn>
        <ul>
          <li v-for="(session) of batch.sessions" class="body-1" :key="session.folderId">
            {{session.name}}
            <ul>
              <li v-for="(dataset) of session.datasets" :key="dataset._id" :class="{current:dataset._id===currentDatasetId}">
                <v-btn href flat small :to="dataset._id" active-class="">{{dataset.name}}</v-btn>
              </li>
            </ul>
          </li>
        </ul>
      </li>
    </ul>
  </div>
</template>

<style lang="scss" scoped>
.current {
  background: rgb(206, 206, 206);
}
</style>
