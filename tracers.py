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
    def __init__(self, parser, title=None, xlabel=None, ylabel=None):
        common.Base.__init__(self, parser)

        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel

        self.values = []

    def callit(self, options, tree):
        if not options.plot:
            return

        if len(self.values) <= 0:
            return

        self.trace(options, tree)
        del self.values[:]

    def add(self, value):
        self.values.append(value)

class Easy(Tracer):
    def __init__(self, parser, title=None, xlabel=None, ylabel=None, positions=None):
        Tracer.__init__(self, parser, title, xlabel, ylabel)

        self.positions = positions

    def trace(self, options, tree):
        if options.plot_on_window:
            return

        import pylab as pl

        fig = pl.figure()
        ax = fig.add_subplot(111)

        ax.boxplot(self.values)

        if self.positions: ax.set_xticklabels(self.positions)
        if self.xlabel: ax.set_xlabel(self.xlabel)
        if self.ylabel: ax.set_ylabel(self.ylabel)

        tree['MANGLENAME'] = options.manglename_pattern % tree
        filename = '%(NAME)s_%(MANGLENAME)s.svg' % tree

        fig.savefig('%s/%s_%s' % (tree["GRAPHDIR"], self.title.replace(' ', '_') if self.title else 'notitle', filename), format='svg', dpi=280)

class TimeRates(Tracer):
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
            (0, 'orange')]

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
            for tree['BINARY'] in tree['BINARIES']:
                for k in xrange(0, len(self.ratetimes)):
                    tree['RATETIME'] = self.ratetimes[k]
                    ax = fig.add_subplot(1, len(self.ratetimes), k+1)

                    for i in xrange(0, len(tree['SAMPLES'])):
                        pos, color = self.properties[i]
                        tree['NAME'] = tree['SAMPLES'][i][0]

                        data = []

                        for tree['POPSIZE'] in tree['POPSIZES']:
                            data.append(eval(open('%(GRAPHDIR)s/%(RATETIME)s_%(NAME)s_%(FIELD)s_%(BINARY)s_S%(POPSIZE)s_C%(CORESIZE)s.time' % tree).readline()))

                        r = ax.boxplot(data, positions=[x-pos for x in xrange(0,len(data))], widths=0.1)

                        for value in r.values():
                            pl.setp(value, color=color)

                    ax.set_xticklabels(tree['POPSIZES'])

                    if self.legend:
                        if k == len(self.ratetimes)-1:
                            ax.legend(tuple(['%s(%s)' % (tree['SAMPLES'][i][0], self.properties[i][1]) for i in xrange(0, len(tree['SAMPLES']))]))

                    ax.set_title('%(RATETIME)s' % tree)
                    ax.set_xlabel('# populations')
                    ax.set_ylabel('Absolute time')

                    if self.ybound:
                        ax.set_ybound(0, self.ybound)

                tree['MANGLENAME'] = options.manglename_pattern % tree
                tree['FILENAME'] = '%(MANGLENAME)s.svg' % tree

                if not options.plot_on_window:
                    fig.savefig('%(GRAPHDIR)s/TimeRatesByOperator_%(FILENAME)s' % tree, format='svg', dpi=280)

        if options.plot_on_window:
            pl.show()

class OperatorsTimeRates(TimeRates):
    def __init__(self, parser, popsizes=None, coresizes=None, binaries=None, samples=None, restart=False, ybound=None):
        TimeRates.__init__(self, parser, popsizes, coresizes, binaries, samples, restart=restart, ybound=ybound,
                           ratetimes=['Evaluation_elapsed_rate_time',
                                      'Replace_elapsed_rate_time',
                                      'Variation_elapsed_rate_time']
                           )

class GlobalTimeRates(TimeRates):
    def __init__(self, parser, popsizes=None, coresizes=None, binaries=None, samples=None, restart=False, ybound=None):
        TimeRates.__init__(self, parser, popsizes, coresizes, binaries, samples, restart=restart, ybound=ybound, ratetimes=['Global_elapsed_rate_time'])
