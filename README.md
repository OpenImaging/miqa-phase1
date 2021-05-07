# MIQA
MIQA is a medical scan QA/QC application. It takes .nifti files and a CSV file as input, and output the same CSV file with additional QA/QC results.

The server is built based on [Girder](https://github.com/girder/girder), a python based data management solution, and the client application is built with [Vue.js](https://vuejs.org/), Vuetify, and Vue CLI. The medical scan visualization is powered by [VTK.js](https://kitware.github.io/vtk-js/index.html)

## A screen record
![](https://user-images.githubusercontent.com/3123478/63644049-df545a80-c6ad-11e9-8a32-22b18c3add25.gif)

## Active learning
MIQA has an implementation of active learning. It uses MRIQC to extract features out of scans then uses labeled data and Random Forest Regression to evaluate if a dataset meets the standard.

## Development
MIQA can be developed on Linux. See [development](development.md) for detail.

## Deployment
MIQA can be deployed on any Linux system. This repo provides a [solution](devops/docker/README.md) with Docker.

## Try out MIQA
The simplest way to try out MIQA is to follow the steps [here](https://cloud.docker.com/u/kitware/repository/docker/kitware/miqa/general). You could also build MIQA from scratch with the [scripts here](devops/docker/README.md).
