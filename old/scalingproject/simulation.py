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
from numpy.random import randint, uniform

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
