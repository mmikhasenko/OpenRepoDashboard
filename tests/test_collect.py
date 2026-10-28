import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('collector',Path(__file__).resolve().parents[1]/'scripts/collect.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
class CollectorTests(unittest.TestCase):
    def test_private_repository_blocks_all_subsequent_collection(self):
        with patch.object(c,'api',return_value={'private':True,'visibility':'private'}) as api:
            result=c.collect({'repository':'owner/repo','category':'JuliaDev'})
        self.assertEqual(api.call_count,1)
        self.assertTrue(result['errors'])
        self.assertEqual(result['workflows'],[])
    def test_missing_permissions_are_not_success(self):
        with patch.object(c,'api',side_effect=RuntimeError('GitHub HTTP 403')):
            result=c.collect({'repository':'owner/repo','category':'JuliaDev'})
        self.assertTrue(result['errors'])
    def test_completed_duration_and_running(self):
        self.assertEqual(c.duration({'status':'completed','run_started_at':'2026-10-28T06:00:00Z','updated_at':'2026-10-28T06:02:15Z'}),135)
        self.assertIsNone(c.duration({'status':'in_progress'}))
