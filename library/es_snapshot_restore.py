#!/usr/bin/python
__author__ = 'cvig'

import logging
try:
    from elasticsearch import Elasticsearch
    HAS_ELASTIC = True
except ImportError:
    HAS_ELASTIC = False

class SnapRestore():
    def __init__(self, module):
        self.backup_name = module.params['repository_name']
        self.es = Elasticsearch(module.params['elasticsearch_host'])
        self.snapshot_indices = module.params['snapshot_indices']
        self.snapshot_name = module.params['snapshot_name']
        self.repository_path = module.params['repository_path']
        self.module = module
        esup = self.es.ping()
        if esup is False:
            msg = "could not connect to  host  %s" % module.params['elasticsearch_host']
            module.exit_json(failed=True, msg=msg)
        self.create_repo()

    def create_snapshot(self):
        try:
            body = {}
            if self.snapshot_indices:
                body['indices'] = self.snapshot_indices
            self.es.snapshot.create(repository=self.backup_name, snapshot=self.snapshot_name, body=body)
        except elasticsearch.ElasticsearchException as ex:
            msg = "Error creating snapshot  %s" % ex
            self.module.exit_json(failed=True, msg=msg)
        except Exception as e:
            msg = "Error creating snapshot  %s" % e
            self.module.exit_json(failed=True, msg=msg)

    def restore_snapshot(self):
        try:
            body = {}
            if self.snapshot_indices:
                body['indices'] = self.snapshot_indices
            self.es.snapshot.restore(repository=self.backup_name, snapshot=self.snapshot_name, body=body)
        except elasticsearch.ElasticsearchException as ex:
            msg = "Error restoring snapshot  %s" % ex
            self.module.exit_json(failed=True, msg=msg)

    def create_repo(self):
        try:
            result = self.es.snapshot.get_repository(repository=self.backup_name, ignore=404)
            if not('status' in result):
                if result[self.backup_name]['settings']['location'] == self.repository_path:
                    msg = "repo already registered at location  %s" % self.repository_path
                    return

            body = {'type': 'fs', 'settings': {'location': self.repository_path, 'compress': True}}
            result = self.es.snapshot.create_repository(repository=self.backup_name, body=body, verify=True, ignore=[404, 400])
            msg = "Snapshot repo registered at location  %s output: %s" % (self.repository_path, result)
        except elasticsearch.ElasticsearchException as ex:
            msg = "Error creating snapshot  %s error; %s" % (module.params['elasticsearch_host'], ex)
            self.module.exit_json(failed=True, msg=msg)

        #
        # except Exception as err:
        #    print err
        #    module.exit_json(failed=True, msg="There was some kind of error %s" % err)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent']),
            repository_name=dict(required=True, type='str'),
            elasticsearch_host=dict(required=True, type='str'),
            snapshot_indices=dict(required=False, type='str'),
            snapshot_name=dict(required=True, type='str'),
            repository_path=dict(required=True, type='str'),
            mode=dict(required=True, choices=['snapshot', 'restore'], type='str')
        )
    )
    if not HAS_ELASTIC:
        module.fail_json(msg='The elasticsearch python module is required')

    mode = module.params['mode']
    snaprestore = SnapRestore(module)
    if mode == 'snapshot':
        snaprestore.create_repo()
        snaprestore.create_snapshot()
        module.exit_json(changed=True, result="snapshot '%s' created" % module.params['snapshot_name'])
    if mode == 'restore':
        snaprestore.restore_snapshot()
        module.exit_json(changed=True, result="snapshot '%s' restored" % module.params['snapshot_name'])

# import module snippets
from ansible.module_utils.basic import *
logging.basicConfig(level=logging.DEBUG)
main()
