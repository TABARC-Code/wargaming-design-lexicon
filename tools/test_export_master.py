#!/usr/bin/env python3
"""Small, repeatable checks for the staged lexicon exporter."""
import pathlib
import sqlite3
import tempfile
import unittest
from export_master import validate, build_release, tokens, col_index, ReleaseError


def sample():
    return {
        'Lexicon': [
            {'ID':'WG-0001','Term':'Model','Plain-English meaning':'A physical game piece.',
             'Source keys':'SRC1','Aliases / Related labels':'figure; miniature','Category':'Game object'},
            {'ID':'WG-0002','Term':'Legacy model','Plain-English meaning':'Historical duplicate.',
             'Source keys':'SRC1','Aliases / Related labels':'','Category':'Game object'},
        ],
        'Sources':[{'Key':'SRC1','System':'Sample','URL':'https://example.org/source'}],
        'Relationships':[{'Source ID':'WG-0001','Relationship':'similar_to','Target ID':'WG-0002'}],
        'Canonical View':[{'WG ID':'WG-0001','Status':'ACTIVE'},
                          {'WG ID':'WG-0002','Status':'LEGACY_DUPLICATE -> WG-0001'}],
        'Rule Occurrences':[{'Occurrence ID':'OCC-1','Canonical WG ID':'WG-0001'}],
        'Discoveries':[{'Discovery ID':'DISC-1','Source term':'Keyword'}],
        'Candidates':[{'Candidate ID':'CAND-1','Proposed canonical':'Candidate'}],
        'Review Queue':[{'Queue reference':'CAND-1','Reason':'Needs source'}],
    }


class ValidationTests(unittest.TestCase):
    def test_token_split(self):
        self.assertEqual(tokens('A; B;; C '),['A','B','C'])
        self.assertEqual(col_index('AB12'),27)

    def test_valid_with_redirect(self):
        errors, _, counts, status, aliases, links = validate(sample())
        self.assertEqual(errors,[])
        self.assertEqual(counts['redirects'],1)
        self.assertEqual(status['WG-0002'],('REDIRECT','WG-0001'))
        self.assertEqual(len(aliases),2)
        self.assertEqual(len(links),2)

    def test_unregistered_source_rejected(self):
        data=sample();data['Lexicon'][0]['Source keys']='MISSING'
        self.assertIn('unregistered source',str(validate(data)[0]))

    def test_duplicate_term_rejected(self):
        data=sample();data['Lexicon'][1]['ID']='WG-0001'
        self.assertIn('occurs 2 times',str(validate(data)[0]))

    def test_invalid_relation_rejected(self):
        data=sample();data['Relationships'][0]['Target ID']='WG-9999'
        self.assertIn('Invalid relationship',str(validate(data)[0]))

    def test_redirect_chain_rejected(self):
        data=sample();data['Canonical View'][0]['Status']='LEGACY_DUPLICATE -> WG-0002'
        self.assertIn('Invalid redirect',str(validate(data)[0]))

    def test_new_staging_directory_and_integrity(self):
        data=sample()
        errors,warnings,counts,status,aliases,links=validate(data)
        self.assertEqual(errors,[])
        with tempfile.TemporaryDirectory() as folder:
            target=pathlib.Path(folder)/'staged'
            manifest=build_release(target,data,counts,status,aliases,links,'test-hash',warnings)
            self.assertEqual(manifest['release_status'],'staged-not-published')
            self.assertTrue((target/'terms.csv').exists())
            with sqlite3.connect(target/'wargaming_lexicon.sqlite') as conn:
                self.assertEqual(conn.execute('PRAGMA integrity_check').fetchone()[0],'ok')
                self.assertEqual(conn.execute('SELECT count(*) FROM terms').fetchone()[0],2)
                self.assertEqual(conn.execute('SELECT redirect_target FROM terms WHERE term_id="WG-0002"').fetchone()[0],'WG-0001')
                self.assertEqual(conn.execute('SELECT count(*) FROM term_search WHERE term_search MATCH "physical"').fetchone()[0],1)
            with self.assertRaises(ReleaseError):
                build_release(target,data,counts,status,aliases,links,'test-hash',warnings)


if __name__ == '__main__':
    unittest.main()
