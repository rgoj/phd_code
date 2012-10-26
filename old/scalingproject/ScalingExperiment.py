# Roman Goj
# 15/01/2011
from __future__ import division

from copy import deepcopy
from numpy import mean, ones, array
from matplotlib import pyplot
from numpy.random import normal, uniform
from scaling import perform_scaling, test_scaling, create_scaled_data_structure
from anova import run_anova, select_electrodes
from simulation import random_generator_configuration, \
        scale_generator_configuration, gen_simulation
from topographicmap import plot_simulated_topographies


class ScalingExperiment:
    def __init__(self, experiment, debug=False, collect=False,
                 parameters=None, parameter_file=None,
                 generator_magnitude_stddev=1800.28,
                 normal_noise_amplitude=3.28,
                 constant_noise_amplitude=2.5,
                 topographic_noise_amplitude=1.0,
                 configuration='random',
                 reference='none',
                 factor='hsl'):
        self.experiment = experiment
        
        self.debug = debug
        self.collect = collect
        
        if parameter_file != None:
            parameters = build_parameters(parameter_file)
        elif parameters == None:
            print('No parameter file or parameter dictionary given')
        
        # Experiment-specific parameters
        self.experiment_1_magnitude_multiplier =\
            parameters['experiment_1_magnitude_multiplier']
        self.experiment_2_limits_number =\
            parameters['experiment_2_limits_number']
        if self.experiment == 2:
            self.limits_number = self.experiment_2_limits_number
        else:
            self.limits_number = parameters['limits_number']

        # Parameters for all experiments
        self.limits_depth = parameters['limits_depth']
        self.limits_orientation = parameters['limits_orientation']
        self.limits_magnitude = parameters['limits_magnitude']
        self.final_magnitude = parameters['final_magnitude']
        self.number_of_subjects = parameters['number_of_subjects']
        self.number_of_simulations = parameters['number_of_simulations']
        
        # Parameters for statisctical analysis with ANOVA
        self.hemispheres = parameters['hemispheres']
        self.sites = parameters['sites']
        self.locations = parameters['locations']
        if factor == 'electrodes':
            self.doElectrodesAsFactor = True
        else:
            self.doElectrodesAsFactor = False
        
        # Noise and variability parameters
        self.generator_magnitude_stddev = generator_magnitude_stddev
        self.normal_noise_amplitude = normal_noise_amplitude
        self.constant_noise_amplitude = constant_noise_amplitude
        self.topographic_noise_amplitude = topographic_noise_amplitude
        self.configuration = configuration
        self.reference = reference

        # These are meant to store simulation results if self.collect==True
        self.gen_conf_1 = []
        self.gen_conf_2 = []
        self.simulated_gen_1 = []
        self.simulated_gen_2 = []
        self.electrodes = None
        self.electrode_indices = None
        self.normal_noise_1 = []
        self.normal_noise_2 = []
        self.constant_noise = []
        self.topographic_noise_1 = []
        self.topographic_noise_2 = []
        self.simulated_data_1 = []
        self.simulated_data_2 = []
        self.sig_p_count = []
        self.sig_p_count_interaction = []


    def description(self):
        if self.experiment == 1:
            return 'magnitude set in conditions: ' +\
                   str(self.final_magnitude) + ' and ' +\
                   str(self.experiment_1_magnitude_multiplier *\
                   self.final_magnitude)
        if self.experiment == 2:
            return 'magnitudes multiplied by random number between 0 and 10' +\
                    ' and then rescaled again to ' +\
                    str(self.final_magnitude)
        if self.experiment == 3:
            return 'completely different set of generators, rescaled to the' +\
                   ' same value'
        if self.experiment == 4:
            return 'the same set of generators (between 1 and 5 of them) ' +\
                    'but one new additional added with magnitude between 2 ' +\
                    'and 4'

    
    def condition_1_gen_conf(self):
        [gen_conf_1, magnitude_stddev] = \
            random_generator_configuration(self.limits_number, 
                                           self.limits_depth,
                                           self.limits_orientation,
                                           self.limits_magnitude, 
                                           self.final_magnitude,
                                           magnitude_stddev=2)
        return gen_conf_1


    def condition_2_gen_conf(self, gen_conf_1):
        gen_conf_2 = deepcopy(gen_conf_1)
        if self.experiment == 1:
            for i in range(len(gen_conf_2)):
                gen_conf_2[i]['magnitude'] = \
                        self.experiment_1_magnitude_multiplier *\
                        gen_conf_2[i]['magnitude']
        if self.experiment == 2:
            for i in range(len(gen_conf_2)):
                gen_conf_2[i]['magnitude'] = \
                        uniform(0,10) * gen_conf_2[i]['magnitude']
            gen_conf_2 = scale_generator_configuration(
                                                gen_conf_2,
                                                self.final_magnitude)[0]
        if self.experiment == 3:
            # TODO: Generator magnitude stddev scaling not implemented
            gen_conf_2 = random_generator_configuration(
                                                self.limits_number,
                                                self.limits_depth,
                                                self.limits_orientation, 
                                                self.limits_magnitude, 
                                                self.final_magnitude)[0]
        if self.experiment == 4:
            gen_conf_new = random_generator_configuration(
                                                (1,1), 
                                                self.limits_depth,
                                                self.limits_orientation,
                                                self.limits_magnitude,
                                                uniform(2,4))[0]
            gen_conf_2.append(gen_conf_new[0])
        return gen_conf_2


    def simulate_sources(self, gen_conf_1, gen_conf_2):
        [simulated_gen_1, gen_conf_1, electrodes] = \
                gen_simulation(gen_conf_1, 
                               num_sim=self.number_of_subjects,
                               gen_magnitude_stddev=\
                               self.generator_magnitude_stddev)
        [simulated_gen_2, gen_conf_2, electrodes] = \
                gen_simulation(gen_conf_2, 
                               num_sim=self.number_of_subjects,
                               gen_magnitude_stddev=\
                               self.generator_magnitude_stddev)
        return [simulated_gen_1, gen_conf_1, 
                simulated_gen_2, gen_conf_2,
                electrodes]


    def simulate_noise(self, size):
        if self.normal_noise_amplitude:
            normal_noise_1 = normal(0, self.normal_noise_amplitude, size)
            normal_noise_2 = normal(0, self.normal_noise_amplitude, size)
        else:
            normal_noise_1 = None
            normal_noise_2 = None

        if self.constant_noise_amplitude:
            constant_noise = self.constant_noise_amplitude * ones(size)
        else:
            constant_noise = None

        if self.topographic_noise_amplitude:
            noise_conf_1 = \
                random_generator_configuration(
                                        self.limits_number, 
                                        self.limits_depth,
                                        self.limits_orientation,
                                        self.limits_magnitude,
                                        self.topographic_noise_amplitude)[0]
            noise_conf_2 = \
                random_generator_configuration(
                                        self.limits_number, 
                                        self.limits_depth,
                                        self.limits_orientation,
                                        self.limits_magnitude,
                                        self.topographic_noise_amplitude)[0]
            [topographic_noise_1, noise_conf_1, electrodes] = \
                    gen_simulation(noise_conf_1, 
                                   num_sim=self.number_of_subjects)
            [topographic_noise_2, noise_conf_2, electrodes] = \
                    gen_simulation(noise_conf_2, 
                                   num_sim=self.number_of_subjects)
        else:
            topographic_noise_1 = None
            topographic_noise_2 = None
        
        return [normal_noise_1, topographic_noise_1, 
                normal_noise_2, topographic_noise_2, constant_noise]


    def rereference(self, simulated_data_1, simulated_data_2, electrodes):
        left_mastoid = electrodes.index('      T7')
        right_mastoid = electrodes.index('      T8')
        if self.reference == 'left_mastoid':
            for subject in range(self.number_of_subjects):
                subject_mastoid_1 = simulated_data_1[subject][left_mastoid]
                subject_mastoid_2 = simulated_data_2[subject][left_mastoid]
                simulated_data_1[subject] -= subject_mastoid_1
                simulated_data_2[subject] -= subject_mastoid_2
        elif self.reference == 'average_mastoid':
            for subject in range(self.number_of_subjects):
                subject_mastoids_1 =\
                        0.5*simulated_data_1[subject][left_mastoid] +\
                        0.5*simulated_data_1[subject][right_mastoid]
                subject_mastoids_2 =\
                        0.5*simulated_data_2[subject][left_mastoid] +\
                        0.5*simulated_data_2[subject][right_mastoid]
                for electrode in range(len(electrodes)):
                    simulated_data_1[subject][electrode] -=\
                            subject_mastoids_1
                    simulated_data_2[subject][electrode] -=\
                            subject_mastoids_2
        elif self.reference == 'average':
            for subject in range(self.number_of_subjects):
                subject_mean_1 = mean(simulated_data_1[subject])
                subject_mean_2 = mean(simulated_data_2[subject])
                for electrode in range(len(electrodes)):
                    simulated_data_1[subject][electrode] -= subject_mean_1
                    simulated_data_2[subject][electrode] -= subject_mean_2
        return [simulated_data_1, simulated_data_2]


    def run(self, run_generators=True, run_noise=True, run_reference=True):
        smallest_p = create_scaled_data_structure([])
        sig_p_count = create_scaled_data_structure(0)
        sig_p_count_interaction = create_scaled_data_structure(0)

        for simulation_number in range(self.number_of_simulations):
            if run_generators:
                if simulation_number == 0 or self.configuration == 'random':
                    gen_conf_1 = self.condition_1_gen_conf()
                    gen_conf_2 = self.condition_2_gen_conf(gen_conf_1)
                
                if self.configuration == 'uandk':
                    gen_conf_1 = [{'depth': 7.0,\
                                   'magnitude': -1050.0,\
                                   'orientation': 0.0,\
                                   'orientation_phi':  0.0,\
                                   'phi': -0.65,\
                                   'theta': 0.6}]
                    #print('Ran from here')
                    [gen_conf_1, magnitude_stddev] =\
                            scale_generator_configuration(gen_conf_1, 3.5, 2)
                    #print('STOP')
                    #print('HUUUUUGE FAILLLL!')
                    #print magnitude_stddev
                    gen_conf_2 = self.condition_2_gen_conf(gen_conf_1)
                    
                if simulation_number == 0 or self.configuration == 'random' or \
                   self.generator_magnitude_stddev != 0:
                    [simulated_gen_1, gen_conf_1, simulated_gen_2, gen_conf_2, 
                     electrodes] = self.simulate_sources(gen_conf_1, gen_conf_2)
                    self.electrodes = electrodes
            else:
                simulated_gen_1 = deepcopy(self.simulated_gen_1[simulation_number])
                simulated_gen_2 = deepcopy(self.simulated_gen_2[simulation_number])
                gen_conf_1 = deepcopy(self.gen_conf_1[simulation_number])
                gen_conf_2 = deepcopy(self.gen_conf_2[simulation_number])
            
            simulated_data_1 = deepcopy(simulated_gen_1)
            simulated_data_2 = deepcopy(simulated_gen_2)
            
            if run_noise:
                [normal_noise_1, topographic_noise_1, 
                 normal_noise_2, topographic_noise_2, constant_noise] =\
                        self.simulate_noise(simulated_gen_1.shape)
            else:
                normal_noise_1 = deepcopy(self.normal_noise_1[simulation_number])
                normal_noise_2 = deepcopy(self.normal_noise_2[simulation_number])
                topographic_noise_1 = deepcopy(self.topographic_noise_1[simulation_number])
                topographic_noise_2 = deepcopy(self.topographic_noise_2[simulation_number])
                constant_noise = deepcopy(self.constant_noise[simulation_number])

            if normal_noise_1 != None and normal_noise_2 != None:
                simulated_data_1 += normal_noise_1 
                simulated_data_2 += normal_noise_2
            
            if constant_noise != None:
                simulated_data_1 += constant_noise
                simulated_data_2 += constant_noise

            if topographic_noise_1 != None and topographic_noise_2 != None:
                simulated_data_1 += topographic_noise_1 
                simulated_data_2 += topographic_noise_2  

            if run_reference and self.reference != 'none':
                [simulated_data_1, simulated_data_2] =\
                        self.rereference(simulated_data_1, simulated_data_2, 
                                         self.electrodes)

            electrode_indices = select_electrodes(self.hemispheres, 
                                                  self.sites, 
                                                  self.locations,
                                                  self.electrodes)[4]
            simulated_data_1_scaled = perform_scaling(simulated_data_1,
                                                      electrode_indices)
            simulated_data_2_scaled = perform_scaling(simulated_data_2,
                                                      electrode_indices)
            self.electrode_indices = electrode_indices
            
            anova_results_scaled = \
                create_scaled_data_structure(None)

            [anova_results, electrode_indices] = \
                run_anova(self.hemispheres, self.sites, 
                          self.locations, simulated_data_1,
                          simulated_data_2, self.electrodes,
                          self.doElectrodesAsFactor, printResults=False,
                          name='testu_sim')
            p = self.find_smallest_interaction_p(anova_results)
            smallest_p['Unrescaled'].append(p)
            if p < 0.05:
                found_interaction_on_unrescaled = True
                sig_p_count['Unrescaled'] += 1
            else:
                found_interaction_on_unrescaled = False
            
            for key1 in anova_results_scaled.keys():
                if key1 == 'Unrescaled':
                    break
                for key2 in anova_results_scaled[key1].keys():
                    for key3 in anova_results_scaled[key1][key2].keys():
                        anova_results_scaled[key1][key2][key3] = \
                            run_anova(self.hemispheres, self.sites, 
                                      self.locations,
                                      simulated_data_1_scaled[key1][key2][key3],
                                      simulated_data_2_scaled[key1][key2][key3],
                                      self.electrodes, self.doElectrodesAsFactor,
                                      printResults=False,
                                      name='testu_sim_scaled')[0]
                        p = self.find_smallest_interaction_p\
                                (anova_results_scaled[key1][key2][key3])
                        smallest_p[key1][key2][key3].append(p)
                        if p <0.05:
                            sig_p_count[key1][key2][key3] += 1
                            if found_interaction_on_unrescaled:
                                sig_p_count_interaction[key1][key2][key3] += 1
            
            if self.collect:
                if len(self.gen_conf_1) == self.number_of_simulations:
                    self.gen_conf_1[simulation_number] = gen_conf_1
                    self.gen_conf_2[simulation_number] = gen_conf_2
                    self.simulated_gen_1[simulation_number] = simulated_gen_1
                    self.simulated_gen_2[simulation_number] = simulated_gen_2
                    self.normal_noise_1[simulation_number] = normal_noise_1
                    self.normal_noise_2[simulation_number] = normal_noise_2
                    self.constant_noise[simulation_number] = constant_noise
                    self.topographic_noise_1[simulation_number] = topographic_noise_1
                    self.topographic_noise_2[simulation_number] = topographic_noise_2
                    self.simulated_data_1[simulation_number] = simulated_data_1
                    self.simulated_data_2[simulation_number] = simulated_data_2
                    if self.electrodes == None:
                        self.electrodes = electrodes
                    self.sig_p_count[simulation_number] = sig_p_count
                    self.sig_p_count_interaction[simulation_number] = sig_p_count_interaction
                if not (len(self.gen_conf_1) == self.number_of_simulations):
                    self.gen_conf_1.append(gen_conf_1)
                    self.gen_conf_2.append(gen_conf_2)
                    self.simulated_gen_1.append(simulated_gen_1)
                    self.simulated_gen_2.append(simulated_gen_2)
                    self.normal_noise_1.append(normal_noise_1)
                    self.normal_noise_2.append(normal_noise_2)
                    self.constant_noise.append(constant_noise)
                    self.topographic_noise_1.append(topographic_noise_1)
                    self.topographic_noise_2.append(topographic_noise_2)
                    self.simulated_data_1.append(simulated_data_1)
                    self.simulated_data_2.append(simulated_data_2)
                    if self.electrodes == None:
                        self.electrodes = electrodes
                    self.sig_p_count.append(sig_p_count)
                    self.sig_p_count_interaction.append(sig_p_count_interaction)
        
        self.print_stats(sig_p_count, sig_p_count_interaction)
        
        return [simulated_data_1, simulated_data_2, simulated_data_1_scaled,
                simulated_data_2_scaled, gen_conf_1, gen_conf_2, smallest_p,
                sig_p_count, topographic_noise_1, topographic_noise_2,
                constant_noise]


    def browse(self):
        for simulation_number in range(len(self.simulated_gen_1)):
            simulated_gen_1 = mean(self.simulated_gen_1[simulation_number],0)
            simulated_gen_2 = mean(self.simulated_gen_2[simulation_number],0)
            if self.normal_noise_1[0] == None:
                normal_noise_1 = None
                normal_noise_2 = None
            else:
                normal_noise_1 = mean(self.normal_noise_1[simulation_number],0)
                normal_noise_2 = mean(self.normal_noise_2[simulation_number],0)
            if self.topographic_noise_1[0] == None:
                topographic_noise_1 = None
                topographic_noise_2 = None
            else:
                topographic_noise_1 =\
                        mean(self.topographic_noise_1[simulation_number],0)
                topographic_noise_2 =\
                        mean(self.topographic_noise_2[simulation_number],0)
            simulated_data_1 = mean(self.simulated_data_1[simulation_number],0)
            simulated_data_2 = mean(self.simulated_data_2[simulation_number],0)
            #self.plot_topographies(simulated_gen_1, simulated_gen_2, 
            #                  normal_noise_1, normal_noise_2, 
            #                  topographic_noise_1, topographic_noise_2, 
            #                  simulated_data_1, simulated_data_2)
    

    def plot_topographies(self, simulation, subject='average', fig=None,\
                          folder=None, file='topography'):
        if folder == None:
            filename = 'simulated_topographies/' + file + '_sim_' + str(simulation)
        else:
            filename = folder + '/' + file + '_sim_' + str(simulation)
        if subject=='all':
            for subject in range(self.number_of_subjects):
                plot_simulated_topographies(self.simulated_gen_1[simulation],
                                       self.simulated_gen_2[simulation],
                                       self.normal_noise_1[simulation],
                                       self.normal_noise_2[simulation],
                                       self.topographic_noise_1[simulation],
                                       self.topographic_noise_2[simulation],
                                       self.simulated_data_1[simulation],
                                       self.simulated_data_2[simulation],
                                       subject=subject, fig=fig, 
                                       filename=filename +\
                                       '_subject_' + str(subject))
        subject = 'average'
        plot_simulated_topographies(self.simulated_gen_1[simulation],
                               self.simulated_gen_2[simulation],
                               self.normal_noise_1[simulation],
                               self.normal_noise_2[simulation],
                               self.topographic_noise_1[simulation],
                               self.topographic_noise_2[simulation],
                               self.simulated_data_1[simulation],
                               self.simulated_data_2[simulation],
                               subject=subject, fig=fig, 
                               filename=filename + '_average')


    def plot_topography_line(self, simulation=0, folder=None, file='line'):
        if file:
            if folder == None:
                filename = 'simulated_topographies/' + file + '_sim_' +\
                           str(simulation)
            else:
                filename = folder + '/' + file + '_sim_' + str(simulation)
        
        pyplot.figure()
        data_1 = []
        data_2 = []
        for i in self.electrode_indices:
            data_1.append(mean(self.simulated_data_1[simulation][:,i]))
            data_2.append(mean(self.simulated_data_2[simulation][:,i]))
        pyplot.plot(data_1)
        pyplot.plot(data_2)
        pyplot.xlabel('Electrodes used in analysis')
        pyplot.ylabel('Scalp potential')
        
        if file != None:
            pyplot.savefig(filename + '_topographic_line.png', format='png')
            

    def find_smallest_interaction_p(self, stats):
        smallest_p = 1
        for entry in stats:
            if stats[entry]['p'] < smallest_p and 'condition' in entry\
                    and ':' in entry:
                smallest_p=stats[entry]['p']
        return smallest_p


    def print_stats(self, sig_p_count, sig_p_count_interaction):
        print('\n###\n### Experiment ' + str(self.experiment) + '\n###\n#')
        print(self.description())
        print(' * Number of subjects: ' + str(self.number_of_subjects))
        print(' * Number of simulations: ' + str(self.number_of_simulations))
        print(' * Noise: normal (' + str(self.normal_noise_amplitude) +\
              '), constant (' + str(self.constant_noise_amplitude) +\
              ') and topgraphic (' +\
              str(self.topographic_noise_amplitude) + ')')
        print(' * Generator magnitude standard deviation: ' +
              str(self.generator_magnitude_stddev))
        print('\n   *** Results of all analyses ***')
        
        for i in range(4):
            if i == 0:
                print('\nProportion of interactions')
                numerator = sig_p_count
                denominator = self.number_of_simulations
            if i == 1:
                print('\nProportion of interactions after rescaling to ' +\
                      'interactions for unrescaled data')
                numerator = sig_p_count
                denominator = sig_p_count['Unrescaled']
            if i == 2:
                print('\nProportion of interactions in cases where ' +\
                      'interaction was present in unrescaled data')
                numerator = sig_p_count_interaction
                denominator = sig_p_count['Unrescaled']
            if i == 3:
                print('\nProportion of interactions in cases where ' +\
                      'interaction was not present in unrescaled data')
                numerator = sig_p_count_interaction
                for key1 in sig_p_count.keys():
                    if key1 == 'Unrescaled':
                        continue
                    for key2 in sig_p_count[key1].keys():
                        for key3 in sig_p_count[key1][key2].keys():
                            numerator[key1][key2][key3] = \
                                    sig_p_count[key1][key2][key3] -\
                                    sig_p_count_interaction[key1][key2][key3]
                denominator = self.number_of_simulations -\
                              sig_p_count_interaction['Unrescaled']
        
            if denominator == 0:
                print('No interactions - denominator is zero')
                continue

            keys1 = sig_p_count.keys()
            keys1.reverse()
            for key1 in keys1:
                if key1 == 'Unrescaled' and (i == 0 or i == 1):
                    print('Unrescaled ' + ': ' + str(numerator['Unrescaled'])\
                          + '/' + str(denominator) + ' = ' +\
                          str(numerator['Unrescaled']/denominator))
                    continue
                if key1 == 'Unrescaled' and (i == 2 or i == 3):
                    continue
                keys2 = sig_p_count[key1].keys()
                keys2.reverse()
                for key2 in keys2:
                    keys3 = sig_p_count[key1][key2].keys()
                    keys3.reverse()
                    for key3 in keys3:
                        print(key1 + key2 + key3 + ': ' +\
                              str(numerator[key1][key2][key3]) + '/' +\
                              str(denominator) + ' = ' +\
                              str(numerator[key1][key2][key3] / denominator))


