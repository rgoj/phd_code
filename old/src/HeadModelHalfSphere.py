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
This reimplemenation of the HeadModel class provides a half sphere model of a
head. The checkPosition() and runHeadModel() methods have been modified, so
that only positions within one half of a sphere of radius 1 are allowed and
recorded activity is smaller when generator is further from registration site.
"""

from HeadModel import HeadModel

class HeadModelHalfSphere(HeadModel):
    def __init__(self, head):
        HeadModel.__init__(self, head)
        self.head = head
    
    def checkPosition(self,position):
        # Checking if position is a list of three numbers
        if not isinstance(position, list):
            return False
        if len(position) != 3:
            return False
        for i in range(3):
            if (not isinstance(position[i], float)) and (not isinstance(position[i], int)):
                return False
        # Checking if position is smaller than the sphere radius of 1
        positionLength = position[0] ** 2 + position[1] ** 2 + position[2] ** 2
        if positionLength > 1:
            return False
        # If none of the conditions above fail, the position is correct
        return True

    def runHeadModel(self, generatorOutput, recording):
        # Filling all registration sites with the generators' output
        for channel in range(len(recording)):
            recording[channel].append(0)
            for generator in range(len(generatorOutput)):
                # Rejecting generator output that isn't a number
                if isinstance(generatorOutput[generator], str):
                    recording[channel][-1] += 0
                else:
                    distance = 0
                    # Distance between generator and registration site
                    for dimension in range(3):
                        distance += ((self.head.generatorSiteList[generator][dimension]
                                     -
                                     self.head.registrationSiteList[channel][dimension])
                                     ** 2)
                    # The recorded activity is smaller when the generator is
                    # far from the registration site.
                    recording[channel][-1] += generatorOutput[generator] / distance

        return recording
