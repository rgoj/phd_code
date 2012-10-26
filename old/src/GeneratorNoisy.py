# PyBrainSim
# Copyright 2009 Roman Goj
#
# This file is part of PyBrainSim.
#
# PyBrainSim is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# PyBrainSim is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# PyBrainSim.  If not, see <http://www.gnu.org/licenses/>.

__metaclass__ = type # New style classes. Is this necessary?

"""
The GeneratorNoisy class is a reimplementation of the Generator class. It
provides a simple generator which, whenever required, generates a number 
generated from a Gaussian distribution with specified mean and variance.  
"""

from numpy.random import normal

from Generator import Generator

class GeneratorNoisy(Generator):
    def __init__(self, name, head, position = [0,0,0], mean = 0, stddev = 0):
        Generator.__init__(self, name, head, position)
        self.mean = mean
        self.stddev = stddev
    
    def printInfo(self):
        print(self.name + ": A GeneratorNoisy object")

    def runGenerator(self, time):
        if self.stddev == 0:
            self.activation = self.mean
        else:
            self.activation = normal(self.mean, self.stddev)
        
        return self.activation
