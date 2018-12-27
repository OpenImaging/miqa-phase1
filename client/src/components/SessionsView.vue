<script>
import { mapState, mapActions } from "vuex";

export default {
  name: "sessions-view",
  components: {},
  computed: {
    ...mapState(["sessionTree", "currentDatasetId"])
  },
  methods: {}
};
</script>

<template>
  <div class="sessions-view">
    <ul>
      <li v-for="(batch) of sessionTree" :key="batch.folderId">
        {{batch.name}}
        <ul>
          <li v-for="(session) of batch.sessions" :key="session.folderId">
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
