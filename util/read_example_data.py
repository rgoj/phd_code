import sys
sys.path.insert(0, 'briskbrain-code/scalingproject')
sys.path.insert(0, 'briskbrain-code/src')

from numpy import mean, cov, array
from scipy.io import loadmat

from data_import import avg_txt_import, SPSS_query


def rereference_to_average(data):
    for i in range(data.shape[0]):
        data[i] = data[i] - mean(data[i])
    return data


def read_danieles_data(nonEEG_electrodes=False, average_reference=True):
    data_path = '/home/stuff/projects/data/2012 Daniele ERPs (converted in ' +\
                'EEGLAB)/'

    subjects = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22,
                23, 24, 25, 26, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]

    ERPs = {}
    ERPs['left parietal'] = \
            {'within subject': {}, 
             'across subjects': {'hits': {}, 'correct rejections': {}}}
    ERPs['P3b'] = {'within subject': {}, 
                   'across subjects':  {'standard': {}, 'target': {}}}
    ERPs['N400'] = {'within subject': {}, 
                    'across subjects':  {'unrelated': {}, 'related': {}}}
    
    for subject in subjects:
        ERPs['left parietal']['within subject'][subject] = \
                {'hits': {}, 'correct rejections': {}}
        ERPs['P3b']['within subject'][subject] = \
                {'standard': {}, 'target': {}}
        ERPs['N400']['within subject'][subject] = \
                {'unrelated': {}, 'related': {}}

    electrodes = None

    for paradigm in ['left parietal', 'P3b', 'N400']:
        if paradigm == 'left parietal':
            path_paradigm = 'Left Parietal Final EEG Files Stirling/'
            condition_1 = ('hits', 'signal_hits')
            condition_2 = ('correct rejections', 'signal_correct_rejections')
        elif paradigm == 'P3b':
            path_paradigm = 'P3b Final EEG Files Stirling/'
            condition_1 = ('standard', 'signal_standard')
            condition_2 = ('target', 'signal_target')
        elif paradigm == 'N400':
            path_paradigm = 'N400 Final EEG Files Stirling/'
            condition_1 = ('unrelated', 'signal_unrelated')
            condition_2 = ('related', 'signal_related')
        
        subject_averages = {condition_1[0]: [], condition_2[0]: []}

        for subject in subjects:
            file_name =  'time_window_averages_subject_' + str(subject) + '.mat'
            
            mat_file = loadmat(data_path + path_paradigm + file_name)
            
            electrode_names = []
            for el_name in mat_file['electrode_names']:
                electrode_names.append(str(el_name).strip())
            if electrodes == None:
                electrodes = electrode_names
            elif electrodes != electrode_names:
                print('WARNING: Different electrodes!')

            if nonEEG_electrodes is True:
                accepted_electrodes = range(len(electrodes))
            else:
                accepted_electrodes = range(len(electrodes))
                accepted_electrodes.remove(electrodes.index('M1'))
                accepted_electrodes.remove(electrodes.index('M2'))
                accepted_electrodes.remove(electrodes.index('HEO'))
                accepted_electrodes.remove(electrodes.index('VEO'))

            if average_reference is True:
                ERPs[paradigm]['within subject'][subject][condition_1[0]] =\
                        rereference_to_average(mat_file[condition_1[1]][accepted_electrodes,:].T)
                ERPs[paradigm]['within subject'][subject][condition_2[0]] =\
                        rereference_to_average(mat_file[condition_2[1]][accepted_electrodes,:].T)
            else:
                print('WARNING: Not rereferencing to average!')
                ERPs[paradigm]['within subject'][subject][condition_1[0]] =\
                        mat_file[condition_1[1]][accepted_electrodes,:].T
                ERPs[paradigm]['within subject'][subject][condition_2[0]] =\
                        mat_file[condition_2[1]][accepted_electrodes,:].T
            
            subject_averages[condition_1[0]].append(\
                    mean(ERPs[paradigm]['within subject'][subject][condition_1[0]],0))
            subject_averages[condition_2[0]].append(\
                    mean(ERPs[paradigm]['within subject'][subject][condition_2[0]],0))
        
        ERPs[paradigm]['across subjects'][condition_1[0]] =\
                array(subject_averages[condition_1[0]])
        ERPs[paradigm]['across subjects'][condition_2[0]] =\
                array(subject_averages[condition_2[0]])
    
    final_electrodes = []
    for [i, electrode] in zip(range(len(electrodes)), electrodes):
        if i in accepted_electrodes:
            final_electrodes.append(electrode)

    return [ERPs, final_electrodes, subjects]


def read_brittanys_data():
    data_path = '/home/stuff/projects/data/2009 MSc Brittany ERPs/'
    # Area reports
    ERP_area = {'old': {}, 'new': {}}
    ERP_area_scaled = {'old': {}, 'new': {}}
    file_SPSS = data_path + 'Spss_Dataset_104_1936_PSI' +\
                        '_BrittanysCorrections_TwoMainTimeWindows.dat'
    ERP_area_baseline = {}
    file_SPSS_baseline = data_path + 'Spss_Dataset_104_1936_NONE' +\
                                 '_BrittanysCorrections_BaselineTimeWindows.dat'
    electrodes_read_area = {}
    electrodes_area = []

    [ERP_area['old']['300-500'], electrodes_read_area[1]] = \
                SPSS_query(file_SPSS, condition='11', time_window='1')
    [ERP_area['new']['300-500'], electrodes_read_area[2]] = \
                SPSS_query(file_SPSS, condition='12', time_window='1')
    [ERP_area['old']['500-700'], electrodes_read_area[3]] = \
                SPSS_query(file_SPSS, condition='11', time_window='2')
    [ERP_area['new']['500-700'], electrodes_read_area[4]] = \
                SPSS_query(file_SPSS, condition='12', time_window='2')

    [ERP_area_baseline['old'], electrodes_read_area[5]] = \
                SPSS_query(file_SPSS_baseline, condition='11')
    [ERP_area_baseline['new'], electrodes_read_area[6]] = \
                SPSS_query(file_SPSS_baseline, condition='12')

    data = ERP_area['new']['300-500']
    rereference_to_average(data)

    mean_data = mean(data,0)
    cov_data = cov(data.transpose())

    electrodes = electrodes_read_area[2]

    return [data, mean_data, cov_data, electrodes]
