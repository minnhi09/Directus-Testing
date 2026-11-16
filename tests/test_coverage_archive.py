"""Offline archive identity/tamper checks; snapshots are synthetic fixtures."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import coverage_offline as c


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.archive=self.root/'docs/coverage/sources/immutable-inputs-v1'
        self.archive.mkdir(parents=True);self.raw=b'historical fixture\n'
        self.digest=hashlib.sha256(self.raw).hexdigest();self.snapshot=self.archive/(self.digest+'.txt');self.snapshot.write_bytes(self.raw)
        current=self.root/'manifest/baseline.yaml';current.parent.mkdir();current.write_bytes(b'new baseline\n')
        self.ref=dict(kind='ARTIFACT',path='manifest/baseline.yaml',revision=None,sha256=self.digest,pointer='#L1')
        self.entry=dict(source_kind='ARTIFACT',source_path=self.ref['path'],revision=None,sha256=self.digest,
                        snapshot_path=self.snapshot.relative_to(self.root).as_posix(),bytes=len(self.raw))
        self.data={'baseline-manifest':{'sut_commit':'pinned-sha'},'refs':[self.ref]}
        self.write_index([self.entry])
        self.root_patch=patch.object(c,'ROOT',self.root);self.root_patch.start();self.addCleanup(self.root_patch.stop)

    def write_index(self,entries):
        p=self.archive/'index.json';p.write_text(json.dumps({'format':'P08_INPUT_ARCHIVE_1','entries':entries}))
        self.data['input-archive']=dict(format='P08_INPUT_ARCHIVE_1',index_path=p.relative_to(self.root).as_posix(),index_sha256=hashlib.sha256(p.read_bytes()).hexdigest())

    def test_declared_snapshot_keeps_original_hash_and_data(self):
        original=copy.deepcopy(self.data)
        self.assertEqual(c.reference_check(self.data,False)['archived_identities'],1)
        self.assertEqual(self.data,original)
        self.assertEqual((self.root/'manifest/baseline.yaml').read_bytes(),b'new baseline\n')

    def test_no_implicit_fallback_without_sidecar(self):
        del self.data['input-archive']
        with self.assertRaisesRegex(c.Invalid,'ARTIFACT_HASH_MISMATCH'):c.reference_check(self.data,False)

    def test_snapshot_tamper_same_size_is_failure(self):
        self.snapshot.write_bytes(b'X'+self.raw[1:])
        with self.assertRaisesRegex(c.Invalid,'ARTIFACT_HASH_MISMATCH'):c.reference_check(self.data,False)

    def test_snapshot_truncation_is_failure(self):
        self.snapshot.write_bytes(b'')
        with self.assertRaisesRegex(c.Invalid,'ARCHIVE_SNAPSHOT_SIZE'):c.reference_check(self.data,False)

    def test_index_tamper_is_failure(self):
        with (self.archive/'index.json').open('a') as f:f.write(' ')
        with self.assertRaisesRegex(c.Invalid,'ARCHIVE_INDEX_HASH'):c.reference_check(self.data,False)

    def test_different_source_identity_is_not_rebound(self):
        self.entry['source_path']='manifest/another.yaml';self.write_index([self.entry])
        with self.assertRaisesRegex(c.Invalid,'ARTIFACT_HASH_MISMATCH'):c.reference_check(self.data,False)

    def test_changed_expected_digest_does_not_select_snapshot(self):
        self.ref['sha256']='0'*64
        with self.assertRaisesRegex(c.Invalid,'ARTIFACT_HASH_MISMATCH'):c.reference_check(self.data,False)

    def test_archive_path_escape_and_duplicate_identity_fail(self):
        self.entry['snapshot_path']='runtime/private.env';self.write_index([self.entry])
        with self.assertRaisesRegex(c.Invalid,'ARCHIVE_SNAPSHOT_PATH'):c.reference_check(self.data,False)
        self.entry['snapshot_path']=self.snapshot.relative_to(self.root).as_posix();self.write_index([self.entry,self.entry])
        with self.assertRaisesRegex(c.Invalid,'ARCHIVE_DUPLICATE_IDENTITY'):c.reference_check(self.data,False)

    def test_pointer_range_still_checked(self):
        self.ref['pointer']='#L99'
        with self.assertRaisesRegex(c.Invalid,'LINE_REF_RANGE'):c.reference_check(self.data,False)

    def test_private_env_reference_rejected_even_with_snapshot(self):
        self.ref['path']='runtime/p09.env';self.entry['source_path']=self.ref['path'];self.write_index([self.entry])
        with self.assertRaisesRegex(c.Invalid,'SENSITIVE_REF_PATH'):c.reference_check(self.data,False)

    def test_pinned_git_snapshot_works_without_source_checkout(self):
        self.ref.update(kind='GIT_FILE',path='../directus/api/src/app.ts',revision='pinned-sha')
        self.entry.update(source_kind='GIT_FILE',source_path=self.ref['path'],revision='pinned-sha');self.write_index([self.entry])
        with patch.object(c.subprocess,'run',side_effect=AssertionError('No Git or network permitted')):
            self.assertEqual(c.reference_check(self.data,False)['archived_identities'],1)
        self.ref['revision']='other-sha'
        with self.assertRaisesRegex(c.Invalid,'REF_SOURCE_BASELINE'):c.reference_check(self.data,False)


if __name__=='__main__':unittest.main()
