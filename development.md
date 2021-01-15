## Development environment setup

MIQA has server, client two components. They are located under *server* and *client* directory respectively.

### Prerequisite
* Pyhton 3.5+
* Mongodb running at the default port
* Node 8

### Server

#### Pre-requisite for active learning:

Both `celery` and RabbitMQ are required for the active learning component of the application, which uses Girder Worker.

RabbitMQ is available for Mac OS via homebrew, or on debian Linux systems via `apt-get`.  There is also a Docker image available.  See the Girder Worker [docs](https://girder-worker.readthedocs.io/en/latest/getting-started.html) on getting started for details.  Normally, `celery` is available as a python module, but do not install it directly, as the latest version is not compatible with Girder Worker.  Rather, install the `girder-worker` module, which installs appropriate versions of dependencids.  The install command is shown in the steps below.

#### Setup

* `git clone https://github.com/OpenImaging/miqa.git`
* `pip install -e miqa/server/`
* `pip install -e miqa/miqa_worker_task/`
* `pip install -e miqa/mriqc/`
* `pip install girder-worker`
* `girder build`
* `girder serve`

Now a running girder instance should be available at `localhost:8080/girder`

#### Extra steps for active learning

First start the rabbitmq server:

```
/usr/local/sbin/rabbitmq-server
```

Assuming the installation was successful, this should print output similar to the following:

```
$ /usr/local/sbin/rabbitmq-server
Configuring logger redirection

  ##  ##      RabbitMQ 3.8.9
  ##  ##
  ##########  Copyright (c) 2007-2020 VMware, Inc. or its affiliates.
  ######  ##
  ##########  Licensed under the MPL 2.0. Website: https://rabbitmq.com

  Doc guides: https://rabbitmq.com/documentation.html
  Support:    https://rabbitmq.com/contact.html
  Tutorials:  https://rabbitmq.com/getstarted.html
  Monitoring: https://rabbitmq.com/monitoring.html

  Logs: /usr/local/var/log/rabbitmq/rabbit@localhost.log
        /usr/local/var/log/rabbitmq/rabbit@localhost_upgrade.log

  Config file(s): (none)

  Starting broker...

 completed with 6 plugins.
```

Set the MRIQC master path in your environment and start `celery`:

```
export MIQA_MRIQC_PATH=/Users/scott/miqa/mriqc_master_folder
celery worker -A girder_worker.app -l info
```

If there were no errors, then this should print something like:

```
$ celery worker -A girder_worker.app -l info
/_REDACTED_/site-packages/celery/backends/amqp.py:67: CPendingDeprecationWarning:
    The AMQP result backend is scheduled for deprecation in     version 4.0 and removal in version v5.0.     Please use RPC backend or a persistent backend.

  alternative='Please use RPC backend or a persistent backend.')

 -------------- celery@_REDACTED_.local v4.4.7 (cliffs)
--- ***** -----
-- ******* ---- Darwin-19.6.0-x86_64-i386-64bit 2021-01-14 17:41:41
- *** --- * ---
- ** ---------- [config]
- ** ---------- .> app:         girder_worker:0x10d6c27d0
- ** ---------- .> transport:   amqp://guest:**@localhost:5672//
- ** ---------- .> results:     amqp://
- *** --- * --- .> concurrency: 8 (prefork)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** -----
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery


[tasks]
  . girder_worker.docker.tasks.docker_run
  . miqa_worker_task.tasks.retrain_with_data_task

[2021-01-14 17:41:41,600: INFO/MainProcess] Connected to amqp://guest:**@127.0.0.1:5672//
[2021-01-14 17:41:41,615: INFO/MainProcess] mingle: searching for neighbors
[2021-01-14 17:41:42,648: INFO/MainProcess] mingle: all alone
[2021-01-14 17:41:42,665: INFO/MainProcess] celery@_REDACTED_.local ready.
```

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
To put the sample data somewhere other than the user home directory, the json
data description must be edited, probably just to update the `data_root` value
to match the location of the data on your system.  For more information on
importing arbitrary datasets, see `IMPORTING_DATA.md`.

#### Prepare data store
* Navigate to localhost:8080 and click the third tab to open girder interface
* Navigate to *Collection*
* Create a collection named `miqa`
* Navigate to *Admin Console*, *Assetstores*
* Create a *Filesystem* assetstore

#### Populate data
* Navigate back to localhost:8081 and navigate to `Settings` tab
* Suppose the repo is located at home diretory.
* Set `import path` to `~/miqa/sample_data/sample.json` and set `export path` to something like `~/miqa/sample_data/sample-output.json`
