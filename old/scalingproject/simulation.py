# Roman Goj
# 22/11/2010
"""
This module contains functions for generating random generator conigurations as
well as running the simulations of these generator configurations
"""
# TODO: Write a script that would simulate multiple epochs and multple
# subjects.

from __future__ import division

import sys
from numpy import pi, array, max, min, mean, power, sqrt
from numpy.random import randint
from numpy.random import uniform

sys.path.insert(0, '../src')
from Head import Head
from HeadModel import HeadModel
from HeadModelDipoleSphere import HeadModelDipoleSphere
from GeneratorNoisy import GeneratorNoisy

from topographicmap import read_electrode_locations

def gen_simulation(gen_conf, num_sim=1, gen_magnitude_stddev=0):
    """Runs a single simulation of generators of ERP components.
    
    Currently only one epoch for one subject is calculated, maybe this should
    change. The generator configuration is specified as input.
    
    """
    # TODO: Remove all the scaling variables!
    # Initialisation of the PyBrainSim modelling framework with a homogeneous
    # spherical head model with a head radius set to 11.5 cm. Since we are
    # modelling only the spatical characteristics of the ERP component, we set
    # the temporal sampling frequency to 1, to obtain only one simulated value
    # per epoch.
    head = Head()
    head.setSamplingFrequency(1)
    headModel = HeadModelDipoleSphere(head, 11.5)
    
    # Initialisation of the simulated electrode array from predefined electrode
    # locations simulating the 10-20 electrode placement system.
    # TODO: This isn't elegant and should be changed!
    # TODO: This excludes simulations with a line of electrodes, which are
    # important for some applications as well, see doOneSimulation.py for
    # example implementation.
    [electrodes, topoX, topoY, thetaAngles, phiAngles] =\
        read_electrode_locations()
    for i in range(len(electrodes)):
        head.addRegistrationSite([thetaAngles[i], phiAngles[i]])
    
    # TODO: Here we are assuming that we know the generator locations!
    # (from the gen_conf variable)

    # Adding dipole generators to the head with the configuration parameters
    # given in gen_conf.
    # TODO: This is not working code
    # TODO: It would be really good if this code could fit in less lines!
    # TODO: Actually adding the generators to a list is not necessary any more,
    # maybe I could just run the constructor?
    generators = []
    for i in range(len(gen_conf)):
        # Combining the generator with the head model
        generators.append(
            GeneratorNoisy('Gen', head, 
                           position=[gen_conf[i]['depth'], 
                                     gen_conf[i]['theta'], 
                                     gen_conf[i]['phi'], 
                                     gen_conf[i]['orientation'], 
                                     gen_conf[i]['orientation_phi']], 
                           mean=gen_conf[i]['magnitude'], 
                           stddev=gen_magnitude_stddev))
    
    # Running the simulation.
    # TODO: runSimulation() should already return a numpy.array, now it returns
    # a list (checked that)!
    simulated_data = array(head.runSimulation(num_sim))

    # TODO: I should be returning something different here, perhaps?
    # TODO: I need to transpose simulated data to enable it to be used with
    # e.g. the topographic maps without transposing, like with the real data...
    # but whether this is a good idea in the long run - no idea...
    return [simulated_data.transpose(), gen_conf, electrodes]


def scale_generator_configuration(gen_conf, magnitude_final, 
                                  magnitude_stddev=0):
    [simulated_data, gen_conf, electrodes] = gen_simulation(gen_conf)
    #range_data = (max(mean(simulated_data,0)) - min(mean(simulated_data,0)))
    range_data = (max(simulated_data) - min(simulated_data))
    #print(str(max(mean(simulated_data,0))) + ' ' +
    #      str(min(mean(simulated_data,0))))
    #print(str(max(simulated_data)) + ' ' + str(min(simulated_data)))
    for i in range(len(gen_conf)):
        gen_conf[i]['magnitude'] = (gen_conf[i]['magnitude'] * 
            magnitude_final / range_data)
        if magnitude_stddev>0:
            magnitude_stddev = (magnitude_stddev * magnitude_final / range_data)
    
    # TODO:
    # THIS ISN't workin g AS IT SHOULD. Apparently, for UandK a t least it
    # generates results twice as big as found in practice, heh.
    #if magnitude_stddev != 0:
    #    simulated_gen = []
    #    for i in range(len(gen_conf)):
    #        simulated_gen.append(gen_simulation([gen_conf[i]])[0])
    #    magnitude_stddev = 2 # TODO: This shouldn' be hard-coded. It should
                             # reflect parameter incoded in parameter files, 
                             # the electrode-level noise level
    #    magnitude_stddev = magnitude_stddev * len(electrodes)
    #    denominator = 0
    #    for i in range(len(electrodes)):
    #        under_sqrt = 0
    #        under_sqrt = sqrt(power(simulated_gen[0][0][i],2))
            #for j in range(len(gen_conf)):
                #under_sqrt += 1 / power(gen_conf[j]['magnitude']*\
                #                        simulated_gen[j][0][i],2)
            #    under_sqrt += 1 / power(gen_conf[j]['magnitude']*\
            #                            simulated_gen[j][0][i],2)
            #print len(simulated_gen[j][0])
    #        denominator += under_sqrt
    #    magnitude_stddev = magnitude_stddev * 1050 / denominator
        #magnitude_stddev = magnitude_stddev / denominator

    return [gen_conf, magnitude_stddev]


def random_generator_configuration(num_gen_lim=(1,5), depth_lim=(4,5),
                                   orientation_lim=(0,0), magnitude_lim=(1,10),
                                   magnitude_final=False, magnitude_stddev=0, 
                                   electrode_setup='1020'):
    """Randomizing parameters of generators within the limits given to obtain a
    random generator coniguration.
    
    """
    gen_conf = []
    num_gen = randint(num_gen_lim[0], num_gen_lim[1] + 1)

    for i in range(num_gen):
        gen_conf.append({})

        # Dipole location
        gen_conf[i]['depth'] = uniform(depth_lim[0], depth_lim[1])
        gen_conf[i]['theta'] = uniform(0,pi/2)
        gen_conf[i]['phi'] = uniform(0,2*pi)
        
        # Dipole orientation
        gen_conf[i]['orientation'] = uniform(orientation_lim[0],
                                             orientation_lim[1])
        gen_conf[i]['orientation_phi'] = uniform(0, 2*pi)

        # Dipole magnitude
        gen_conf[i]['magnitude'] = uniform(magnitude_lim[0], magnitude_lim[1])
     
    # Scaling the simulated data and the amplitudes of the simulated
    # generators. This insures that the data from different generator
    # configurations can have the same amplitudes.
    if magnitude_final:
        [gen_conf, magnitude_stddev] = scale_generator_configuration(gen_conf, 
                                            magnitude_final, magnitude_stddev)

    return [gen_conf, magnitude_stddev]
