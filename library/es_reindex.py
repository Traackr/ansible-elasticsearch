#!/usr/bin/python
__author__ = 'cvig'
# run this as an ad-hoc ansible task:
# ansible master -m es_reindex -i /etc/ansible/localhost.ini -a "to_index=wiki2 from_index=wiki"

import logging

from ansible.module_utils.basic import *
###### MOVE THIS TO A SEPARATE MODULE PLEASE #####
import logging
import elasticsearch
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan, bulk
string_types = str,bytes


def reindex_h(client, source_index, target_index, query=None, target_client=None,
        chunk_size=500, scroll='5m', userfields=[], scan_kwargs={}, bulk_kwargs={}):

    """
    Reindex all documents from one index that satisfy a given query
    to another, potentially (if `target_client` is specified) on a different cluster.
    If you don't specify the query you will reindex all the documents.

    .. note::

        This helper doesn't transfer mappings, just the data.

    :arg client: instance of :class:`~elasticsearch.Elasticsearch` to use (for
        read if `target_client` is specified as well)
    :arg source_index: index (or list of indices) to read documents from
    :arg target_index: name of the index in the target cluster to populate
    :arg query: body for the :meth:`~elasticsearch.Elasticsearch.search` api
    :arg target_client: optional, is specified will be used for writing (thus
        enabling reindex between clusters)
    :arg chunk_size: number of docs in one chunk sent to es (default: 500)
    :arg scroll: Specify how long a consistent view of the index should be
        maintained for scrolled search
    :arg scan_kwargs: additional kwargs to be passed to
        :func:`~elasticsearch.helpers.scan`
    :arg bulk_kwargs: additional kwargs to be passed to
        :func:`~elasticsearch.helpers.bulk`
    """
    target_client = client if target_client is None else target_client

    docs = scan(client,
        query=query,
        index=source_index,
        scroll=scroll,
        fields= ('_source', '_parent', '_routing', '_timestamp'),
        **scan_kwargs
    )
    def _change_doc_index(hits, index):

        for h in hits:
            h['_index'] = index
            if 'fields' in h:
                h.update(h.pop('fields'))
            yield h

    def expand_my_action(data):
        """
        From one document or action definition passed in by the user extract the
        action/data lines needed for elasticsearch's
        :meth:`~elasticsearch.Elasticsearch.bulk` api.
        """
        # when given a string, assume user wants to index raw json
        if isinstance(data, string_types):
            return '{"index":{}}', data

        # make sure we don't alter the action
        data = data.copy()
        op_type = data.pop('_op_type', 'index')
        action = {op_type: {}}
        for key in ('_index', '_parent', '_percolate', '_routing', '_timestamp',
                '_ttl', '_type', '_version', '_version_type', '_id', '_retry_on_conflict'):
            if key in data:
                action[op_type][key] = data.pop(key)

        # no data payload for delete
        if op_type == 'delete':
            return action, None
        if userfields:
            returdata = {}
            for field in userfields:
                if field in data['_source']:
                    returdata[field] = data['_source'][field]
                else:
                    logging.info('field not found in _source "%s"' % field)


            return action, returdata
        return action, data.get('_source', data)


    kwargs = {
        'stats_only': True,
        'expand_action': expand_my_action
    }
    kwargs.update(bulk_kwargs)
    return bulk(target_client, _change_doc_index(docs, target_index),
                chunk_size=chunk_size, stats_only=True, expand_action_callback=expand_my_action)


class ReIndex():
    def __init__(self, module):
        if 'elasticsearch_host' in module.params:
            self.es = Elasticsearch(module.params['elasticsearch_host'], timeout=100)
        else:
            self.es = Elasticsearch(timeout=100)
        self.from_index = module.params['from_index']
        self.to_index = module.params['to_index']
        self.query = None
        if 'query' in module.params:
            self.query = module.params['query']
        self.fields = None
        if 'fields' in module.params:
            self.fields = module.params['fields']
        self.module = module
        esup = self.es.ping()
        logging.info('in reindex')
        if not esup:
            msg = "could not connect to  host  %s" % module.params['elasticsearch_host']
            module.exit_json(failed=True, msg=msg)

    def reindex(self):
        try:
            reindex_h(self.es, self.from_index, self.to_index, self.query, userfields=self.fields)
        except elasticsearch.ElasticsearchException as ex:
            msg = "Error reindexing   %s" % ex
            self.module.exit_json(failed=True, msg=msg)
        except Exception as e:
            msg = "Error reindexing  %s" % e
            self.module.exit_json(failed=True, msg=msg)


#class MyModule():
#    def __init__(self, params):
#        self.params = params
#    def exit_json(self, **kwargs):
#        logging.info('feiled')
#def main():
#    module=MyModule({'from_index':'wiki', 'to_index': 'wiki3', 'fields': ['title', 'article', 'timestamp']})
#    reindex=ReIndex(module)
#    reindex.reindex()

#logging.basicConfig(filename='reindex.log', level=logging.INFO)
#main()
### END OF MOVE TO SEPARATE MODULE #####


def main():

    module = AnsibleModule(
        argument_spec=dict(
            from_index=dict(required=True, type='str'),
            to_index=dict(required=True, type='str'),
            fields=dict(required=False, type='list'),
            elasticsearch_host=dict(required=False, type='str', default='localhost:9200'),
            query=dict(required=False, type='str', default=None)
        )
    )
    logging.debug('in main')
    reindex = ReIndex(module)
    reindex.reindex()
    module.exit_json(changed=True, result="Reindex from '%s' to '%s' " % (module.params['from_index'], module.params['to_index']))

if __name__ == '__main__':
    logging.basicConfig(filename='example.log', level=logging.INFO)
    main()


