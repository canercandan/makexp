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

"""
Variables interface

Browser classes enable to choose the order of experiences you want to test. Sometimes it is useful to define priorities for each test in order to get faster the results wished. This is mainly the case when you have a long waiting time.
"""

import optparse, logging, sys, os, subprocess, shutil
from datetime import datetime
import common
import browsers
from browsers import Browser, Sample, Pop, Core, Sequential, Restart, Starting, Dynamic, Schema, Command, Range, Execute, ProgressBar, Dummy

class Do(Browser):
    """
    Main class to call in passing in argument the parser
    and a browser class.
    Ugly name I know but called like that for historical reasons
    """

    def __init__(self, parser, browser=None, topic=None, other_topic=None):
        Browser.__init__(self, parser, browser)

        self.datename = str(datetime.today())
        for char in [' ', ':', '-', '.']: self.datename = self.datename.replace(char, '_')

        parser.add_option('-t', '--topic', default=topic, help='give here an experience path to use')
        parser.add_option('-O', '--other_topic', default=other_topic, help='give here another experience path to compare with the current one')

    def browse(self, options, tree):
        if not options.topic:
            raise ValueError('option --topic (-t) is missing')

        def makedirs(dirname):
            try:
                os.makedirs(dirname)
            except OSError:
                pass

        def inittree(t):
            d = {
                'MANGLENAME_PATTERN': '%(FIELD)s_%(COMMAND)s_%(SCHEMA)s_S%(POPSIZE)d_C%(CORESIZE)d',
                'SEQ_MANGLENAME_PATTERN': '%(FIELD)s_%(COMMAND)s_%(SCHEMA)s_S%(POPSIZE)d_C1',
                'TIMEFILENAME_PATTERN': '%(TIMEDIR)s/%(NAME)s_%(MANGLENAME)s.time.%(NUM)s',
                'RESFILENAME_PATTERN': '%(RESDIR)s/%(NAME)s_%(MANGLENAME)s.out.%(NUM)s',
                'SEQ_RESFILENAME_PATTERN': '%(RESDIR)s/%(NAME)s_%(SEQ_MANGLENAME)s.out.%(NUM)s',
                'PLANFILENAME_PATTERN': '%(RESDIR)s/%(NAME)s_%(MANGLENAME)s.soln.%(NUM)s',
                'COMMAND_PATTERN':\
                    '/usr/bin/time -v -o %(TIME_FILENAME)s '\
                    'timelimit -t %(TIMELIMIT)d '\
                    '%(MAKEXPDIR)s/%(COMMAND)s '\
                    '--seed=%(SEED)d '\
                    '--domain=%(DOMAIN)s '\
                    '--instance=%(INSTANCE)s '\
                    '--plan-file=%(PLAN_FILENAME)s '\
                    '--runs-max=%(RUNMAX)d '\
                    '--popSize=%(POPSIZE)d '\
                    '--gen-steady=%(GENSTEADY)d '\
                    '--parallelize-loop=%(PARALLELIZE)d '\
                    '--parallelize-nthreads=%(CORESIZE)d '\
                    '--parallelize-dynamic=%(SCHEMABOOL)d '\
                    '> %(RES_FILENAME)s',

                'RESDIR_PATTERN': '%(TOPIC)s/Res',
                'TIMEDIR_PATTERN': '%(TOPIC)s/Time',
                'MAKEXPDIR_PATTERN': '%(TOPIC)s/makexp_%(DATENAME)s',
                'GRAPHDIR_PATTERN': '%(TOPIC)s/graph_%(DATENAME)s',

                'SAMPLES': [],
                'NRUNS': 1,
                'POPSIZES': [],
                'CORESIZES': [],
                'BINARIES': [],
                'BINARYPATH': '.',
                'RESTART': False,
                'DYNAMIC': False,
                'EXECUTE': False,
                'PLOT': False,
                'PLOT_ON_WINDOW': False,
                'PARALLELIZE': True,
                'SEED': 0,
                'RUNMAX': 0,
                'GENSTEADY': 50,
                'TIMELIMIT': 1800,

                'TITLE': None,
                'XLABEL': None,
                'YLABEL': None,
                'POSITIONS': None,
                'XBOUND': None,
                'YBOUND': None,
                'LEGEND': True,
                'PROPERTIES': [],

                'SPEEDUP_IDX': 3,
                'EFFICIENCY_IDX': 3,
                'MAKESPAN_IDX': 2,
                'TOTALCOST_IDX': 3,
                'EVALUATION_TIME_IDX': 20,
                'VARIATION_TIME_IDX': 21,
                'REPLACE_TIME_IDX': 22,
                'GLOBAL_TIME_IDX': 23,
                'TIME_IDX': 4,

                'PROGRESSBAR_SIZE': 1,
                }
            t.update(d)

        def filltree(t):
            t['RESDIR'] = '%(RESDIR_PATTERN)s' % t % t
            t['TIMEDIR'] = '%(TIMEDIR_PATTERN)s' % t % t
            t['MAKEXPDIR'] = '%(MAKEXPDIR_PATTERN)s' % t % t
            t['GRAPHDIR'] = '%(GRAPHDIR_PATTERN)s' % t % t

        tree['TOPIC'] = options.topic
        tree['OTHER_TOPIC'] = options.other_topic
        tree['DATENAME'] = self.datename

        inittree(tree)
        tree.update(eval(''.join(open('%(TOPIC)s/variables.py' % tree).readlines())))
        filltree(tree)

        if options.other_topic:
            tree['OTHER'] = otree = {}
            otree['TOPIC'] = options.other_topic
            otree['DATENAME'] = self.datename

            inittree(otree)
            otree.update(eval(''.join(open('%(TOPIC)s/variables.py' % otree).readlines())))
            filltree(otree)

            otree['RESDIR'] = '%(RESDIR_PATTERN)s' % otree % otree
            otree['TIMEDIR'] = '%(TIMEDIR_PATTERN)s' % otree % otree
            otree['MAKEXPDIR'] = '%(MAKEXPDIR_PATTERN)s' % otree % otree
            otree['GRAPHDIR'] = '%(GRAPHDIR_PATTERN)s' % otree % otree

        # create needed directories
        if tree['EXECUTE']:
            for key in ['RESDIR', 'TIMEDIR', 'MAKEXPDIR']: makedirs(tree[key])
            dirname = os.path.dirname(sys.argv[0])
            script = os.path.basename(sys.argv[0])
            for f in [script, 'browsers.py', 'common.py', 'stats.py', 'tracers.py']:
                shutil.copy2("%s/%s" % (dirname, f), "%(MAKEXPDIR)s/" % tree)

            open('%(TOPIC)s/COMMAND' % tree, 'w').write("%s\n" % ' '.join(sys.argv))
            open('%(TOPIC)s/README' % tree, 'w').write(tree['DESCRIPTION'])

        if not os.path.isdir(tree['TOPIC']):
            self.logger.error('the topic (directory) %(TOPIC)s doesnot exist.' % tree)
            return

        if tree['PLOT']: makedirs(tree['GRAPHDIR'])

        self.browseAll(tree)
