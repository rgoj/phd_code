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
This is a reimplementation of the Stimulus class (child of the Generator class)
that prints messages from inside of the interesting methods.
"""

from Stimulus import Stimulus

class StimulusDummy(Stimulus):
    def printInfo(self):
        print(self.name + ": A StimulusDummy object")
    
    def runGenerator(self, time):
        print("[runGenerator] " + self.name + ": Preparing the stimulus")
        return Stimulus.runGenerator(self, time)
