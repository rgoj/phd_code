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
The GeneratorNumberIncrementing class is a reimplementation of the Generator
class. It provides an elementary example of how the methods could be used to do
integer addition.
"""

from Generator import Generator

class GeneratorNumberIncrementing(Generator):
    def printInfo(self):
        print(self.name + ": A GeneratorNumberIncrementing object")

    def receiveInput(self, input):
        if input == 'Stimulus':
            self.activation = 0
        else:
            self.activation += input

    def runGenerator(self, time):
        self.activation = self.activation + 1
        return self.activation
