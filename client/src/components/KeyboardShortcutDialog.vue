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
      ["Next dataset", "<code>→</code>"],
      ["Previous dataset", "<code>←</code>"],
      [
        "Change slices",
        "<code>q</code> / <code>w</code>, <code>a</code> / <code>s</code>, <code>z</code> / <code>x</code>"
      ],
      ["Toggle fullscreen", "<code>e</code> / <code>d</code> / <code>c</code>"],
      ["Zooming", "<code>right button + dragging</code>"],
      ["Panning", "<code>shift + dragging</code>"],
      ["Cancel on confirm dialog", "<code>esc</code>"],
      ["Increase/decrease window", "<code>=</code> / <code>-</code>"],
      ["Increase/decrease window level", "<code>[</code> / <code>]</code>"],
      ["Focus to note", "<code>n</code>"],
      ["Show note history", "<code>h</code>"],
      ["Unfocus from note", "<code>esc</<code>"],
      [
        "Mark as bad/good/usable extra",
        "<code>b</code> / <code>g</code> / <code>u</code>"
      ],
      ["Save", "<code>alt + s</code>"],
      ["Save on confirm dialog", "<code>y</code>"],
      ["Don't save on confirm dialog", "<code>n</code>"],
      ["Cancel on confirm dialog", "<code>esc</code>"]
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
        <v-data-table :items="shortcuts" hide-default-footer hide-default-header>
          <template v-slot:body="{ items }">
            <tbody>
              <tr v-for="item in items" :key="item[0]">
                <td>{{ item[0] }}</td>
                <td v-html="item[1]"></td>
              </tr>
            </tbody>
          </template>
        </v-data-table>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" text @click="$emit('input', false)">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
