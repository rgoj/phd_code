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
The Connection class is used for describing communication between two
generators - i.e. inhibitory or excitatory connections between simulated neural
populations.

This class is only the simplest implementation of these ideas, intended to
serve as an example and a starting point for creating complex derived classes,
ready for real simulation tasks.  
"""

class Connection:
    def __init__(self, name, head, sourceGenerator, targetGenerator, gain = 1):
        self.name = name
        self.sourceGenerator = sourceGenerator
        self.targetGenerator = targetGenerator
        self.gain = gain
        head.addConnection(self)
    
    def printInfo(self):
        print(self.name + " A Connection object")
    
    def getName(self):
        return self.name
    
    def getSource(self):
        return self.sourceGenerator
    
    def getTarget(self):
        return self.targetGenerator
    
    def runConnection(self, sourceGeneratorOutput):
        self.targetGenerator.receiveInput(self.gain * sourceGeneratorOutput)
