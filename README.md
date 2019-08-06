# MIQA

## Develop environment setup

MIQA has server, client two components. They are located under *server* and *client* directory respectively.

### Prerequisite
* Pyhton 3.5+
* Mongodb running at the default port
* Node 8

### Server

#### Setup
* `git clone https://github.com/OpenImaging/miqa.git`
* `pip install -e miqa/server/`
* `girder build`
* `girder serve`
Now a running girder instance should be available at `localhost:8080/girder`

#### Setup Girder with Miqa Server
* Navigate to `localhost:8080/girder`
* Create admin user
* Navigate to *Admin Console*, *System configuration*
* Populate fields under *Email Delivery* of appropriate values to enable girder to send emails
* under *Advanced Settings*, Set *CORS Allowed Origins* to *, then click *Save*

### Client
Miqa client is a [Vue CLI](https://cli.vuejs.org/) based application. All Vue-CLI options are available. 

* `cd miqa/client`
* `npm install`
* `npm run serve`
* Navigate to `localhost:8081`
* After login, datasets should be available in the application

### Populate data
MIQA works with any data provided in the following format. The repo currently doesn't provide a sample dataset.

* Navigate to localhost:8080 and jump to the Girder interface
* Navigate to *Collection*
* Create a collection named `miqa`
* Copy the collection ID from the URL or detail dialog
* Navigate to *Admin Console*, *Assetstores*
* Create a *Filesystem* assetstore
* Navigate back to localhost:8080 and open the Sessions sidebar
* Choose a CSV file. the CSV file needs to have the following fields
  * *xnat_experiment_id*, an id field of an experiment. Same id will be grouped
  * *nifti_folder*, *scan_id*, and *scan_type* these three columns will be concatenated into a directory path, which needs to be accessible by the server and each directory needs to contain one or more **.nii.gz* files
  * *experiment_note*
  * *decision*
* Click *Import*. The importing will take up to few minutes based on number of record in the CSV file

## Deployment
MIQA can be deploymented on any linux system. This repo provided a [solution](devops/docker/README.md) with Docker.
