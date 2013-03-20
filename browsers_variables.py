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
from browsers import *

class Do(Browser):
    """
    Main class to call in passing in argument the parser
    and a browser class.
    Ugly name I know but called like that for historical reasons
    """

    def __init__(self, parser, browser=None, workdir=None, other_workdir=None):
        Browser.__init__(self, parser, browser)

        self.datename = str(datetime.today())
        for char in [' ', ':', '-', '.']: self.datename = self.datename.replace(char, '_')

        parser.add_option('-w', '--working_directory', dest='workdir', default=workdir, help='Working directory where the experiments will be done.')
        parser.add_option('-c', '--compare_with', dest='other_workdir', default=other_workdir, help='Another working directory to compare with the current one.')


    def browse(self, options, tree):
        if not options.workdir:
            raise ValueError('option --working_directory (-w) is missing')

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
                'STATFILENAME_PATTERN': '%(STATDIR)s/%(TITLE)s_%(NAME)s_%(MANGLENAME)s.stat',
                'GRAPHFILENAME_PATTERN': '%(STATDIR)s/%(TITLE)s_%(NAME)s_%(MANGLENAME)s.data',
                'SEQ_RESFILENAME_PATTERN': '%(RESDIR)s/%(NAME)s_%(SEQ_MANGLENAME)s.out.%(NUM)s',
                # 'TIMELIMIT_COMMAND_PATTERN': 'timelimit -t %(TIMELIMIT)d',
                'TIMEOUT_COMMAND_PATTERN': 'timeout %(TIMEOUT)d',
                'COMMAND_PATTERN':\
                    '/usr/bin/time -v -o %(TIME_FILENAME)s '\
                    # '%(TIMELIMIT_COMMAND)s '\
                    '%(TIMEOUT_COMMAND)s '\
                    '%(MAKEXPDIR)s/%(COMMAND)s '\
                    '--seed=%(SEED)d '\
                    '--domain=%(DOMAIN)s '\
                    '--instance=%(INSTANCE)s '\
                    '--plan-file=%(PLAN_FILENAME)s '\
                    '--runs-max=%(RUNMAX)d '\
                    '--popSize=%(POPSIZE)d '\
                    '--gen-min=%(GENMIN)d '\
                    '--gen-steady=%(GENSTEADY)d '\
                    '--gen-max=%(GENMAX)d '\
                    '--parallelize-loop=%(PARALLELIZE)d '\
                    '--parallelize-nthreads=%(CORESIZE)d '\
                    '--parallelize-dynamic=%(SCHEMABOOL)d '\
                    '--parallelize-enable-results=1 '\
                    '--parallelize-prefix=%(RES_FILENAME)s ' \
                    '--status=%(RES_FILENAME)s.status '\
                    '> %(RES_FILENAME)s',

                'RESDIR_PATTERN': '%(WORKDIR)s/Res',
                'TIMEDIR_PATTERN': '%(WORKDIR)s/Time',
                'STATDIR_PATTERN': '%(WORKDIR)s/Stat',
                'MAKEXPDIR_PATTERN': '%(WORKDIR)s/makexp_%(DATENAME)s',
                'GRAPHDIR_PATTERN': '%(WORKDIR)s/graph_%(DATENAME)s',

                'SAMPLES': [],
                'NRUNS': 1,
                'POPSIZES': [],
                'POPSIZE': 0,
                'CORESIZES': [],
                'CORESIZE': 0,
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
                'GENMIN': 10,
                'GENSTEADY': 50,
                'GENMAX': 1000,
                # 'TIMELIMIT': 1800,
                'TIMEOUT': 1800,

                'TITLE': None,
                'XLABEL': None,
                'YLABEL': None,
                'POSITIONS': None,
                'XBOUND': None,
                'YBOUND': None,
                'LEGEND': True,
                'PROPERTIES': [],
                'EXTENSIONS': ['pdf', 'png'],

                'PROGRESSBAR_SIZE': 1,
                }
            t.update(d)

        def filltree(t):
            t['RESDIR'] = '%(RESDIR_PATTERN)s' % t % t
            t['TIMEDIR'] = '%(TIMEDIR_PATTERN)s' % t % t
            t['STATDIR'] = '%(STATDIR_PATTERN)s' % t % t
            t['MAKEXPDIR'] = '%(MAKEXPDIR_PATTERN)s' % t % t
            t['GRAPHDIR'] = '%(GRAPHDIR_PATTERN)s' % t % t

        tree['WORKDIR'] = options.workdir
        tree['OTHER_WORKDIR'] = options.other_workdir
        tree['DATENAME'] = self.datename

        if not os.path.isdir(tree['WORKDIR']):
            makedirs(tree['WORKDIR'])
            shutil.copy('default_variables.py', '%(WORKDIR)s/variables.py' % tree)
            self.logger.info('The working directory %(WORKDIR)s was just created take your time to configure it and run it again.' % tree)
            return

        inittree(tree)
        tree.update(eval(''.join(open('%(WORKDIR)s/variables.py' % tree).readlines())))
        filltree(tree)

        if options.other_workdir:
            tree['OTHER'] = otree = {}
            otree['WORKDIR'] = options.other_workdir
            otree['DATENAME'] = self.datename

            inittree(otree)
            otree.update(eval(''.join(open('%(WORKDIR)s/variables.py' % otree).readlines())))
            filltree(otree)

        # create needed directories
        if tree['EXECUTE']:
            for key in ['RESDIR', 'TIMEDIR', 'STATDIR', 'MAKEXPDIR']: makedirs(tree[key])
            dirname = os.path.dirname(sys.argv[0])
            script = os.path.basename(sys.argv[0])
            for f in [script,
                      'browsers.py', 'browsers_options.py', 'browsers_variables.py',
                      'stats.py', 'stats_options.py', 'stats_variables.py',
                      'tracers.py', 'tracers_options.py', 'tracers_variables.py',
                      'common.py', 'parser.py'
                      ]:
                print("%s/%s" % (dirname, f), "%(MAKEXPDIR)s/" % tree)
                shutil.copy("%s/%s" % (dirname, f), "%(MAKEXPDIR)s/" % tree)

            open('%(WORKDIR)s/COMMAND' % tree, 'w').write("%s\n" % ' '.join(sys.argv))
            open('%(WORKDIR)s/README' % tree, 'w').write(tree['DESCRIPTION'])

        if not os.path.isdir(tree['WORKDIR']):
            self.logger.error('The working directory %(WORKDIR)s doesnot exist.' % tree)
            return

        if tree['PLOT']: makedirs(tree['GRAPHDIR'])

        self.browseAll(tree)
