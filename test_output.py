import os
import unittest

class TestModelOutput(unittest.TestCase):
    
    def test_timeseries_linecontents(self):
        with open('tests/compare.csv') as f:
            expected = f.read().splitlines()

        with open('outputs/test_full_run_Philippines/scenario_1/timeseries.csv') as f:
            new_set = f.read().splitlines()

        for expected_line, new_set_line in zip(expected, new_set):
            self.assertEqual(expected_line, new_set_line, msg = "Line has different value")

    def test_timeseries_line_length(self):
        with open('tests/compare.csv') as f:
            expected = f.read().splitlines()

        with open('outputs/test_full_run_Philippines/scenario_1/timeseries.csv') as f:
            new_set = f.read().splitlines()

        self.assertEqual(len(expected), len(new_set), msg = "Number of lines in timeseries differs")

if __name__ == '__main__':
    unittest.main()
