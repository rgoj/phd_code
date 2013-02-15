from string import join
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


def generate_accepted_electrodes(electrodes, electrodes_to_remove):
    # Remove these electrodes:
    # ['M1', 'M2', 'HEO', 'VEO', 'CB1', 'CB2']
    accepted_electrodes = range(len(electrodes))
    for el in electrodes_to_remove:
        accepted_electrodes.remove(electrodes.index(el))
    
    final_electrodes = []
    for [i, electrode] in zip(range(len(electrodes)), electrodes):
        if i in accepted_electrodes:
            final_electrodes.append(electrode)

    return [accepted_electrodes, final_electrodes]


def read_danieles_data(nonEEG_electrodes=False, average_reference=True,
                       time_window=True):
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

        if time_window is False:
            cond = condition_1[1].split('_')
            cond.insert(1,'eeg')
            condition_1 = (condition_1[0], join(cond,'_'))
            cond = condition_2[1].split('_')
            cond.insert(1,'eeg')
            condition_2 = (condition_2[0], join(cond,'_'))
        
        subject_averages = {condition_1[0]: [], condition_2[0]: []}

        for subject in subjects:
            if time_window is True:
                file_name =  'time_window_averages_subject_' + str(subject) + '.mat'
            else:
                file_name =  'full_eeg_subject_' + str(subject) + '.mat'
            
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
                [accepted_electrodes, final_electrodes] = \
                        generate_accepted_electrodes(electrodes, \
                        ['M1', 'M2', 'HEO', 'VEO', 'CB1', 'CB2'])
            
            for cond_name in [condition_1,condition_2]:
                if time_window is True:
                    signal = mat_file[cond_name[1]][accepted_electrodes,:].T
                    if average_reference is True:
                        signal = rereference_to_average(signal)
                    else:
                        print('WARNING: Not rereferencing to average!')
                else:
                    print('WARNING: Not rereferencing to average!')
                    signal = mat_file[cond_name[1]][accepted_electrodes,:,:]
                
                ERPs[paradigm]['within subject'][subject][cond_name[0]] = signal
                if time_window is True:
                    subject_averages[cond_name[0]].append(mean(signal,0))
                else:
                    subject_averages[cond_name[0]].append(mean(signal,2))
                
        for cond_name in [condition_1,condition_2]:
            ERPs[paradigm]['across subjects'][cond_name[0]] =\
                    array(subject_averages[cond_name[0]])

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
    
    electrodes = electrodes_read_area[2]
    [accepted_electrodes, final_electrodes] = \
            generate_accepted_electrodes(electrodes, \
            ['CB1', 'CB2'])
    
    data = data[:,accepted_electrodes]

    rereference_to_average(data)

    mean_data = mean(data,0)
    cov_data = cov(data.transpose())

    return [data, mean_data, cov_data, final_electrodes]
