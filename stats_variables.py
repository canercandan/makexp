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

class AgregatedFitness(Stat):
    def __init__(self, parser, tracer, idx_name, pattern, title="Agregated Fitness"):
        Stat.__init__(self, parser, tracer)

        self.idx_name = idx_name
        self.pattern = pattern
        self.title = title

    def callit(self, options, tree):
        if not tree['PLOT']: return

        tree['MANGLENAME'] = '%(MANGLENAME_PATTERN)s' % tree % tree
        tree['NUM'] = ''
        tree['PLAN_FILENAME'] = '%(PLANFILENAME_PATTERN)s' % tree % tree

        idx = tree[self.idx_name]
        fitnesses = []

        dirs = listdir(tree['RESDIR'])
        dirs.sort()
        for f in dirs:
            f = '%s/%s' % (tree['RESDIR'], f)

            if tree['PLAN_FILENAME'] in f:
                data = open(f).readlines()

                if len(data) <= idx: continue
                if self.pattern not in data[idx]: continue

                fitness = int(data[idx].split()[-1])
                fitnesses.append(fitness)

        if len(fitnesses) > 0:
            self.tracer.add(fitnesses)
            tree['TITLE'] = self.title.replace(' ', '_')
            open('%(GRAPHDIR)s/%(TITLE)s_%(NAME)s_%(MANGLENAME)s.data' % tree, 'w').write(str(fitnesses))

class AgregatedMakeSpan(AgregatedFitness):
    def __init__(self, parser, tracer):
        AgregatedFitness.__init__(self, parser, tracer, 'MAKESPAN_IDX', 'Makespan', title='Agregated Makespan')

class AgregatedTotalCost(AgregatedFitness):
    def __init__(self, parser, tracer):
        AgregatedFitness.__init__(self, parser, tracer, 'TOTALCOST_IDX', 'TotalCost', title='Agregated Total cost')

class Fitness(Stat):
    def __init__(self, parser, tracer, idx_name, pattern, title="Fitness"):
        Stat.__init__(self, parser, tracer)

        self.idx_name = idx_name
        self.pattern = pattern
        self.title = title

    def callit(self, options, tree):
        if not tree['PLOT']: return

        tree['MANGLENAME'] = '%(MANGLENAME_PATTERN)s' % tree % tree
        tree['NUM'] = ''
        tree['PLAN_FILENAME'] = '%(PLANFILENAME_PATTERN)s' % tree % tree

        fitnesses = []
        idx = tree[self.idx_name]

        dirs = listdir(tree['RESDIR'])
        dirs.sort()
        for tree['FILENAME'] in dirs:
            f = '%(RESDIR)s/%(FILENAME)s' % tree

            if tree['PLAN_FILENAME'] in f and '.last' in f:
                data = open(f).readlines()

                if len(data) <= idx: continue
                if self.pattern not in data[idx]: continue

                fitness = int(data[idx].split()[-1])
                fitnesses.append(fitness)

        if len(fitnesses) > 0:
            self.tracer.add(fitnesses)
            tree['TITLE'] = self.title.replace(' ', '_')
            open('%(GRAPHDIR)s/%(TITLE)s_%(NAME)s_%(MANGLENAME)s.data' % tree, 'w').write(str(fitnesses))

class MakeSpan(Fitness):
    def __init__(self, parser, tracer):
        Fitness.__init__(self, parser, tracer, idx_name='MAKESPAN_IDX', pattern='Makespan', title='Makespan')

class TotalCost(Fitness):
    def __init__(self, parser, tracer):
        Fitness.__init__(self, parser, tracer, idx_name='TOTALCOST_IDX', pattern='TotalCost', title='Total cost')

class SpeedUp(Stat):
    def __init__(self, parser, tracer, idx_name, pattern):
        Stat.__init__(self, parser, tracer)

        self.idx_name = idx_name
        self.pattern = pattern
        self.title = 'Speedup'

    def callit(self, options, tree):
        if not tree['PLOT']: return

        tree['MANGLENAME'] = '%(MANGLENAME_PATTERN)s' % tree % tree

        diffs = []

        for tree['NUM'] in xrange(1, tree['NRUNS']+1):
            tree['TIME_FILENAME'] = '%(TIMEFILENAME_PATTERN)s' % tree % tree

            idx = tree[self.idx_name]

            data = open(tree['TIME_FILENAME']).readlines()

            if len(data) <= idx: continue

            if 'Command exited' in data[0]:
                idx += 1
                if len(data) <= idx: continue

            if self.pattern not in data[idx]: continue

            diff = float(data[idx].split()[-1][:-1]) / 100
            diffs.append(diff)

        if len(diffs) > 0:
            self.tracer.add(diffs)
            tree['TITLE'] = self.title.replace(' ', '_')
            open('%(GRAPHDIR)s/%(TITLE)s_%(NAME)s_%(MANGLENAME)s.data' % tree, 'w').write(str(diffs))

class Efficiency(Stat):
    def __init__(self, parser, tracer, idx_name, pattern):
        Stat.__init__(self, parser, tracer)

        self.idx_name = idx_name
        self.pattern = pattern
        self.title = 'Efficiency'

    def callit(self, options, tree):
        if not tree['PLOT']: return

        tree['MANGLENAME'] = '%(MANGLENAME_PATTERN)s' % tree % tree

        diffs = []

        for tree['NUM'] in xrange(1, tree['NRUNS']+1):
            tree['TIME_FILENAME'] = '%(TIMEFILENAME_PATTERN)s' % tree % tree

            idx = tree[self.idx_name]

            data = open(tree['TIME_FILENAME']).readlines()

            if len(data) <= idx: continue

            if 'Command exited' in data[0]:
                idx += 1
                if len(data) <= idx: continue

            if self.pattern not in data[idx]: continue

            diff = float(data[idx].split()[-1][:-1]) / tree["CORESIZE"] * 1/100
            diffs.append(diff)

        if len(diffs) > 0:
            self.tracer.add(diffs)
            tree['TITLE'] = self.title.replace(' ', '_')
            open('%(GRAPHDIR)s/%(TITLE)s_%(NAME)s_%(MANGLENAME)s.data' % tree, 'w').write(str(diffs))

class TimeSpeedUp(SpeedUp):
    def __init__(self, parser, tracer):
        SpeedUp.__init__(self, parser, tracer, idx_name='SPEEDUP_IDX', pattern='Percent of CPU this job got')

class TimeEfficiency(Efficiency):
    def __init__(self, parser, tracer):
        Efficiency.__init__(self, parser, tracer, idx_name='EFFICIENCY_IDX', pattern='Percent of CPU this job got')

class ElapsedTime(Stat):
    def __init__(self, parser, tracer, idx_name, pattern, title="Elapsed time", rate=False):
        Stat.__init__(self, parser, tracer)

        self.idx_name = idx_name
        self.pattern = pattern
        self.title = title
        self.rate = rate

    def callit(self, options, tree):
        if not tree['PLOT']: return

        tree['MANGLENAME'] = '%(MANGLENAME_PATTERN)s' % tree % tree

        idx = tree[self.idx_name]
        times = []

        for tree['NUM'] in xrange(1, tree['NRUNS']+1):
            tree['RES_FILENAME'] = '%(RESFILENAME_PATTERN)s' % tree % tree

            data = open(tree['RES_FILENAME']).readlines()

            if len(data) <= idx: continue
            if self.pattern not in data[idx]: continue

            global_time = None

            if self.rate:
                idx_global_time = tree['GLOBAL_TIME_IDX']
                if len(data) <= idx_global_time: continue
                if "Elapsed time" not in data[idx_global_time]:

                    tree['TIME_FILENAME'] = '%(TIMEFILENAME_PATTERN)s' % tree % tree

                    idx_time = tree['TIME_IDX']
                    data_time = open(tree['TIME_FILENAME']).readlines()

                    if len(data_time) <= idx_time: continue

                    if 'Command exited' in data_time[0]:
                        idx_time += 1
                        if len(data_time) <= idx_time: continue

                    if 'Elapsed (wall clock) time' not in data_time[idx_time]: continue

                    global_time = data_time[idx_time].split()[-1][:-1].split(':')
                    global_time = float(int(global_time[0]) * 60 + float(global_time[1]))

                else:

                    global_time = float(data[idx_global_time].split()[-1][:-1])

            time = float(data[idx].split()[-1][:-1])

            if self.rate:
                times.append(time/global_time)
            else:
                times.append(time)

        if len(times) > 0:
            self.tracer.add(times)
            tree['TITLE'] = self.title.replace(' ', '_')
            open('%(GRAPHDIR)s/%(TITLE)s_%(NAME)s_%(MANGLENAME)s.time' % tree, 'w').write(str(times))

class EvaluationTime(ElapsedTime):
    def __init__(self, parser, tracer):
        ElapsedTime.__init__(self, parser, tracer, 'EVALUATION_TIME_IDX', 'Evaluation elapsed time', title='Evaluation elapsed rate time')

class VariationTime(ElapsedTime):
    def __init__(self, parser, tracer):
        ElapsedTime.__init__(self, parser, tracer, 'VARIATION_TIME_IDX', 'Variation elapsed time', title='Variation elapsed rate time')

class ReplaceTime(ElapsedTime):
    def __init__(self, parser, tracer):
        ElapsedTime.__init__(self, parser, tracer, 'REPLACE_TIME_IDX', 'Replace elapsed time', title='Replace elapsed rate time')

class ElapsedTimeCommand(Stat):
    def __init__(self, parser, tracer, idx_name, pattern, title="Elapsed time", rate=False):
        Stat.__init__(self, parser, tracer)

        self.idx_name = idx_name
        self.pattern = pattern
        self.title = title
        self.rate = rate

    def callit(self, options, tree):
        """
        Construct the list 'times' in browsing N runs, then for each run, it reads there result and time files:
        - the result file provides the absolute elapsed time measured at runtime
        - the time file provides the elapsed time (wall clock) got through the command time
        """

        if not tree['PLOT']: return

        tree['MANGLENAME'] = '%(MANGLENAME_PATTERN)s' % tree % tree

        times = []

        for tree['NUM'] in xrange(1, tree['NRUNS']+1):
            tree['RES_FILENAME'] = '%(RESFILENAME_PATTERN)s' % tree % tree
            tree['TIME_FILENAME'] = '%(TIMEFILENAME_PATTERN)s' % tree % tree

            idx = tree[self.idx_name]

            global_time = None

            if self.rate:
                idx_time = tree['TIME_IDX']
                data_time = open(tree['TIME_FILENAME']).readlines()

                if len(data_time) <= idx_time: continue

                if 'Command exited' in data_time[0]:
                    idx_time += 1
                    if len(data_time) <= idx_time: continue

                if 'Elapsed (wall clock) time' not in data_time[idx_time]: continue

                global_time = data_time[idx_time].split()[-1][:-1].split(':')
                global_time = float(int(global_time[0]) * 60 + float(global_time[1]))

            data = open(tree['RES_FILENAME']).readlines()

            if len(data) <= idx: continue
            if self.pattern not in data[idx]: continue

            time = float(data[idx].split()[-1][:-1])

            if self.rate:
                times.append(time/global_time)
            else:
                times.append(time)

        if len(times) > 0:
            self.tracer.add(times)
            tree['TITLE'] = self.title.replace(' ', '_')
            open('%(GRAPHDIR)s/%(TITLE)s_%(NAME)s_%(MANGLENAME)s.time' % tree, 'w').write(str(times))

class GlobalTime(ElapsedTimeCommand):
    def __init__(self, parser, tracer):
        ElapsedTimeCommand.__init__(self, parser, tracer, idx_name='GLOBAL_TIME_IDX', pattern='Elapsed time', title='Global elapsed rate time')

class ResultsSpeedup(Stat):
    """
    Generate some values for speedup based on the sequential execution results.
    """

    def __init__(self, parser, tracer, idx_name='GLOBAL_TIME_IDX', pattern='Elapsed time', title="Results Speedup"):
        Stat.__init__(self, parser, tracer)

        self.idx_name = idx_name
        self.pattern = pattern
        self.title = title

    def callit(self, options, tree):
        if not tree['PLOT']: return

        tree['MANGLENAME'] = '%(MANGLENAME_PATTERN)s' % tree % tree
        tree['SEQ_MANGLENAME'] = '%(SEQ_MANGLENAME_PATTERN)s' % tree % tree

        times = []

        for tree['NUM'] in xrange(1, tree['NRUNS']+1):
            tree['RES_FILENAME'] = '%(RESFILENAME_PATTERN)s' % tree % tree
            tree['SEQ_RES_FILENAME'] = '%(SEQ_RESFILENAME_PATTERN)s' % tree % tree

            idx = tree[self.idx_name]

            data = open(tree['RES_FILENAME']).readlines()
            seqdata = open(tree['SEQ_RES_FILENAME']).readlines()

            if len(data) <= idx: continue
            if self.pattern not in data[idx]: continue

            if len(seqdata) <= idx: continue
            if self.pattern not in seqdata[idx]: continue

            seqtime = float(seqdata[idx].split()[-1][:-1])
            partime = float(data[idx].split()[-1][:-1])
            # print seqtime, partime, seqtime / partime, tree['CORESIZE'], tree['NAME']
            times.append(seqtime / partime)

        if len(times) > 0:
            self.tracer.add(times)
            tree['TITLE'] = self.title.replace(' ', '_')
            open('%(GRAPHDIR)s/%(TITLE)s_%(NAME)s_%(MANGLENAME)s.data' % tree, 'w').write(str(times))

class ResultsEfficiency(Stat):
    """
    Generate some values for efficiency based on the sequential execution results.
    """

    def __init__(self, parser, tracer, idx_name='GLOBAL_TIME_IDX', pattern='Elapsed time', title="Results Efficiency"):
        Stat.__init__(self, parser, tracer)

        self.idx_name = idx_name
        self.pattern = pattern
        self.title = title

    def callit(self, options, tree):
        if not tree['PLOT']: return

        tree['MANGLENAME'] = '%(MANGLENAME_PATTERN)s' % tree % tree
        tree['SEQ_MANGLENAME'] = '%(SEQ_MANGLENAME_PATTERN)s' % tree % tree

        times = []

        for tree['NUM'] in xrange(1, tree['NRUNS']+1):
            tree['RES_FILENAME'] = '%(RESFILENAME_PATTERN)s' % tree % tree
            tree['SEQ_RES_FILENAME'] = '%(SEQ_RESFILENAME_PATTERN)s' % tree % tree

            idx = tree[self.idx_name]

            data = open(tree['RES_FILENAME']).readlines()
            seqdata = open(tree['SEQ_RES_FILENAME']).readlines()

            if len(data) <= idx: continue
            if self.pattern not in data[idx]: continue

            if len(seqdata) <= idx: continue
            if self.pattern not in seqdata[idx]: continue

            seqtime = float(seqdata[idx].split()[-1][:-1])
            partime = float(data[idx].split()[-1][:-1])
            #print seqtime, partime, seqtime / (partime * tree['CORESIZE']), tree['CORESIZE'], tree['NAME']
            times.append(seqtime / (partime * tree['CORESIZE']))

        if len(times) > 0:
            self.tracer.add(times)
            tree['TITLE'] = self.title.replace(' ', '_')
            open('%(GRAPHDIR)s/%(TITLE)s_%(NAME)s_%(MANGLENAME)s.data' % tree, 'w').write(str(times))
