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

import common

class Tracer(common.Base):
    """
    Base class for tracer classes.
    """

    def __init__(self, parser, title=None, xlabel=None, ylabel=None):
        common.Base.__init__(self, parser)

        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel

        self.values = []

    def callit(self, options, tree):
        if not options.plot: return
        if len(self.values) <= 0: return

        self.trace(options, tree)
        del self.values[:]

    def add(self, value):
        self.values.append(value)

class VariablesOnTracer(common.Base):
    """
    Base class for tracer classes.
    """

    def __init__(self, parser):
        common.Base.__init__(self, parser)

        self.values = []

    def callit(self, options, tree):
        if not tree['PLOT']: return
        if len(self.values) <= 0: return

        self.trace(options, tree)
        del self.values[:]

    def add(self, value):
        self.values.append(value)

class Easy(Tracer):
    """
    A generic class in order to trace data generated by stat classes.
    """

    def __init__(self, parser, title=None, xlabel=None, ylabel=None, positions=None):
        Tracer.__init__(self, parser, title, xlabel, ylabel)

        self.positions = positions

    def trace(self, options, tree):
        if options.plot_on_window: return

        import pylab as pl

        fig = pl.figure()
        ax = fig.add_subplot(111)

        ax.boxplot(self.values)

        if self.positions: ax.set_xticklabels(self.positions)
        if self.xlabel: ax.set_xlabel(self.xlabel)
        if self.ylabel: ax.set_ylabel(self.ylabel)

        tree['MANGLENAME'] = options.manglename_pattern % tree
        filename = '%(NAME)s_%(MANGLENAME)s.pdf' % tree

        fig.savefig('%s/%s_%s' % (tree["GRAPHDIR"], self.title.replace(' ', '_') if self.title else 'notitle', filename), format='pdf', dpi=280)

class VariablesOnEasy(VariablesOnTracer):
    """
    A generic class in order to trace data generated by stat classes.
    """

    def __init__(self, parser, title=None, xlabel=None, ylabel=None, xbound=None, ybound=None):
        VariablesOnTracer.__init__(self, parser)

        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.xbound = xbound
        self.ybound = ybound

    def trace(self, options, tree):
        if tree['PLOT_ON_WINDOW']: return

        import pylab as pl

        fig = pl.figure()
        ax = fig.add_subplot(111)

        ax.boxplot(self.values)

        for first, second, func in [
            (None, tree['POSITIONS'], ax.set_xticklabels),
            (self.xlabel, tree['XLABEL'], ax.set_xlabel),
            (self.ylabel, tree['YLABEL'], ax.set_ylabel),
            (self.xbound, tree['XBOUND'], ax.set_xbound),
            (self.ybound, tree['YBOUND'], ax.set_ybound),
            ]:
            if first: func(first)
            elif second: func(second)

        tree['MANGLENAME'] = '%(MANGLENAME_PATTERN)s' % tree % tree
        tree['FILENAME'] = '%(NAME)s_%(MANGLENAME)s.pdf' % tree

        if self.title: tree['TITLE'] = self.title.replace(' ', '_')
        elif tree['TITLE']: tree['TITLE'] = tree['TITLE'].replace(' ', '_')
        else: tree['TITLE'] = 'notitle'

        fig.savefig('%(GRAPHDIR)s/%(TITLE)s_%(FILENAME)s' % tree, format='pdf', dpi=280)

class AbsoluteTimeProportions(Tracer):
    """
    A high level tracer for multiple boxplots in order to compare several data having commons parameters.
    """

    def __init__(self, parser, popsizes=None, coresizes=None, binaries=None, samples=None, ratetimes=[], restart=False, ybound=None, legend=True):
        Tracer.__init__(self, parser)

        self.popsizes = popsizes
        self.coresizes = coresizes
        self.binaries = binaries
        self.samples = samples
        self.ratetimes = ratetimes
        self.restart = restart
        self.ybound = ybound
        self.legend = legend

        self.properties = [
            (-0.1, 'green'),
            (-0.2, 'black'),
            (0.1, 'red'),
            (0.2, 'blue'),
            (0.3, 'gray'),
            (0, 'orange')
            ]

        self.values = [0]

    def trace(self, options, tree):
        import pylab as pl

        tree['POPSIZES'] = self.popsizes
        tree['CORESIZES'] = self.coresizes
        tree['BINARIES'] = self.binaries
        tree['SAMPLES'] = self.samples
        tree['FIELD'] = 'RESTART' if self.restart else ''

        fig = pl.figure()

        for tree['CORESIZE'] in tree['CORESIZES']:
            for tree['COMMAND'] in tree['BINARIES']:
                for k in xrange(len(self.ratetimes)):
                    tree['TITLE'] = self.ratetimes[k]
                    ax = fig.add_subplot(1, len(self.ratetimes), k+1)

                    for i in xrange(len(tree['SAMPLES'])):
                        pos, color = self.properties[i]
                        tree['NAME'] = tree['SAMPLES'][i][0]

                        data = []

                        for tree['POPSIZE'] in tree['POPSIZES']:
                            data.append(eval(open('%(GRAPHDIR)s/%(TITLE)s_%(NAME)s_%(MANGLENAME)s.time' % tree).readline()))

                        r = ax.boxplot(data, positions=[x-pos for x in xrange(len(data))], widths=0.1)

                        for value in r.values():
                            pl.setp(value, color=color)

                    ax.set_xticklabels(tree['POPSIZES'])

                    if self.legend:
                        if k == len(self.ratetimes)-1:
                            ax.legend(tuple(['%s(%s)' % (tree['SAMPLES'][i][0], self.properties[i][1]) for i in xrange(len(tree['SAMPLES']))]))

                    ax.set_title('%(TITLE)s' % tree)
                    ax.set_xlabel('# populations')
                    ax.set_ylabel('Absolute time')

                    if self.ybound:
                        ax.set_ybound(0, self.ybound)

                if not options.plot_on_window:
                    tree['MANGLENAME'] = options.manglename_pattern % tree
                    tree['FILENAME'] = '%(MANGLENAME)s.pdf' % tree
                    fig.savefig('%(GRAPHDIR)s/TimeRatesByOperator_%(FILENAME)s' % tree, format='pdf', dpi=280)

        if options.plot_on_window:
            pl.show()

class VariablesOnAbsoluteTimeProportions(VariablesOnTracer):
    """
    A high level tracer for multiple boxplots in order to compare several data having commons parameters.
    """

    def __init__(self, parser, ratetimes=[], title=None, xlabel=None, ylabel=None):
        VariablesOnTracer.__init__(self, parser)

        self.ratetimes = ratetimes

        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel

        self.values = [0]

    def trace(self, options, tree):
        import pylab as pl

        tree['FIELD'] = 'RESTART' if tree['RESTART'] else ''
        tree['SCHEMA'] = 'DYNAMIC' if tree['DYNAMIC'] else 'STATIC'

        fig = pl.figure()

        for tree['CORESIZE'] in tree['CORESIZES']:
            for tree['COMMAND'] in tree['BINARIES']:
                axes = []

                for k in xrange(len(self.ratetimes)):
                    tree['TITLE'] = self.ratetimes[k]
                    ax = fig.add_subplot(1, len(self.ratetimes), k+1)

                    for i in xrange(len(tree['SAMPLES'])):
                        pos, color = tree['PROPERTIES'][i]
                        tree['NAME'] = tree['SAMPLES'][i][0]

                        data = []

                        for tree['POPSIZE'] in tree['POPSIZES']:
                            tree['MANGLENAME'] = '%(MANGLENAME_PATTERN)s' % tree % tree

                            data.append(eval(open('%(GRAPHDIR)s/%(TITLE)s_%(NAME)s_%(MANGLENAME)s.time' % tree).readline()))

                        r = ax.boxplot(data, positions=[x-pos for x in xrange(len(data))], widths=0.1)

                        for value in r.values():
                            pl.setp(value, color=color)

                    if tree['LEGEND']:
                        if k == len(self.ratetimes)-1:
                            ax.legend(tuple(['%s(%s)' % (tree['SAMPLES'][i][0], tree['PROPERTIES'][i][1]) for i in xrange(len(tree['SAMPLES']))]))

                    ax.set_xlabel('# populations')
                    ax.set_ylabel('Absolute time')

                    for first, second, func in [
                        (None, tree['POPSIZES'], ax.set_xticklabels),
                        (self.xlabel, tree['XLABEL'], ax.set_xlabel),
                        (self.ylabel, tree['YLABEL'], ax.set_ylabel),
                        (self.title, tree['TITLE'], ax.set_title),
                        ]:
                        if first: func(first)
                        elif second: func(second)

                    axes.append(ax)

                max_bound = max([ax.get_ybound() for ax in axes])
                for ax in axes: ax.set_ybound(max_bound)

                if not tree['PLOT_ON_WINDOW']:
                    tree['MANGLENAME'] = '%(MANGLENAME_PATTERN)s' % tree % tree
                    tree['FILENAME'] = '%(MANGLENAME)s.pdf' % tree
                    fig.savefig('%(GRAPHDIR)s/TimeRatesByOperator_%(FILENAME)s' % tree, format='pdf', dpi=280)

        if tree['PLOT_ON_WINDOW']:
            pl.show()

class OperatorsTimeProportions(AbsoluteTimeProportions):
    def __init__(self, parser, popsizes=None, coresizes=None, binaries=None, samples=None, restart=False, ybound=None):
        AbsoluteTimeProportions.__init__(self, parser, popsizes, coresizes, binaries, samples, restart=restart, ybound=ybound,
                                         ratetimes=['Evaluation_elapsed_rate_time',
                                                    'Replace_elapsed_rate_time',
                                                    'Variation_elapsed_rate_time']
                                         )

class VariablesOnOperatorsTimeProportions(VariablesOnAbsoluteTimeProportions):
    def __init__(self, parser, title=None, xlabel=None, ylabel=None):
        VariablesOnAbsoluteTimeProportions.__init__(self, parser,
                                                    ratetimes=['Evaluation_elapsed_rate_time',
                                                               'Replace_elapsed_rate_time',
                                                               'Variation_elapsed_rate_time'],
                                                    title=title, xlabel=xlabel, ylabel=ylabel
                                                    )

class GlobalAbsoluteTime(AbsoluteTimeProportions):
    def __init__(self, parser, popsizes=None, coresizes=None, binaries=None, samples=None, restart=False, ybound=None):
        AbsoluteTimeProportions.__init__(self, parser, popsizes, coresizes, binaries, samples, restart=restart, ybound=ybound, ratetimes=['Global_elapsed_rate_time'])

class VariablesOnGlobalAbsoluteTime(VariablesOnAbsoluteTimeProportions):
    def __init__(self, parser, title=None, xlabel=None, ylabel=None):
        VariablesOnAbsoluteTimeProportions.__init__(self, parser, ratetimes=['Global_elapsed_rate_time'],
                                                    title=title, xlabel=xlabel, ylabel=ylabel)

class VariablesOnGlobalTimeSpeedup(VariablesOnTracer):
    def __init__(self, parser):
        VariablesOnTracer.__init__(self, parser)

        self.ratetimes = ['Global_elapsed_rate_time']
        self.values = [0]

        self.rate = False
        self.pattern = 'Elapsed time'

    def trace(self, options, tree):
        if not options.other_topic:
            raise ValueError('option --other_topic (-O) is missing')

        otree = tree['OTHER']

        import pylab as pl

        tree['FIELD'] = 'RESTART' if tree['RESTART'] else ''
        otree['FIELD'] = 'RESTART' if otree['RESTART'] else ''

        tree['SCHEMA'] = 'DYNAMIC' if tree['DYNAMIC'] else 'STATIC'
        otree['SCHEMA'] = 'DYNAMIC' if otree['DYNAMIC'] else 'STATIC'

        fig = pl.figure()

        for tree['CORESIZE'] in tree['CORESIZES']:
            otree['CORESIZE'] = tree['CORESIZE']

            for tree['COMMAND'] in tree['BINARIES']:
                otree['COMMAND'] = tree['COMMAND']

                for k in xrange(len(self.ratetimes)):
                    tree['TITLE'] = otree['TITLE'] = self.ratetimes[k]
                    ax = fig.add_subplot(1, len(self.ratetimes), k+1)

                    for i in xrange(len(tree['SAMPLES'])):
                        pos, color = tree['PROPERTIES'][i]
                        tree['NAME'] = otree['NAME'] = tree['SAMPLES'][i][0]

                        data = []

                        for tree['POPSIZE'] in tree['POPSIZES']:
                            otree['POPSIZE'] = tree['POPSIZE']

                            tree['MANGLENAME'] = '%(MANGLENAME_PATTERN)s' % tree % tree
                            otree['MANGLENAME'] = '%(MANGLENAME_PATTERN)s' % otree % otree

                            idx = tree['GLOBAL_TIME_IDX']
                            times = []
                            otimes = []

                            for tree['NUM'] in xrange(1, tree['NRUNS']+1):
                                otree['NUM'] = tree['NUM']

                                tree['RES_FILENAME'] = '%(RESFILENAME_PATTERN)s' % tree % tree
                                otree['RES_FILENAME'] = '%(RESFILENAME_PATTERN)s' % otree % otree

                                tree['TIME_FILENAME'] = '%(TIMEFILENAME_PATTERN)s' % tree % tree
                                otree['TIME_FILENAME'] = '%(TIMEFILENAME_PATTERN)s' % otree % otree

                                global_time = None
                                oglobal_time = None

                                if self.rate:
                                    idx_time = tree['TIME_IDX']
                                    data_time = open(tree['TIME_FILENAME']).readlines()
                                    if len(data_time) <= idx_time: continue
                                    if 'Elapsed (wall clock) time' not in data_time[idx_time]: continue

                                    odata_time = open(otree['TIME_FILENAME']).readlines()
                                    if len(odata_time) <= idx_time: continue
                                    if 'Elapsed (wall clock) time' not in odata_time[idx_time]: continue

                                    global_time = data_time[idx_time].split()[-1][:-1].split(':')
                                    global_time = float(int(global_time[0]) * 60 + float(global_time[1]))

                                    oglobal_time = data_time[idx_time].split()[-1][:-1].split(':')
                                    oglobal_time = float(int(oglobal_time[0]) * 60 + float(oglobal_time[1]))


                                local_data = open(tree['RES_FILENAME']).readlines()
                                olocal_data = open(otree['RES_FILENAME']).readlines()

                                if len(local_data) <= idx: continue
                                if self.pattern not in local_data[idx]: continue

                                if len(olocal_data) <= idx: continue
                                if self.pattern not in olocal_data[idx]: continue

                                time = float(local_data[idx].split()[-1][:-1])
                                otime = float(olocal_data[idx].split()[-1][:-1])

                                if self.rate:
                                    times.append(time/global_time)
                                    otimes.append(otime/oglobal_time)
                                else:
                                    times.append(time)
                                    otimes.append(otime)

                            for i in xrange(len(times)): otimes[i] /= times[i]

                            data.append(otimes)

                        r = ax.boxplot(data, positions=[x-pos for x in xrange(len(data))], widths=0.1)

                        for value in r.values():
                            pl.setp(value, color=color)

                    ax.set_xticklabels(tree['POPSIZES'])

                    if tree['LEGEND']:
                        if k == len(self.ratetimes)-1:
                            ax.legend(tuple(['%s(%s)' % (tree['SAMPLES'][i][0], tree['PROPERTIES'][i][1]) for i in xrange(len(tree['SAMPLES']))]))

                    ax.set_title('%(TITLE)s' % tree)

                    if tree['XLABEL']: ax.set_xlabel(tree['XLABEL'])

                    ax.set_ylabel('Speedup')

                    if tree['XBOUND']: ax.set_xbound(0, tree['XBOUND'])
                    if tree['YBOUND']: ax.set_ybound(0, tree['YBOUND'])

                if not tree['PLOT_ON_WINDOW']:
                    tree['MANGLENAME'] = '%(MANGLENAME_PATTERN)s' % tree % tree
                    tree['FILENAME'] = '%(MANGLENAME)s.pdf' % tree
                    fig.savefig('%(GRAPHDIR)s/GlobalTimeSpeedup_%(FILENAME)s' % tree, format='pdf', dpi=280)

        if tree['PLOT_ON_WINDOW']:
            pl.show()

class VariablesOnGlobalEfficiency(VariablesOnTracer):
    """
    A high level tracer for multiple boxplots in order to compare several data having commons parameters. The parameter used here is the efficiency.
    """

    def __init__(self, parser, xlabel=None, ylabel=None, xbound=None, ybound=None):
        VariablesOnTracer.__init__(self, parser)

        self.title = 'Efficiency'
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.xbound = xbound
        self.ybound = ybound

        self.values = [0]

    def trace(self, options, tree):
        import pylab as pl

        tree['FIELD'] = 'RESTART' if tree['RESTART'] else ''
        tree['SCHEMA'] = 'DYNAMIC' if tree['DYNAMIC'] else 'STATIC'

        tree['TITLE'] = self.title

        fig = pl.figure()

        for tree['CORESIZE'] in tree['CORESIZES']:
            for tree['COMMAND'] in tree['BINARIES']:
                ax = fig.add_subplot(111)

                for i in xrange(len(tree['SAMPLES'])):
                    pos, color = tree['PROPERTIES'][i]
                    tree['NAME'] = tree['SAMPLES'][i][0]

                    data = []

                    for tree['POPSIZE'] in tree['POPSIZES']:
                        tree['MANGLENAME'] = '%(MANGLENAME_PATTERN)s' % tree % tree

                        data.append(eval(open('%(GRAPHDIR)s/%(TITLE)s_%(NAME)s_%(MANGLENAME)s.data' % tree).readline()))

                    r = ax.boxplot(data, positions=[x-pos for x in xrange(len(data))], widths=0.1)

                    for value in r.values():
                        pl.setp(value, color=color)

                # if tree['LEGEND']:
                #     ax.legend(tuple(['%s(%s)' % (tree['SAMPLES'][i][0], tree['PROPERTIES'][i][1]) for i in xrange(len(tree['SAMPLES']))]))

                ax.set_xlabel('# populations')
                ax.set_ylabel('Efficiency')

                for first, second, func in [
                    (None, tree['POPSIZES'], ax.set_xticklabels),
                    (self.xlabel, tree['XLABEL'], ax.set_xlabel),
                    (self.ylabel, tree['YLABEL'], ax.set_ylabel),
                    (self.xbound, tree['XBOUND'], ax.set_xbound),
                    (self.ybound, tree['YBOUND'], ax.set_ybound),
                    (self.title, tree['TITLE'], ax.set_title),
                    ]:
                    if first: func(first)
                    elif second: func(second)

                if not tree['PLOT_ON_WINDOW']:
                    tree['MANGLENAME'] = '%(MANGLENAME_PATTERN)s' % tree % tree
                    tree['FILENAME'] = '%(MANGLENAME)s.pdf' % tree
                    fig.savefig('%(GRAPHDIR)s/GlobalEfficiency_%(FILENAME)s' % tree, format='pdf', dpi=280)

        if tree['PLOT_ON_WINDOW']:
            pl.show()
