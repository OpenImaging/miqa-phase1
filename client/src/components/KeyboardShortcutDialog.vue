<script>
export default {
  name: "KeyboardShortcutDialog",
  props: {
    value: {
      type: Boolean,
      required: true
    }
  },
  data: () => ({
    shortcuts: [
      ["Next dataset", "right arrow"],
      ["Previous dataset", "left arrow"],
      ["Change slices", "q / w, a / s, z / x"],
      ["Increase/decrease window", "= / -"],
      ["Increase/decrease window level", "[ / ]"],
      ["Focus to note", "n"],
      ["Show note history", "h"],
      ["Unfocus from note", "esc"],
      ["Mark as bad/good/usable extra", "b / g / e"],
      ["Save", "alt + s"],
      ["Save on confirm dialog", "y"],
      ["Don't save on confirm dialog", "n"],
      ["Cancel on confirm dialog", "esc"]
    ]
  })
};
</script>

<template>
  <v-dialog
    :value="value"
    @input="$emit('input', $event)"
    max-width="500"
    scrollable
  >
    <v-card>
      <v-card-title class="title" primary-title
        >Keyboard shortcuts
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text style="height: 500px;">
        <v-data-table :items="shortcuts" hide-actions hide-headers>
          <template #items="{ item }">
            <td>{{ item[0] }}</td>
            <td>{{ item[1] }}</td>
          </template>
        </v-data-table>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" flat @click="$emit('input', false)">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
