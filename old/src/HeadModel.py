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

from __future__ import division
from numpy import arange
__metaclass__ = type # New style classes. Is this necessary?

"""
The HeadModel class takes care of what happens to the generators' activity on
it's way to the registration sites - i.e. with impedance of the skull.
"""

class HeadModel:
    def __init__(self, head):
        head.setHeadModel(self)
    
    def checkPosition(self,position):
        return position == [0,0,0]

    def runHeadModel(self, generatorOutput, recording):
        # Filling all registration sites with the generators' output
        for i in range(len(recording)):
            recording[i].append(0)
            for j in range(len(generatorOutput)):
                # Rejecting generator output that isn't a number
                if isinstance(generatorOutput[j], str):
                    recording[i][-1] += 0
                else:
                    recording[i][-1] += generatorOutput[j]

        return recording
