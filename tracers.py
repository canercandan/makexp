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

        parser.add_option('-p', '--plot', action='store_true', default=False, help='plot data')

        self.values = []

    def callit(self, options, tree):
        self.trace(options, tree)
        del self.values[:]

    def add(self, value):
        self.values.append(value)

class Fitness(Tracer):
    def __init__(self, parser):
        Tracer.__init__(self, parser)

    def trace(self, options, tree):
        if options.plot:
            import pylab

            if len(self.values) > 0:
                pylab.boxplot(self.values)
                pylab.xlabel('number of runs')
                pylab.ylabel('fitness')
                pylab.savefig('output.pdf', format='pdf')
                pylab.savefig('output.png', format='png')
                pylab.cla()
                pylab.clf()
