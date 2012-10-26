# Roman Goj
# 18/11/2010
"""
A script for managing the scaling experiments.

"""
from __future__ import division

import sys
from copy import deepcopy
from sumatra.parameters import build_parameters
from ScalingExperiment import ScalingExperiment

######################
# Reading parameters #
######################

parameters = build_parameters(sys.argv[1])
default_parameters = deepcopy(parameters)
param_dict = parameters.as_dict()

##############################
# Running scaling experiment #
##############################

experiment = 1
se = ScalingExperiment(experiment, parameters=param_dict,
                       topographic_noise_amplitude=0,
                       generator_magnitude_stddev=0)
se.run()

