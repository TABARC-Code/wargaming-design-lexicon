import unittest
from verify_frozen_ids import compare_rows
from export_master import ReleaseError


class HistoricalIdsTests(unittest.TestCase):
    def sample(self):
        return [{'ID': 'WG-0001', 'Term': 'Model'},
                {'ID': 'WG-0002', 'Term': 'Movement'}]

    def test_additional_terms_are_allowed(self):
        current = self.sample() + [{'ID': 'WG-0003', 'Term': 'Cover'}]
        result = compare_rows(self.sample(), current)
        self.assertEqual(result['new_wg_identifiers'], 1)
        self.assertEqual(result['inherited_rows_with_changed_fields'], 0)

    def test_updated_text_is_reported(self):
        current = self.sample()
        current[1]['Term'] = 'Movement allowance'
        result = compare_rows(self.sample(), current)
        self.assertEqual(result['field_change_counts']['Term'], 1)

    def test_missing_identifier_rejected(self):
        with self.assertRaises(ReleaseError):
            compare_rows(self.sample(), [{'ID': 'WG-0001', 'Term': 'Model'}])

    def test_reordered_identifier_rejected(self):
        with self.assertRaises(ReleaseError):
            compare_rows(self.sample(), list(reversed(self.sample())))

    def test_duplicate_identifier_rejected(self):
        with self.assertRaises(ReleaseError):
            compare_rows(self.sample(), self.sample() + [self.sample()[0]])

    def test_inserted_before_frozen_ids_rejected(self):
        current = [self.sample()[0], {'ID': 'WG-9999', 'Term': 'Extra'}, self.sample()[1]]
        with self.assertRaises(ReleaseError):
            compare_rows(self.sample(), current)


if __name__ == '__main__':
    unittest.main()
