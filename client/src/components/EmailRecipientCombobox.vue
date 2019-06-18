<script>
export default {
  name: "EmailRecipientCombobox",
  props: {
    label: {
      type: String,
      required: true
    },
    value: {
      reqyured: true,
      type: Array
    },
    candidates: {
      type: Array,
      default: () => []
    },
    required: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    isValid(recipient) {
      if (this.candidates.indexOf(recipient) !== -1) {
        return true;
      } else {
        return /.+@.+/.test(recipient);
      }
    },
    allValid(recipients) {
      var invalid = recipients.find(recipient => !this.isValid(recipient));
      return invalid ? "Receipient is not valid" : true;
    }
  }
};
</script>

<template>
  <v-combobox
    :value="value"
    @input="$emit('input', $event)"
    :items="candidates"
    :label="label"
    multiple
    deletable-chips
    small-chips
    :rules="[
      allValid,
      v =>
        !!v.length || (required ? `at least one recipient is required` : true)
    ]"
    hide-selected
  >
    <template #selection="{ item, parent, selected }">
      <v-chip
        :color="isValid(item) ? '' : 'error'"
        :selected="selected"
        small
        close
        @input="parent.selectItem(item)"
        >{{ item }}</v-chip
      >
    </template>
  </v-combobox>
</template>
