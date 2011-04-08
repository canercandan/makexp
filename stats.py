#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# Authors:
# Caner Candan <caner@candan.fr>, http://caner.candan.fr
#

from os import listdir
import common

class Stat(common.Base):
    def __init__(self, parser, tracer=None):
        common.Base.__init__(self, parser)

        self.tracer = tracer

class Fitness(Stat):
    def __init__(self, parser, tracer, idx, pattern):
        Stat.__init__(self, parser, tracer)

        self.idx = idx
        self.pattern = pattern

    def callit(self, options, tree):
        tree['MANGLENAME'] = options.manglename_pattern % tree
        tree['PLAN_FILENAME'] = options.planfilename_pattern % tree

        fitnesses = []

        dirs = listdir(tree['RESDIR'])
        dirs.sort()
        for f in dirs:
            f = '%s/%s' % (tree['RESDIR'], f)

            if tree['PLAN_FILENAME'] in f:
                data = open(f).readlines()

                if len(data) <= self.idx:
                    continue

                if self.pattern not in data[self.idx]:
                    continue

                fitness = int(data[self.idx].split()[-1])
                fitnesses.append(fitness)

        if len(fitnesses) > 0:
            self.tracer.add(fitnesses)

class MakeSpan(Fitness):
    def __init__(self, parser, tracer):
        Fitness.__init__(self, parser, tracer, 2, 'Makespan')

class TotalCost(Fitness):
    def __init__(self, parser, tracer):
        Fitness.__init__(self, parser, tracer, 3, 'TotalCost')

class SpeedUp(Stat):
    def __init__(self, parser, tracer, idx, pattern):
        Stat.__init__(self, parser, tracer)

        self.idx = idx
        self.pattern = pattern

    def callit(self, options, tree):
        tree['MANGLENAME'] = options.manglename_pattern % tree

        diffs = []

        for num in range(1, options.nruns+1):
            tree['NUM'] = num
            tree['TIME_FILENAME'] = options.timefilename_pattern % tree

            data = open(tree['TIME_FILENAME']).readlines()

            if len(data) <= self.idx:
                continue

            if self.pattern not in data[self.idx]:
                continue

            diff = float(data[self.idx].split()[-1][:-1]) / tree["CORESIZE"] * 1/100
            diffs.append(diff)

        if len(diffs) > 0:
            self.tracer.add(diffs)

class TimeSpeedUp(SpeedUp):
    def __init__(self, parser, tracer):
        SpeedUp.__init__(self, parser, tracer, 3, 'Percent of CPU this job got')
