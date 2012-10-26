# PyBrainSim Copyright 2009 Roman Goj
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
The Stimulus class is a child class of the Generatorc lass. It reimplements the
runGenerator method, so that a stimulus can be periodically sent to all
connected generators.
"""

from Generator import Generator

class Stimulus(Generator):
    def __init__(self, name, head):
        Generator.__init__(self, name, head)
        self.stimulusTimes = []
        self.currentStimulus = 0

    def printInfo(self):
        print(self.name + ": A Stimulus object")
    
    def setStimulusTimes(self, stimulusTimes):
        self.stimulusTimes = stimulusTimes

    def runGenerator(self, time):
        if self.currentStimulus < len(self.stimulusTimes):
            if self.stimulusTimes[self.currentStimulus] <= time:
                self.currentStimulus += 1
                self.activation = 'Stimulus'
            else:
                self.activation = 0
        else:
            self.activation = 0

        return self.activation 
