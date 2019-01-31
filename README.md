# MIQA

## Develop environment setup

Miqa has server, client two components. They are located under *miqa_server* and *client* directory respectively.

### Prerequisite
* Pyhton 3.6+ 
(3.6+ required) 
* Mongodb running at the default port
* Node 8

### Server

#### Install Girder
MIQA server is a girder plugin. MIQA needs to be installed on a working copy of girder. There are many ways to set up girder. The following shows how to set up a girder instance from source code.
* `git clone https://github.com/girder/girder.git`
* `pip install -e girder`
* `girder build`
* `girder serve`

Now a running girder instance should be available at `localhost:8080`

#### Install Miqa Server as a girder plugin
* `git clone https://github.com/OpenImaging/miqa.git`
* `pip install -e miqa/miqa_server/`

#### Setup Girder with Miqa Server
* `girder serve`
* Navigate to localhost:8080
* Create admin user
* Navigate to *Admin Console*, *System configuration*
* Populate values under *Email Delivery* to enable girder to send emails
* under *Advanced Settings*, Set *CORS Allowed Origins* to *, then click *Save*
* Navigate to *Admin Console*, *Plugins*
* Enable *miqa server*
* Stop `girder serve` process and restart it

#### Populate data (Current method)
* Navigate to *Collection*
* Create a collection named `miqa`
* Copy the collection ID from the URL or detail dialog
* Navigate to *Admin Console*, *Assetstores*
* Create a *Filesystem* assetstore
* Click *Import data*
* Set *Import path* to a location accessible by the server that contains nii.gz files at third level
Such as the *data* directory if you have obtained a sample data archive
* Set *Destination type* to *Collection*
* Set *Destination ID* to the collection ID copied above, and leave *Leaf Folders as Items* to *False*
* Click *Begin import*
* The process should finish without error

#### Client
Miqa client is a [Vue CLI](https://cli.vuejs.org/) based application. All Vue-CLI options are available. 

* `cd miqa/client`
* `npm install`
* `npm run serve`
* Navigate to `localhost:8081`
* After login, datasets should be available in the application
