#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Ewerton Lopes
# Politecnico di Milano, December, 2016.
import unittest
import csv
import os
from helper_functions import getCSV, getListOfFiles


csv_dir = "../data"
files = getListOfFiles(csv_dir, ".csv")


class CSVRetrievalTestCase(unittest.TestCase):
    """Tests the data retrieval for `data_summary.py`"""

    def loadCSV(self, filename):
        """
        Opens csv and return the data as a dictionary
        :param filename: the csv file to be open
        :return: the dictionary whose key is the column name in the csv and
                 the value is a list with the data for the column.
        """
        reader = csv.DictReader(open(filename))
        csv_data = {}
        for row in reader:
            for col, value in row.iteritems():
                csv_data.setdefault(col, []).append(value)
        return csv_data

    def test_retrieval(self):
        """Is the list of windows successfully retrieved?"""

        for f in files[:1]:
            filename = os.path.join(csv_dir,f)
            loaded_csv = self.loadCSV(filename)
            nwin , data = getCSV(filename)
            csv_windows_separator = ""

            ## Checks whether the getCSV return is the same
            # as the original data. That is, checks weather
            # the windows retrieval is correct.
            # print filename
            for key in data.keys():
                restored = []
                for l in data[key]:
                    r = []
                    for i in l:
                        if i is None:
                            r.append("")
                        else:
                            r.append(i)
                    restored += r + [csv_windows_separator]
                self.assertEqual(restored, loaded_csv[key])
                print key

    def test_reference_error(self):
        """Does it throws a ValueError when the referenceColumn is not in the csv?"""
        filename = os.path.join(csv_dir, files[0])
        reference_column = "ThisFails"

        with self.assertRaises(ValueError):
            _ = getCSV(filename, reference_column=reference_column)

    def test_separator_error(self):
        """Does it throws a ValueError when the windows separator is not in the csv?"""
        filename = os.path.join(csv_dir, files[0])

        with self.assertRaises(ValueError):
            _ = getCSV(filename, windows_separator="???")

if __name__ == '__main__':

    unittest.main()