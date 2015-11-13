#!/bin/bash
set -e

# Put data
curl -XPUT 'http://localhost:9200/blog/user/dilbert' -d '{ "name" : "Dilbert Brown" }'

#Get data
curl -XGET 'http://localhost:9200/blog/user/dilbert?pretty=true' | grep "\"name\" : \"Dilbert Brown\""

# Check if kopf is running
curl -XGET 'http://localhost:9200/_plugin/kopf/' | grep "ng-app=\"kopf\""
