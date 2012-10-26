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
The Generator class serves as a starting point for creating complex classes
simulating populations of neurons.  
"""

class Generator:
    def __init__(self, name, head, position = [0, 0, 0]):
        self.name = name
        self.activation = 0
        head.addGenerator(self, position)
    
    def printInfo(self):
        print(self.name + ": A Generator object")
    
    def getName(self):
        return self.name
    
    def receiveInput(self, input):
        self.activation += input

    def runGenerator(self, time):
        return self.activation

