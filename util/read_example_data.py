import sys
sys.path.insert(0, 'briskbrain-code/scalingproject')
sys.path.insert(0, 'briskbrain-code/src')

from numpy import mean, cov

from data_import import avg_txt_import, SPSS_query


def rereference_to_average(data):
    for i in range(data.shape[0]):
        data[i] = data[i] - mean(data[i])


def read_example_data():
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

    return [data, mean_data, cov_data]
