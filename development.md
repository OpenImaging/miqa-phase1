## Development environment setup

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
* Create a user
* Navigate to *Admin Console*, *System configuration*
* Populate fields under *Email Delivery* of appropriate values to enable girder to send emails
* under *Advanced Settings*, Set *CORS Allowed Origins* to *, then click *Save*

### Client
Miqa client is a [Vue CLI](https://cli.vuejs.org/) based application. All Vue-CLI options are available. 

* keep the server running and open a new terminal
* `cd miqa/client`
* `npm install`
* `npm run serve`
* Navigate to `localhost:8081`
* and login with the user created above

### Data
The repo has a sample dataset. By default, it needs to be put under user home directory.
Sample data is attributed to: [OpenNeuro](https://openneuro.org/datasets/ds000002/versions/00002)

#### Prepare data store
* Navigate to localhost:8080 and click the third tab to open girder interface
* Navigate to *Collection*
* Create a collection named `miqa`
* Navigate to *Admin Console*, *Assetstores*
* Create a *Filesystem* assetstore

#### Populate data
* Navigate back to localhost:8081 and navigate to `Settings` tab
* Suppose the repo is located at home diretory. 
* Set `import path` to `~/miqa/sample_data/sample.csv` and set `export path` to something like `~/miqa/sample_data/sample-output.csv`
