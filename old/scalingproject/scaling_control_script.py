# roman goj
# 18/11/2010
"""
a script for managing the scaling experiments.

"""
from __future__ import division

import sys
from os import mkdir, makedirs, path
from copy import deepcopy
from numpy import mean, std, pi, square, sqrt
from scipy.stats.stats import pearsonr
from matplotlib.pyplot import figure, savefig
from datetime import datetime
from prettytable import PrettyTable
from sumatra.parameters import build_parameters
from dataimport import avg_txt_import, SPSS_query
from scaling import perform_scaling, test_scaling
from anova import run_anova, select_electrodes
from assumptions import test_assumptions
from erpplot import plot_ERP
from topographicmap import plot_topographic_map, plot_topographic_map_array,\
                           read_electrode_locations
from simulation import random_generator_configuration, gen_simulation
from ScalingExperiment import ScalingExperiment
from SimulationBrowserGUI import SimulationBrowserGUI

######################
# Reading parameters #
######################

parameters = build_parameters(sys.argv[1])
default_parameters = deepcopy(parameters)

########################################################
# Creating a timestamp or reading it from command line #
########################################################

#if len(sys.argv) < 3:
#    mkdir('Results/' + timestamp)
#    mkdir('Results/' + timestamp + '/topographies')
#else:
#    timestamp = sys.argv[2]

# If not run from sumatra (currently doesn't put data into a timestamp folder though!
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

# If run from sumatra
label = sys.argv[-1]

####################
# Helper functions #
####################

def examine_data(data, electrodes, indices, name):
    print('\n\n\n' + name)
    print('Data consists of: ' + str(data.shape[0]) + ' subjects and ' +\
          str(data.shape[1]) + ' electrodes\n')

    
    # Examine values for single subjects
    column_names = [electrodes[index] for index in indices]
    column_names.insert(0, 'Subject')
    column_names.append(' ')
    column_names.append(' ')
    subjectvalues = PrettyTable(column_names)
    for i in range(data.shape[0]):
        row = [str(round(data[i,index],4))[0:8] for index in indices]
        row.insert(0,i)
        if i != data.shape[0]-1:
            row.append(' ')
            row.append(' ')
        else:
            row.append('MEAN')
            row.append('STD DEV')
        subjectvalues.add_row(row)
    
    electrode_means = mean(data,0)
    electrode_stddevs = std(data,0)
    electrode_range = []
    for i in range(data.shape[1]):
        electrode_range.append(max(data[:,i]) - min(data[:,i]))
    
    row = [str(round(electrode_means[index],4))[0:8] for index in indices]
    row.insert(0, 'Mean')
    row.append(str(round(mean(electrode_means),4))[0:8])
    row.append(str(round(std(electrode_means),4))[0:8])
    subjectvalues.add_row(row)
    row = [str(round(electrode_stddevs[index],4))[0:8] for index in indices]
    row.insert(0, 'Std Dev')
    row.append(str(round(mean(electrode_stddevs),4))[0:8])
    row.append(str(round(std(electrode_stddevs),4))[0:8])
    subjectvalues.add_row(row)
    row = [str(round(electrode_range[index],4))[0:8] for index in indices]
    row.insert(0, 'Range')
    row.append(str(round(mean(electrode_range),4))[0:8])
    row.append(str(round(std(electrode_range),4))[0:8])
    subjectvalues.add_row(row)
    
    subjectvalues.printt(border=False)
    
    # Correlation between electrode mean and standard deviation
    figure()
    from matplotlib import pyplot
    pyplot.subplot(211)
    pyplot.plot(electrode_means, electrode_stddevs, '.')
    pyplot.xlabel('Electrode mean')
    pyplot.ylabel('Electrode standard deviation')
    pyplot.title(name)
    [coefficient, pvalue] = pearsonr(electrode_means, electrode_stddevs)
    print('\nCorrelation between mean and standard deviation, coefficient: ' +\
          str(coefficient) + ', significance value: ' + str(pvalue))
    
    # Correlation (across subjects) between electrodes depending on distance
    # between the electrodes
    pyplot.subplot(212)
    electrode_correlations = []
    electrode_distances = []
    [electrodes_file, pos_x, pos_y, pos_theta, pos_phi] = \
            read_electrode_locations()
    for electrode1 in range(data.shape[1]):
        for electrode2 in range(data.shape[1]):
            #if electrode1 <= electrode2:
            #    break
            [coefficient, pvalue] = pearsonr(data[:,electrode1], data[:,electrode2])
            electrode_correlations.append(coefficient)
            distance = sqrt(square(pos_x[electrode1] - pos_x[electrode2])
                            + square(pos_y[electrode1] - pos_y[electrode2]))
            electrode_distances.append(distance)
    pyplot.plot(electrode_distances, electrode_correlations, '.')
    pyplot.xlabel('Distance between two electrodes')
    pyplot.ylabel('Correlation between two\nelectrodes across subjects')


################################
# Going through all procedures #
################################

if parameters['todo_import_data']:
    print('Importing experimental ERP data')

    # Grand averages
    ERP_avg = {}
    electrodes_read_avg = {}
    electrodes_avg = []
    data_path = '/home/stuff/projects/data/2009 MSc Brittany ERPs/'
    [ERP_avg['old'], electrodes_read_avg[1]] = \
        avg_txt_import(data_path + 'grandAvgOld.dat')
    [ERP_avg['new'], electrodes_read_avg[2]] = \
        avg_txt_import(data_path + 'grandAvgNew.dat')
                    
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
    
    # Preparing lists of electrodes
    if electrodes_read_avg[1] == electrodes_read_avg[2]:
        electrodes_avg = electrodes_read_avg[1]
    for key in electrodes_read_area.keys():
        if electrodes_read_area[key] == electrodes_read_area[1]:
            electrodes_area = electrodes_read_area[1]
        else:
            electrodes = None
            print('Electrode mismatch in ERP data files')
            break
 
    electrode_indices = select_electrodes(parameters['hemispheres'], 
                                          parameters['sites'], 
                                          parameters['locations'],
                                          electrodes_area)[4]

    for key1 in ERP_area.keys():
        for key2 in ERP_area[key1].keys():
            # NOTE: Copy is done inside perform_scaling
            ERP_area_scaled[key1][key2] = perform_scaling(ERP_area[key1][key2],
                                                          electrode_indices)
            # TODO: This should be done as a unit test probably
            if test_scaling(ERP_area_scaled[key1][key2], electrode_indices):
                print('A problem with scaling has been detected')


if parameters['todo_test_assumptions_data']:
    print('Performing assumption tests on ERP data')
    
    # This is temporary, but works
    data1 = ERP_area['old']['300-500']
    data2 = ERP_area['new']['300-500']
    
    test_assumptions(parameters['hemispheres'], parameters['sites'], parameters['locations'], data1, data2,
                     electrodes_area, name='testu')


if parameters['todo_run_anovas_data']:
    print('Performing anovas on ERP data')
    
    # This is temporary, but works
    data1 = ERP_area['old']['300-500']
    data2 = ERP_area['new']['300-500']
 
    for factor in ['hsl', 'electrodes']:
        if factor == 'hsl':
            doElectrodesAsFactor = False
        elif factor == 'electrodes':
            doElectrodesAsFactor = True
        
        if parameters['todo_anova_' + factor]:
            [anova_results, electrodeIndices] = \
                run_anova(parameters['hemispheres'], parameters['sites'], 
                          parameters['locations'], data1, data2, 
                          electrodes_area, doElectrodesAsFactor, 
                          printResults=True, name='testu')


if parameters['todo_plot_data_topographies']:
    print('Drawing topographic maps for all imported data')
    
    map_array = [[ERP_area['old']['300-500'], ERP_area['new']['300-500'],
                  ERP_area['old']['300-500'] - ERP_area['new']['300-500']],
                 [ERP_area['old']['500-700'], ERP_area['new']['500-700'],
                  ERP_area['old']['500-700'] - ERP_area['new']['500-700']]]
    
    title_array = [['Old', 'New', 'Old - New'], [False, False, False]]
    label_y_array = [['300-500 ms', False, False], 
                     ['500-700 ms', False, False]]
    scale_array = [[False, False, True], [False, False, True]]

    figure()
    plot_topographic_map_array(map_array, scale=scale_array, 
                               label_y=label_y_array, title=title_array)
    folder = 'Results/' + label + '/data_topographies'
    if not path.exists(folder):
        makedirs(folder)
    savefig(folder + '/average.png')

    for i in range(23):
        map_array = [[ERP_area['old']['300-500'][i], 
                      ERP_area['new']['300-500'][i],
                      ERP_area['old']['300-500'][i] -\
                      ERP_area['new']['300-500'][i]],
                     [ERP_area['old']['500-700'][i], 
                      ERP_area['new']['500-700'][i],
                      ERP_area['old']['500-700'][i] -\
                      ERP_area['new']['500-700'][i]]]
        figure()
        plot_topographic_map_array(map_array, scale=scale_array, 
                                   label_y=label_y_array, title=title_array)
        savefig(folder + '/subject_' + str(i+1) + '.png')



if parameters['todo_plot_grand_averages']:
    print('Drawing grand averages for all imported data')
    figure()
    plot_ERP(ERP_avg['old'][0])


if parameters['todo_plot_simulated_noise']:
    print('Running simulation to show topographic properties of noise')
    gen_conf = random_generator_configuration()
    [simulated_data, gen_conf, electrodes] =\
            gen_simulation(gen_conf, num_sim=parameters['number_of_subjects'],
            gen_magnitude_stddev=parameters['generator_magnitude_stddev'])
    figure()
    plot_topographic_map(mean(simulated_data,0))
    #savefig('Results/' + timestamp + '/simulated_noise')
    savefig('Results/' + label + '/simulated_noise')


# Here we will be running the scaling experiments
# se <-- holds all simulation experiments, for all parameter combinations
se = {}

# All simulation experiment parameters we will be looping through
experiments = [1, 2, 3, 4]
configurations = ['random', 'uandk']
variabilities = ['scaling', 'gen_amplitude', 'gen_location']
noise_types = ['normal_only', 'constant_and_normal','topographic_and_normal']
references = ['none', 'left_mastoid', 'average_mastoid', 'average']
factors = ['hsl', 'electrodes']
combinations = [(x, y, z, u, v, w) for x in experiments \
                                for y in configurations \
                                for z in variabilities \
                                for u in noise_types \
                                for v in references \
                                for w in factors]

param_dict = parameters.as_dict()

# This loop just creates empty lists in the se dictionaries
# gen_se <-- holds information whether generators have been simulated for a
#            particular combination of experiment, configuration and 
#            variability parameters
# noise_se <-- holds information whether generators and noise have been 
#              simulated for a particular combination of generator and noise
#              parameters (everything other than reference and factor)
gen_se = {}
noise_se = {}
for experiment in experiments:
    se[experiment] = {}
    gen_se[experiment] = {}
    noise_se[experiment] = {}
    for configuration in configurations:
        se[experiment][configuration] = {}
        gen_se[experiment][configuration] = {}
        noise_se[experiment][configuration] = {}
        for variability in variabilities:
            se[experiment][configuration][variability] = {}
            gen_se[experiment][configuration][variability] = None
            noise_se[experiment][configuration][variability] = {}
            for noise_type in noise_types:
                se[experiment][configuration][variability][noise_type] = {}
                noise_se[experiment][configuration][variability][noise_type] = None
                for reference in references:
                    se[experiment][configuration][variability][noise_type]\
                      [reference] = {}
                    for factor in factors:
                        se[experiment][configuration][variability][noise_type]\
                          [reference][factor] = []

# This is the main loop through all simulation parameters
for experiment, configuration, variability, noise_type, reference, factor \
        in combinations:
    # Break if this parameter combination is not to be run
    if not param_dict['todo_run_simulation_experiment_' + str(experiment)] or\
       not param_dict['todo_configurations_' + configuration] or\
       not param_dict['todo_variability_' + variability] or\
       not param_dict['todo_noise_type_' + noise_type] or\
       not param_dict['todo_reference_' + reference] or\
       not param_dict['todo_anova_' + factor]:
        continue

    # If possible and if so specified reusing data from previous simulations
    if param_dict['todo_reuse']:
        if noise_se[experiment][configuration][variability]\
                   [noise_type] != None:
            print('\n\n\nREUSING GENERATORS AND NOISE!\n\n\n')
            run_generators = False
            run_noise = False
            se[experiment][configuration][variability][noise_type][reference]\
              [factor] = deepcopy(noise_se[experiment][configuration]\
                                          [variability][noise_type])
        elif gen_se[experiment][configuration][variability] != None:
            print('\n\n\nREUSING GENERATORS!\n\n\n')
            run_generators = False
            run_noise = True
            se[experiment][configuration][variability][noise_type][reference]\
              [factor] = deepcopy(gen_se[experiment][configuration]\
                                        [variability])
        else:
            run_generators = True
            run_noise = True
    else:
        run_generators = True
        run_noise = True

    # Setting simulation experiment parameter values
    if noise_type == 'topographic_and_normal':
        topographic_noise_amplitude = param_dict['topographic_noise_amplitude']
        constant_noise_amplitude = False
    elif noise_type == 'constant_and_normal':
        topographic_noise_amplitude = False
        constant_noise_amplitude = param_dict['constant_noise_amplitude']
    elif noise_type == 'normal_only':
        topographic_noise_amplitude = False
        constant_noise_amplitude = False
    if variability == 'scaling':
        normal_noise_amplitude = param_dict['normal_noise_amplitude']
        generator_magnitude_stddev = 0
    elif variability == 'gen_amplitude':
        normal_noise_amplitude = 0.1
        generator_magnitude_stddev = param_dict['generator_magnitude_stddev']
    
    # Setting the parameters of preexisting simulations to reuse them or else
    # creating a new SimulationExperiment instance and setting parameters
    if param_dict['todo_reuse'] and (noise_se[experiment][configuration]\
            [variability][noise_type] != None or gen_se[experiment]\
            [configuration][variability] != None):
        se[experiment][configuration][variability][noise_type][reference]\
          [factor].generator_magnitude_stddev = generator_magnitude_stddev
        se[experiment][configuration][variability][noise_type][reference]\
          [factor].normal_noise_amplitude = normal_noise_amplitude
        se[experiment][configuration][variability][noise_type][reference]\
          [factor].constant_noise_amplitude = constant_noise_amplitude
        se[experiment][configuration][variability][noise_type][reference]\
          [factor].topographic_noise_amplitude = topographic_noise_amplitude
        se[experiment][configuration][variability][noise_type][reference]\
          [factor].configuration = configuration
        se[experiment][configuration][variability][noise_type][reference]\
          [factor].reference = reference
        se[experiment][configuration][variability][noise_type][reference]\
          [factor].factor = factor
    else:
        se[experiment][configuration][variability][noise_type][reference]\
          [factor] = ScalingExperiment(experiment, 
                                       param_dict['todo_debug'],
                                       param_dict['todo_collect'],
                                       param_dict, None,
                                       generator_magnitude_stddev,
                                       normal_noise_amplitude,
                                       constant_noise_amplitude,
                                       topographic_noise_amplitude,
                                       configuration, reference, factor)
    
    # Running simulation experiment
    print('\n\n\nRunning experiment ' + str(experiment) +
          '\nwith configuration: ' + configuration +
          ',\nvariability: ' + str(variability) + 
          ',\nnoise type: ' + str(noise_type) + 
          ',\nrereferenced to: ' + reference +
          ',\nwith factors: ' + factor + '\n\n\n')
    se[experiment][configuration][variability][noise_type]\
      [reference][factor].run(run_generators, run_noise)
    
    if parameters['todo_examine_noise_simulations']:
        name = str(experiment) + '' + configuration + '' + variability + '' +\
               noise_type + '' + reference + '' + factor
        print('Condition 1:')
        examine_data(se[experiment][configuration][variability][noise_type]
                     [reference][factor].simulated_data_1[0], electrodes_area,\
                     electrode_indices, name)
        print('Condition 2:')
        examine_data(se[experiment][configuration][variability][noise_type]
                     [reference][factor].simulated_data_2[0], electrodes_area,\
                     electrode_indices, name)
    
    # Saving simulations and noise for later reuse if necessary
    if param_dict['todo_reuse']:
        if noise_se[experiment][configuration][variability]\
                   [noise_type] == None:
            print('\n\n\nSAVING GENERATORS AND NOISE FOR REUSE!\n\n\n')
            noise_se[experiment][configuration][variability][noise_type] =\
                    deepcopy(se[experiment][configuration][variability]\
                               [noise_type][reference][factor])
        if gen_se[experiment][configuration][variability] == None:
            print('\n\n\nSAVING GENERATORS FOR REUSE!\n\n\n')
            gen_se[experiment][configuration][variability] =\
                    deepcopy(se[experiment][configuration][variability]\
                               [noise_type][reference][factor])


if parameters['todo_examine_noise_data']:
    name = 'Condition: OLD, Time Window: 300-500'
    data = ERP_area['old']['300-500']
    examine_data(data, electrodes_area, electrode_indices, name)
    name = 'Condition: OLD, Time Window: 500-700'
    data = ERP_area['old']['500-700']
    examine_data(data, electrodes_area, electrode_indices, name)
    name = 'Condition: NEW, Time Window: 300-500'
    data = ERP_area['new']['300-500']
    examine_data(data, electrodes_area, electrode_indices, name)
    name = 'Condition: NEW, Time Window: 500-700'
    data = ERP_area['new']['500-700']
    examine_data(data, electrodes_area, electrode_indices, name)


#if parameters['todo_examine_noise_simulations']:
#    if parameters['todo_variability_scaling'] == True:
#        name = 'Simulated data. Noise: Normal noise at electrode level'
#        example = se[1]['scaling']['normal_only']['random'].simulated_data_1[0]
#        examine_data(example, electrodes_area, electrode_indices, name)
#    if parameters['todo_variability_gen_amplitude'] == True:
#        name = 'Simulated data. Noise: Generator amplitude'
#        example = se[1]['gen_amplitude']['normal_only']['random'].simulated_data_1[0]
#        examine_data(example, electrodes_area, electrode_indices, name)


# This isn't working!
if parameters['todo_browse_simulations']:
    boo = se[1]['gen_amplitude']['normal_only']['random']
    app = SimulationBrowserGUI(boo)
    app.MainLoop()
    

if parameters['todo_import_show']:
    from matplotlib.pyplot import show


def plot_all_simulated_topographies(se, simulation=0, subject=False):
    for experiment, configuration, variability, noise_type, reference, factor\
            in combinations:
        # Break if this parameter combination is not to be run
        if not param_dict['todo_run_simulation_experiment_' + str(experiment)]\
           or not param_dict['todo_configurations_' + configuration] or\
           not param_dict['todo_variability_' + variability] or\
           not param_dict['todo_noise_type_' + noise_type] or\
           not param_dict['todo_reference_' + reference] or\
           not param_dict['todo_anova_' + factor]:
            continue

        folder = 'Results/' + label + '/topographies'
        file = str(experiment) + '_' + configuration + '_' + variability +\
                '_' + noise_type + '_' + reference + '_' + factor
        if not path.exists(folder):
            makedirs(folder)
        se[experiment][configuration][variability][noise_type]\
          [reference][factor].plot_topographies(simulation, subject=subject,\
                                               folder=folder, file=file)
        se[experiment][configuration][variability][noise_type]\
          [reference][factor].plot_topography_line(simulation, folder=folder, 
                                                   file=file)
        #savefig('Results/' + label + '/simulated_noise')


if parameters['todo_plot_simulated_topographies']:
    subject = parameters['plot_simulated_topographies_subject']
    for i in range(parameters['plot_simulated_topographies_number']):
        plot_all_simulated_topographies(se, simulation=i, subject=subject)

