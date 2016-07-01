#!/bin/bash

usage() {
  cat <<EOF
  usage: $0 -n <node> -t <target_node>

  This script starts reroute unassigned shards to another elasticsearch node

  OPTIONS:
     -h   Show this message
     -n   Elasticsearch host
     -t   Target node to move the unassigned shards
EOF
}

type curl >/dev/null 2>&1 || {
  echo >&2 "curl required ;-)";
  exit 1
}

ESHOST=
TARGETNODE=

while getopts "h:n:t:" OPTION
do
  case $OPTION in
    h)
      usage
      exit 1
      ;;
    n)
      ESHOST=$OPTARG
      ;;
    t)
      TARGETNODE=$OPTARG
      ;;
    ?)
      usage
      exit
    ;;
  esac
done

if [[ -z $ESHOST ]] || [[ -z $TARGETNODE ]]; then
  usage
  exit 1
fi

IFS=$'\n'
for line in $(curl -s "${ESHOST}:9200/_cat/shards" | fgrep UNASSIGNED); do
  INDEX=$(echo $line | (awk '{print $1}'))
  SHARD=$(echo $line | (awk '{print $2}'))

  curl -XPOST "$ESHOST:9200/_cluster/reroute?pretty" -d '{
     "commands": [
        {
            "allocate": {
                "index": "'$INDEX'",
                "shard": '"$SHARD"',
                "node": "'$TARGETNODE'",
                "allow_primary": true
          }
        }
    ]
  }'

done
