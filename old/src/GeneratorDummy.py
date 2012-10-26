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
The GeneratorDummy class is a reimplementation of the parent class
GeneratorDummy, printing out a message whenever any interesting methods are
invoked.
"""

from Generator import Generator

class GeneratorDummy(Generator):
    def printInfo(self):
        print(self.name + ": A GeneratorDummy object")
    
    def receiveInput(self, input):
        print("[receiveInput] " + self.name + ": Received input from connection")

    def runGenerator(self, time):
        print("[runGenerator] " + self.name + ": Calculating activation")
        return 0
