<script>
export default {
  name: "FileSelector",
  props: {
    value: {
      type: [Array, String]
    },
    accept: {
      type: String,
      default: "*"
    },
    label: {
      type: String,
      default: "Choose file"
    },
    required: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    multiple: {
      type: Boolean,
      default: false
    },
    messages: {
      type: [String, Array],
      default: ""
    }
  },
  data() {
    return {
      filename_: ""
    };
  },
  computed: {
    filename() {
      if (this.value) {
        return this.value;
      } else {
        return this.filename_;
      }
    }
  },
  methods: {
    onFocus() {
      if (!this.disabled) {
        this.$refs.fileInput.click();
      }
    },
    onFileChange($event) {
      const files = $event.target.files || $event.dataTransfer.files;
      var filename;
      if (files) {
        if (files.length > 0) {
          filename = [...files].map(file => file.name).join(", ");
        } else {
          filename = null;
        }
      } else {
        filename = $event.target.value.split("\\").pop();
      }
      this.filename_ = filename;
      this.$emit("input", filename);
      this.$emit("file", this.multiple ? files : files[0]);
    }
  }
};
</script>

<template>
  <div>
    <v-text-field
      class="file-selector"
      readonly
      append-icon="attach_file"
      :disabled="disabled"
      :value="filename"
      :label="label"
      :messages="messages"
      :required="required"
      @click.native="onFocus"
      ref="fileTextField"
    ></v-text-field>
    <input
      type="file"
      :accept="accept"
      :multiple="multiple"
      :disabled="disabled"
      ref="fileInput"
      @change="onFileChange"
    />
  </div>
</template>

<style scoped>
input[type="file"] {
  position: absolute;
  left: -99999px;
}
</style>
