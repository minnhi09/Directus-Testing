"""Offline safety checks: no Docker/API calls, no credentials."""
import copy
import json
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import p09_runtime as p09


class RuntimeOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.ns = 'r06-k05-p09-offline-fixture'
        self.profile = json.loads(p09.PROFILE.read_text())
        self.labels = {'com.docker.compose.project':self.ns, 'damh.phase':'P09', 'damh.namespace':self.ns}
        self.volumes = [{'Name':self.ns+suffix, 'Labels':self.labels} for suffix in ('_db_data','_uploads','_extensions')]
        self.networks = [{'Name':self.ns+'_network', 'Labels':self.labels}]
        self.containers = []
        for service, mounts in [('database', [('_db_data','/var/lib/postgresql/data')]),
                                ('directus', [('_uploads','/directus/uploads'),('_extensions','/directus/extensions')])]:
            self.containers.append({'Config':{'Labels':{**self.labels,'com.docker.compose.service':service},
                'Image':self.profile['services'][service]['image']}, 'State':{'Health':{'Status':'healthy'}},
                'Mounts':[{'Type':'volume','Name':self.ns+n,'Destination':d} for n,d in mounts],
                'NetworkSettings':{'Networks':{self.ns+'_network':{}}, 'Ports':
                    {'8055/tcp':[{'HostIp':'127.0.0.1','HostPort':'18055'}]} if service=='directus' else {}}})

    def check(self):
        return p09.check_resources(self.ns,self.containers,self.volumes,self.networks,self.profile)

    def test_owned_lab_accepted(self):
        self.assertEqual(set(self.check()), {'database','directus'})

    def test_old_db_volume_rejected(self):
        self.containers[0]['Mounts'][0]['Name'] = 'r06-k05_db_data'
        with self.assertRaisesRegex(ValueError,'STORAGE'):
            self.check()

    def test_host_bind_rejected(self):
        self.containers[1]['Mounts'].append({'Type':'bind','Destination':'/directus/demo'})
        with self.assertRaisesRegex(ValueError,'STORAGE'):
            self.check()

    def test_public_api_or_published_db_rejected(self):
        original = copy.deepcopy(self.containers)
        self.containers[1]['NetworkSettings']['Ports']['8055/tcp'][0]['HostIp'] = '0.0.0.0'
        with self.assertRaisesRegex(ValueError,'PORT'):
            self.check()
        self.containers = original
        self.containers[0]['NetworkSettings']['Ports'] = {'5432/tcp':[{'HostIp':'127.0.0.1','HostPort':'5432'}]}
        with self.assertRaisesRegex(ValueError,'PORT'):
            self.check()

    def test_foreign_network_or_volume_owner_rejected(self):
        self.containers[0]['NetworkSettings']['Networks']['demo'] = {}
        with self.assertRaisesRegex(ValueError,'NETWORK'):
            self.check()
        del self.containers[0]['NetworkSettings']['Networks']['demo']
        self.volumes[0]['Labels'] = {**self.labels,'damh.namespace':'demo'}
        with self.assertRaisesRegex(ValueError,'OWNERSHIP'):
            self.check()

    def test_wrong_image_and_unhealthy_rejected(self):
        self.containers[0]['Config']['Image'] = 'postgres:latest'
        with self.assertRaisesRegex(ValueError,'IMAGE'):
            self.check()
        self.containers[0]['Config']['Image'] = self.profile['services']['database']['image']
        self.containers[1]['State']['Health']['Status'] = 'unhealthy'
        with self.assertRaisesRegex(ValueError,'HEALTHY'):
            self.check()
