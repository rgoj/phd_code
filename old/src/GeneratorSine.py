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
The GeneratorSine class is a reimplementation of the Generator class. It
provides a sine generator and allows the phase of the sine to be zeroed by a
stimulus.  
"""

from math import pi
from math import sin

from Generator import Generator

class GeneratorSine(Generator):
    def __init__(self, name, head, position = [0,0,0], frequency = 2, phaseShift = 0):
        Generator.__init__(self, name, head, position)
        self.frequency = frequency
        self.phaseShift = phaseShift
        self.currentPhase = self.phaseShift
        self.lastTimePoint = 0
    
    def printInfo(self):
        print(self.name + ": A GeneratorSine object")

    def receiveInput(self, input):
        if input == 'Stimulus':
            self.currentPhase = self.phaseShift

    def runGenerator(self, time):
        timeStep = time - self.lastTimePoint
        self.lastTimePoint = time
        self.currentPhase += self.frequency * timeStep
        self.activation = sin(self.currentPhase * 2 * pi)
        
        return self.activation
