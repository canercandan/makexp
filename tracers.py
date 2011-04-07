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
    def __init__(self, parser):
        common.Base.__init__(self, parser)

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
    def __init__(self, parser, title=None, xlabel=None, ylabel=None):
        Tracer.__init__(self, parser)

        self.title = title if title else 'notitle'
        self.xlabel = xlabel
        self.ylabel = ylabel

    def trace(self, options, tree):
        import pylab
        pylab.boxplot(self.values)
        if self.xlabel: pylab.xlabel(self.xlabel)
        if self.ylabel: pylab.ylabel(self.ylabel)

        filename = '%(NAME)s_%(MANGLENAME_PATTERN)s.pdf' % tree % tree

        pylab.savefig('%s/%s_%s' % (tree["GRAPH_DIR"], self.title, filename), format='pdf')

        pylab.cla()
        pylab.clf()