#Roman Goj
# 23/11/2010
"""
This module contains functions for importing data from Neuroscan AVG files and
AutoERP generated SPSS files.

"""
import csv
from numpy import array, mean


def avg_txt_import(filename, electrodes=True):
    """Reads in an ERP average exported to a text file by Neuroscan. If the
    text files contains labels, set the electrodes parameter to True, if not
    set it to False. Unfortunately this doesn't read in headers. Also if the
    electrodes were exported with square brackets ('[' ']'), reading in the
    electrodes will fail and the electrodes will need to be removed from the
    .avg file. So this function may or may not work for a particular exported
    avg file.

    """
    reader = csv.reader(open(filename, "rb"), dialect='excel-tab')

    data = []
    channels = []

    for row in reader:
        if electrodes and reader.line_num == 1:
            for entry in row:
                if entry.strip() != '':
                    channels.append(entry.strip())
                    data.append([])
        else:
            ichannel = 0
            for entry in row:
                if electrodes is False and reader.line_num ==1:
                    data.append([])
                if entry !='':
                    data[ichannel].append(float(entry))
                    ichannel += 1

    if electrodes is False:
        data.pop()
    
    return [array(data).T, channels]


def SPSS_import(filename):
    """Reads in all the data, column headings and subject numbers from the SPSS
    file created by AutoERP.
    
    It is then the role of the querySPSSData() function to retrieve the needed
    parts of the data.

    """
    reader = csv.reader(open(filename, "rb"), delimiter=' ')

    column_names = []
    subject_numbers = []
    data = []

    for row in reader:
        if reader.line_num == 1:
            column_names = row
        else:            
            subject_numbers.append(int(row[0]))
            data.append(map(float, row[1:]))

    data = array(data)

    return [column_names, subject_numbers, data]


def SPSS_query(filename, condition='11', time_window='1',
               electrodes=0, subjects=0):
    """Reads in all the data and returns only the specified subjects,
    electrodes, condition and time window

    """
    [file_column_names, file_subject_numbers, file_data] = \
        SPSS_import(filename)
    
    # File columns correspond to electrodes, so we pick only those columns that
    # correspond to the electrodes we are interested in.
    columns = []
    if electrodes == 0:
        # Reading in all electrodes
        electrodes = []
        for column_heading in file_column_names:
            target_column_heading = condition + time_window + '_'
            if target_column_heading == column_heading[0:4]:
                columns.append(file_column_names.index(column_heading) - 1)
                electrodes.append(column_heading[4:])
    else:
        # Reading in only specific electrodes
        for electrode in electrodes:
            target_column_heading = condition + time_window + '_' + electrode
            columns.append(file_column_names.index(column_heading) - 1)
        columns.sort()

    subject_indices = []
    if subjects == 0:
        # Reading in all subjects
        subject_indices = range(file_data.shape[0])
        subjects = file_subject_numbers
    else:
        # Reading in only specific subjects
        for subject in subjects:
            subject_indices.append(subject_numbers.index(subject))

    query = file_data[:,columns]
    data = query[subject_indices,:]
    
    # TODO: Do we really need to return all this?
    # return [data, subjects, condition, time_window, electrodes, columns,
    #        subject_indices, file_column_names, file_subject_numbers]
    return [data, electrodes]
