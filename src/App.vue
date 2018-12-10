<template>
  <v-app id="app">
    <v-toolbar app>
      <v-toolbar-title class="ml-0 pl-3">
        <span>MIQA</span>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-toolbar-items class="hidden-sm-and-down">
        <v-btn flat>Upload Scans</v-btn>
        <v-btn flat>Browse Scans</v-btn>
        <v-btn flat>Screenshots</v-btn>
        <v-btn icon>
          <v-icon>person</v-icon>
        </v-btn>
      </v-toolbar-items>
    </v-toolbar>
    <router-view/>
  </v-app>
</template>

<style lang="scss">
html {
  overflow-y: auto !important;
}
</style>