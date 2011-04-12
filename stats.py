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
    def __init__(self, parser, tracer=None, title=None):
        common.Base.__init__(self, parser)

        self.tracer = tracer
        self.title = title

        if title:
            if not tracer.title:
                tracer.title = title

            if not tracer.ylabel:
                tracer.ylabel = title

class Fitness(Stat):
    def __init__(self, parser, tracer, idx, pattern, title="Fitness"):
        Stat.__init__(self, parser, tracer, title)

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

                if len(data) <= self.idx: continue
                if self.pattern not in data[self.idx]: continue

                fitness = int(data[self.idx].split()[-1])
                fitnesses.append(fitness)

        if len(fitnesses) > 0:
            self.tracer.add(fitnesses)
            tree['TITLE'] = self.title.replace(' ', '_')
            open('%(GRAPHDIR)s/%(TITLE)s_%(NAME)s_%(MANGLENAME)s.data' % tree, 'w').write(str(fitnesses))

class MakeSpan(Fitness):
    def __init__(self, parser, tracer):
        Fitness.__init__(self, parser, tracer, 2, 'Makespan', title='Makespan')

class TotalCost(Fitness):
    def __init__(self, parser, tracer):
        Fitness.__init__(self, parser, tracer, 3, 'TotalCost', title='Total cost')

class FitnessLast(Stat):
    def __init__(self, parser, tracer, idx, pattern, title="Fitness"):
        Stat.__init__(self, parser, tracer, title)

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
                if '.last' in f:
                    data = open(f).readlines()

                    if len(data) <= self.idx: continue
                    if self.pattern not in data[self.idx]: continue

                    fitness = int(data[self.idx].split()[-1])
                    fitnesses.append(fitness)

        if len(fitnesses) > 0:
            self.tracer.add(fitnesses)
            tree['TITLE'] = self.title.replace(' ', '_')
            open('%(GRAPHDIR)s/%(TITLE)s_%(NAME)s_%(MANGLENAME)s.data' % tree, 'w').write(str(fitnesses))

class MakeSpanLast(FitnessLast):
    def __init__(self, parser, tracer):
        FitnessLast.__init__(self, parser, tracer, 2, 'Makespan', title='Makespan Last ones')

class TotalCostLast(FitnessLast):
    def __init__(self, parser, tracer):
        FitnessLast.__init__(self, parser, tracer, 3, 'TotalCost', title='Total cost Last ones')

class SpeedUp(Stat):
    def __init__(self, parser, tracer, idx, pattern):
        Stat.__init__(self, parser, tracer, title="Speed up")

        self.idx = idx
        self.pattern = pattern

    def callit(self, options, tree):
        tree['MANGLENAME'] = options.manglename_pattern % tree

        diffs = []

        for num in range(1, options.nruns+1):
            tree['NUM'] = num
            tree['TIME_FILENAME'] = options.timefilename_pattern % tree

            data = open(tree['TIME_FILENAME']).readlines()

            if len(data) <= self.idx: continue
            if self.pattern not in data[self.idx]: continue

            diff = float(data[self.idx].split()[-1][:-1]) / 100
            diffs.append(diff)

        if len(diffs) > 0:
            self.tracer.add(diffs)
            tree['TITLE'] = self.title.replace(' ', '_')
            open('%(GRAPHDIR)s/%(TITLE)s_%(NAME)s_%(MANGLENAME)s.data' % tree, 'w').write(str(diffs))

class Efficiency(Stat):
    def __init__(self, parser, tracer, idx, pattern):
        Stat.__init__(self, parser, tracer, title="Efficiency")

        self.idx = idx
        self.pattern = pattern

    def callit(self, options, tree):
        tree['MANGLENAME'] = options.manglename_pattern % tree

        diffs = []

        for num in range(1, options.nruns+1):
            tree['NUM'] = num
            tree['TIME_FILENAME'] = options.timefilename_pattern % tree

            data = open(tree['TIME_FILENAME']).readlines()

            if len(data) <= self.idx: continue
            if self.pattern not in data[self.idx]: continue

            diff = float(data[self.idx].split()[-1][:-1]) / tree["CORESIZE"] * 1/100
            diffs.append(diff)

        if len(diffs) > 0:
            self.tracer.add(diffs)
            tree['TITLE'] = self.title.replace(' ', '_')
            open('%(GRAPHDIR)s/%(TITLE)s_%(NAME)s_%(MANGLENAME)s.data' % tree, 'w').write(str(diffs))

class TimeSpeedUp(SpeedUp):
    def __init__(self, parser, tracer, idx=3):
        SpeedUp.__init__(self, parser, tracer, idx, 'Percent of CPU this job got')

class TimeEfficiency(Efficiency):
    def __init__(self, parser, tracer, idx=3):
        Efficiency.__init__(self, parser, tracer, idx, 'Percent of CPU this job got')
