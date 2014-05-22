# Ansible Playbook for Elasticsearch
This is an [Ansible](http://www.ansibleworks.com/) playbook for [Elasticsearch](http://www.elasticsearch.org/). You can use it by itself or as part of a larger playbook customized for your local environment.

## Features
- Support for installing plugins
- Support for installing and configuring EC2 plugin
- Support for installing custom JARs in the Elasticsearch classpath (e.g. custom Lucene Similarity JAR)
- Support for installing the [Sematext SPM](http://www.sematext.com/spm/) monitor
- Support for installing the [Marvel](http://www.elasticsearch.org/guide/en/marvel/current/) plugin

## Testing locally with Vagrant
A sample [Vagrant](http://www.vagrantup.com/) configuration is provided to help with local testing. After installing Vagrant, run `vagrant up` at the root of the project to get an VM instance bootstrapped and configured with a running instance of Elasticsearch. Look at `vars/vagrant.yml` and `defaults/main.yml` for the variables that will be substituted in `templates/elasticsearch.yml.j2`.

## Running Standalone Playbook
### Copy Example Files
Make copies of the following files and rename them to suit your environment. E.g.:

- vagrant-main.yml => my-playbook-main.yml
- vagrant-inventory.ini => my-inventory.ini
- vars/vagrant.yml => vars/my-vars.yml

Edit the copied files to suit your environment and needs. See examples below.

### Edit your my-inventory.ini
Edit your my-inventory.ini and customize your cluster and node names:

```
#########################
# Elasticsearch Cluster #
#########################
[es_node_1]
1.2.3.4.compute-1.amazonaws.com
[es_node_1:vars]
elasticsearch_node_name=elasticsearch-1

[es_node_2]
5.6.7.8.compute-1.amazonaws.com
[es_node_2:vars]
elasticsearch_node_name=elasticsearch-2

[es_node_3]
9.10.11.12.compute-1.amazonaws.com
[es_node_3:vars]
elasticsearch_node_name=elasticsearch-3

[all_nodes:children]
es_node_1
es_node_2
es_node_3

[all_nodes:vars]
elasticsearch_cluster_name=my.elasticsearch.cluster
elasticsearch_plugin_aws_ec2_groups=MyElasticSearchGroup
spm_client_token=<your SPM token here>
```

### Edit your vars/my-vars.yml
See `vars/sample.yml` and `vars/vagrant.yml` for exmaple variable files. These are the files where you specify Elasticsearch settings and apply certain features such as plugins, custom JARs or monitoring. The best way to enable configurations is to look at `templates/elasticsearch.yml.j2` and see which variables you want to defile in your `vars/my-vars.yml`. See below for configurations regarding EC2, plugins and custom JARs.

### Edit your my-playbook-main.yml
Example `my-playbook-main.yml`:

```
---

#########################
# Elasticsearch install #
#########################

- hosts: all_nodes
  user: $user
  sudo: yes

  vars_files:
    - defaults/main.yml
    - vars/my-vars.yml

  tasks:
    - include: tasks/main.yml
```

### Launch
```
$  ansible my-playbook-main.yml -i my-inventory.ini -e user=<your sudo user for the elasticsearch installation>
```

## Enabling Added Features
### Configuring EC2
The following variables need to be defined in your playbook or inventory:

- elasticsearch_plugin_aws_version

See [https://github.com/elasticsearch/elasticsearch-cloud-aws](https://github.com/elasticsearch/elasticsearch-cloud-aws) for the version that most accurately matches your installation.

The following variables provide a for now limited configuration for the plugin. More options may be available in the future (see [http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/modules-discovery-ec2.html)](http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/modules-discovery-ec2.html)):

- elasticsearch_plugin_aws_ec2_groups
- elasticsearch_plugin_aws_ec2_ping_timeout
- elasticsearch_plugin_aws_access_key
- elasticsearch_plugin_aws_secret_key

### Installing plugins
You will need to define an array called `elasticsearch_plugins` in your playbook or inventory, such that:
```
elasticsearch_plugins:
 - { name: '<plugin name>', url: '<[optional] plugin url>' }
 - ...
```

where if you were to install the plugin via bin/plugin, you would type:
`bin/plugin -install <plugin name>` or `bin/plugin -install <plugin name> -url <plugin url>`

Example for [https://github.com/elasticsearch/elasticsearch-mapper-attachments](https://github.com/elasticsearch/elasticsearch-mapper-attachments) (`bin/plugin -install elasticsearch/elasticsearch-mapper-attachments/1.9.0`):

```
elasticsearch_plugins:
 - { name: 'elasticsearch/elasticsearch-mapper-attachments/1.9.0' }
```

Example for [https://github.com/richardwilly98/elasticsearch-river-mongodb](https://github.com/richardwilly98/elasticsearch-river-mongodb) (`bin/plugin -i com.github.richardwilly98.elasticsearch/elasticsearch-river-mongodb/1.7.1`):

```
elasticsearch_plugins:
 - { name: 'com.github.richardwilly98.elasticsearch/elasticsearch-river-mongodb/1.7.1' }
```

Example for [https://github.com/imotov/elasticsearch-facet-script](https://github.com/imotov/elasticsearch-facet-script) (`bin/plugin -install facet-script -url http://dl.bintray.com/content/imotov/elasticsearch-plugins/elasticsearch-facet-script-1.1.2.zip`):

```
elasticsearch_plugins:
 - { name: 'facet-script', url: 'http://dl.bintray.com/content/imotov/elasticsearch-plugins/elasticsearch-facet-script-1.1.2.zip' }
```

### Installing Custom JARs
Custom jars are made available to the Elasticsearch classpath by being downloaded into the elasticsearch_home_dir/lib folder. An example of a custom jar can include a custom Lucene Similarity Provider. You will need to define an array called `elasticsearch_custom_jars` in your playbook or inventory, such that:

```
elasticsearch_custom_jars:
 - { uri: '<URL where JAR can be downloaded from: required>', filename: '<alternative name for final JAR if different from file downladed: leave blank to use same filename>', user: '<BASIC auth username: leave blank of not needed>', passwd: '<BASIC auth password: leave blank of not needed>' }
 - ...
```

### Configuring Thread Pools
Elasticsearch [thread pools](http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/modules-threadpool.html) can be configured using the `elasticsearch_thread_pools` list variable:

```
elasticsearch_thread_pools:
  - "threadpool.bulk.type: fixed"
  - "threadpool.bulk.size: 50"
  - "threadpool.bulk.queue_size: 1000"
```

### Enabling Sematext SPM
Enable the SPM task in your playbook:

```
tasks:
    - include: tasks/spm.yml
    - ...
```

Set the spm_client_token variable in your inventory.ini to your SPM key.

### Configuring Marvel

The following variables need to be defined in your playbook or inventory:

- elasticsearch_plugin_marvel_version

The following variables provide configuration for the plugin. More options may be available in the future (see [http://www.elasticsearch.org/guide/en/marvel/current/#stats-export](http://www.elasticsearch.org/guide/en/marvel/current/#stats-export)):

- elasticsearch_plugin_marvel_agent_enabled
- elasticsearch_plugin_marvel_agent_exporter_es_hosts
- elasticsearch_plugin_marvel_agent_indices
- elasticsearch_plugin_marvel_agent_interval
- elasticsearch_plugin_marvel_agent_exporter_es_index_timeformat

## Disable Java installation

If you prefer to skip the built-in installation of the Oracle JRE, use the `elasticsearch_install_java` flag:

```
elasticsearch_install_java: "false"
```

## Include role in a larger playbook
### Add this role as a git submodule
Assuming your playbook structure is such as:
```
- my-master-playbook
  |- vars
  |- roles
  |- my-master-playbook-main.yml
  \- my-master-inventory.ini
```

Checkout this project as a submodule under roles:

```
$  cd roles
$  git submodule add git://github.com/traackr/ansible-elasticsearch.git ./ansible-elasticsearch
$  git submodule update --init
$  git commit ./submodule -m "Added submodule as ./subm"
```

### Include this playbook as a role in your master playbook
Example `my-master-playbook-main.yml`:

```
---

#########################
# Elasticsearch install #
#########################

- hosts: all_nodes
  user: ubuntu
  sudo: yes

  roles:
    - ansible-elasticsearch

  vars_files:
    - vars/my-vars.yml
```

# Issues, requests, contributions
This software is provided as is. Having said that, if you see an issue, feel free to log a ticket. We'll do our best to address it. Same if you want to see a certain feature supported in the fututre. No guarantees are made that any requested feature will be implemented. If you'd like to contribute, feel free to clone and submit a pull request.

# Dependencies
None

# License
MIT

# Author Information

George Stathis - gstathis [at] traackr.com
