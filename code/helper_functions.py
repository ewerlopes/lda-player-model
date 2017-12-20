"""
Ewerton Lopes, Copyright 2017.
All rights reserved.
"""

import csv
import os
import numpy as np
from collections import defaultdict

def getListOfFiles(directory, extension):
    """
    Get a list of all files with a certain extension inside a given directory.
    
    :param directory : the csv files directory
    :param extension : the file extension, i.e., '.csv.'
    :return          : the list of files inside the directory.
    """
    allFiles = [f for f in os.listdir(directory) if
                os.path.isfile(os.path.join(directory, f)) and f.endswith(extension)]
    return allFiles


def representsFloat(s):
    """
    Check whether a string can be converted to float.
    :param s:   A string.
    :return:    True if s can be converted. False, otherwise.
    """
    try:
        float(s)
        return True
    except ValueError:
        return False

def getCSV(filename, reference_column="time", windows_separator=""):
    """
    Open a csv file and return the data in a dictionary where each key is
    a corresponding csv column name and each value for the key correspond to
    a list of the windows data. Each data windows is a list.
    :param filename             :   the name of the csv file to open.
    :reference_column           :   the column name used to analyse the data.
    :param windows_separator    :   the token that separates the windows in the csv file.
                                     the default "" correspond to blank csv line. In the csv
                                     file, something like ",,,,,".
    :return                    :   the data as a dictionary.
    """
    reader = csv.DictReader(open(filename))
    csv_data = {}
    for row in reader:
        for col, value in row.iteritems():
            csv_data.setdefault(col, []).append(value)

    if reference_column not in csv_data.keys():
        raise ValueError('Reference column name {} not in the {} csv file. Aborting.'
                         .format(reference_column, filename))

    # get windows separation line numbers.
    reference_points = [i for i, v in enumerate(csv_data[reference_column]) if v == windows_separator]

    if not reference_points:
        raise ValueError('Windows separator has not been found in {} csv file. Aborting.'
                         .format(reference_column, filename))

    result = defaultdict(list)
    for i, r in enumerate(reference_points):
        for col in csv_data.keys():
            if i == 0:
                #result[col].append([csv_data[col][v] for v in range(r)])
                accumulator = []
                for v in range(r):
                    if representsFloat(csv_data[col][v]):
                        accumulator.append(round(float(csv_data[col][v]), 2))
                    elif csv_data[col][v] == '':
                        accumulator.append(None)
                    else:
                        accumulator.append(csv_data[col][v])
                result[col].append(accumulator)
            else:
                #result[col].append([csv_data[col][v] for v in range(reference_points[i - 1] + 1, r)])
                accumulator = []
                for v in range(reference_points[i - 1] + 1, r):
                    if representsFloat(csv_data[col][v]):
                        accumulator.append(round(float(csv_data[col][v]), 2))
                    elif csv_data[col][v] == '':
                        accumulator.append(None)
                    else:
                        accumulator.append(csv_data[col][v])
                result[col].append(accumulator)

    number_windows = len(reference_points)
    return (number_windows, result)

def getStatistics(data, reference_column="time", compareWith=50):
    """Checks the amount of overlap between windows
    :param data          :   the csv data.
    :param reference_column : used to get statistics.
    :param compareWith      :   the percentage from which to compare
                                 the amount of overlap.
    :return overlaps       :   a list where each value corresponds to
                                 the amount of overlap for the windows.
    :return meanOfOverlaps : the mean overlap value
    :return meanDeviation  : the mean deviation value.
    """
    overlaps_diff = []
    overlaps = []
    sample_info = {}
    s_info = defaultdict(list)
    n_windows = len(data[reference_column])
    for i in range(n_windows):
        if i != n_windows - 1:
            if data[reference_column][i] == [] or data[reference_column][i+1] == []:
                raise ValueError("\tFile has empty tagged windows. Skipping...")
            overlap = len(set(data[reference_column][i]) & set(data[reference_column][i + 1])) / \
                      float(len(set(data[reference_column][i + 1]))) * 100
            overlaps.append(overlap)
            overlaps_diff.append(overlap - compareWith)

        for k in data.keys():
            s_info[k].append(sum([1 for j in data[k][i] if j != ""]))

    for k in data.keys():
        sample_info[k] = np.mean(s_info[k])

    return overlaps, n_windows, sample_info, np.mean(overlaps), np.mean(overlaps_diff)

def removeMissingData(data, missing_token=""):
    """
    Remove missing data.
    :param  data         :   the list of data
    :param missing_token :   the character used for missing data.
    :return:                the data without missing values.
    """
    return map(lambda x: int(x), filter(lambda v: v != missing_token, data))

def remap_interval(value, oldMin, oldMax, newMin, newMax):
    """Remap from an interval to another"""
    
    # Figure out how 'wide' each range is
    oldSpan = oldMax - oldMin
    newSpan = newMax - newMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - oldMin) / float(oldSpan)

    # Convert the 0-1 range into a value in the right range.
    return newMin + (valueScaled * newSpan)