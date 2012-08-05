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
Options interface

Browser classes enable to choose the order of experiences you want to test. Sometimes it is useful to define priorities for each test in order to get faster the results wished. This is mainly the case when you have a long waiting time.
"""

import optparse, logging, sys, os, subprocess, shutil
from datetime import datetime
import common
import browser
from browser import Dummy

class Do(browser.Browser):
    """
    Main class to call in passing in argument the parser
    and a browser class.
    Ugly name I know but called like that for historical reasons
    """

    def __init__(self, parser, browser=None, workdir=None, other_workdir=None, execute=False, plot=False,
                 manglename_pattern='%(FIELD)s_%(COMMAND)s_%(SCHEMA)s_S%(POPSIZE)d_C%(CORESIZE)d',
                 timefilename_pattern='%(TIMEDIR)s/%(NAME)s_%(MANGLENAME)s.time.%(NUM)s',
                 resfilename_pattern='%(RESDIR)s/%(NAME)s_%(MANGLENAME)s.out.%(NUM)s',
                 planfilename_pattern='%(RESDIR)s/%(NAME)s_%(MANGLENAME)s.soln.%(NUM)s',
                 timelimit_command_pattern='timelimit -t %(TIMELIMIT)d',
                 command_pattern=\
                     '/usr/bin/time -v -o %(TIME_FILENAME)s '\
                     '%(TIMELIMIT_COMMAND)s '\
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
                     '--status=%(RES_FILENAME)s.status ' \
                     '> %(RES_FILENAME)s',
                 description='No description\n'):

        Browser.__init__(self, parser, browser)

        self.datename = str(datetime.today())
        for char in [' ', ':', '-', '.']: self.datename = self.datename.replace(char, '_')

        parser.add_option('-w', '--working_directory', dest='workdir', default=workdir if workdir else self.datename, help='Working directory where the experiments will be done.')
        parser.add_option('-c', '--compare_with', dest='other_workdir', default=other_workdir, help='Another working directory to compare with the current one.')

        parser.add_option('-e', '--execute', action='store_true', default=execute, help='execute experiences')
        parser.add_option('-p', '--plot', action='store_true', default=plot, help='plot data')
        parser.add_option('-P', '--plot_on_window', action='store_true', default=False, help='plot data on window instead of file')

        parser.add_option('-W', '--manglename_pattern', default=manglename_pattern, help='give here a pattern for mangle name')
        parser.add_option('-X', '--timefilename_pattern', default=timefilename_pattern, help='give here a pattern for time filename')
        parser.add_option('-Y', '--resfilename_pattern', default=resfilename_pattern, help='give here a pattern for result filename')
        parser.add_option('-Z', '--planfilename_pattern', default=planfilename_pattern, help='give here a pattern for plan filename')
        parser.add_option('-C', '--command_pattern', default=command_pattern, help='give here a pattern for command')

        parser.add_option('-d', '--description', default=description, help='give here a description of your experience. This is saved in README file')

    def browse(self, options, tree):
        if not options.workdir:
            raise ValueError('option --working_directory (-w) is missing')

        def makedirs(dirname):
            try:
                os.makedirs(dirname)
            except OSError:
                pass

        tree['WORKDIR'] = options.workdir
        tree['OTHER_WORKDIR'] = options.other_workdir
        tree['DATENAME'] = self.datename

        tree['RESDIR'] = '%(WORKDIR)s/Res' % tree
        tree['TIMEDIR'] = '%(WORKDIR)s/Time' % tree
        tree['MAKEXPDIR'] = '%(WORKDIR)s/makexp_%(DATENAME)s' % tree
        tree['GRAPHDIR'] = '%(WORKDIR)s/graph_%(DATENAME)s' % tree

        if options.other_workdir:
            tree['OTHER_RESDIR'] = '%(OTHER_WORKDIR)s/Res' % tree
            tree['OTHER_TIMEDIR'] = '%(OTHER_WORKDIR)s/Time' % tree
            tree['OTHER_MAKEXPDIR'] = '%(OTHER_WORKDIR)s/makexp_%(DATENAME)s' % tree
            tree['OTHER_GRAPHDIR'] = '%(OTHER_WORKDIR)s/graph_%(DATENAME)s' % tree

        # create needed directories
        if options.execute:
            for key in ['RESDIR', 'TIMEDIR', 'MAKEXPDIR']: makedirs(tree[key])
            dirname = os.path.dirname(sys.argv[0])
            script = os.path.basename(sys.argv[0])
            for f in [script,
                      'browsers.py', 'browsers_options.py', 'browsers_variables.py',
                      'stats.py', 'stats_options.py', 'stats_variables.py',
                      'tracers.py', 'tracers_options.py', 'tracers_variables.py',
                      'common.py',
                      ]:
                shutil.copy2("%s/%s" % (dirname, f), "%(MAKEXPDIR)s/" % tree)

            open('%(WORKDIR)s/COMMAND' % tree, 'w').write("%s\n" % ' '.join(sys.argv))
            open('%(WORKDIR)s/README' % tree, 'w').write(options.description)

        if not os.path.isdir(tree['WORKDIR']):
            self.logger.error('The working directory %(WORKDIR)s doesnot exist.' % tree)
            return

        if options.plot: makedirs(tree["GRAPHDIR"])

        self.browseAll(tree)

class Sample(browsers.Sample):
    def __init__(self, parser, samples, browser=None):
        browsers.Sample.__init__(self, parser, browser)
        self.samples = samples

    def browse(self, options, tree):
        tree['SAMPLES'] = self.samples
        browsers.Sample.browse(self, options, tree)

class Pop(browsers.Pop):
    def __init__(self, parser, popsizes, browser=None):
        browsers.Pop.__init__(self, parser, browser)
        self.popsizes = popsizes

    def browse(self, options, tree):
        tree['POPSIZES'] = self.popsizes
        browsers.Pop.browse(self, options, tree)

class Core(browsers.Core):
    def __init__(self, parser, coresizes, browser=None, parallelize=True):
        browsers.Core.__init__(self, parser, browser)

        parser.add_option('-L', '--parallelize', action='store_true', default=parallelize, help='with parallelization')

        self.coresizes = coresizes

    def browse(self, options, tree):
        tree['PARALLELIZE'] = options.parallelize
        tree['CORESIZES'] = self.coresizes
        browsers.Core.browse(self, options, tree)

class Sequential(browsers.Sequential):
    def __init__(self, parser, browser=None):
        browsers.Sequential.__init__(self, parser, browser)

    def browse(self, options, tree):
        browsers.Sequential.browse(self, options, tree)

class Restart(browsers.Restart):
    def __init__(self, parser, browser=None, restart=False):
        browsers.Restart.__init__(self, parser, browser)

        parser.add_option('-R', '--restart', action='store_true', default=restart, help='with restarts')

    def browse(self, options, tree):
        tree['RESTART'] = options.restart
        tree['TIMELIMIT_COMMAND_PATTERN'] = options.timelimit_command_pattern
        browsers.Restart.browse(self, options, tree)

class Starting(browsers.Starting):
    def __init__(self, parser, browser=None):
        browsers.Starting.__init__(self, parser, browser)

    def browse(self, options, tree):
        tree['TIMELIMIT_COMMAND_PATTERN'] = options.timelimit_command_pattern
        browsers.Starting.browse(self, options, browser)

class Dynamic(browsers.Dynamic):
    def __init__(self, parser, browser=None, dynamic=False):
        browsers.Dynamic.__init__(self, parser, browser)

        parser.add_option('-D', '--dynamic', action='store_true', default=dynamic, help='use the dynamic scheduler in openmp')

    def browse(self, options, tree):
        tree['DYNAMIC'] = options.dynamic
        browsers.Dynamic.browse(self, options, tree)

class Schema(browsers.Schema):
    def __init__(self, parser, browser=None):
        browsers.Schema.__init__(self, parser, browser)

    def browse(self, options, tree):
        browsers.Schema.browse(self, options, tree)

class Command(browsers.Command):
    def __init__(self, parser, commands, browser=None, binarypath='.'):
        browsers.Command.__init__(self, parser, browser)

        parser.add_option('-B', '--binarypath', default=binarypath, help='give here binaries\' path')

        self.commands = commands

    def browse(self, options, tree):
        tree['BINARYPATH'] = options.binarypath
        tree['BINARIES'] = self.commands
        browsers.Command.browse(self, options, tree)

class Range(browsers.Range):
    def __init__(self, parser, browser=None, nruns=1):
        browsers.Range.__init__(self, parser, browser)

        parser.add_option('-N', '--nruns', type='int', default=nruns, help='give here a number of runs')

    def browse(self, options, tree):
        tree['NRUNS'] = options.nruns
        browsers.Range.browse(self, options, tree)

class Execute(browsers.Execute):
    def __init__(self, parser, seed=0, runmax=0, genmin=10, gensteady=50, genmax=1000, timelimit=1800, stat=None):
        browsers.Execute.__init__(self, parser, stat=stat)

        parser.add_option('-s', '--seed', type='int', default=seed, help='with seed fixed, seed=0 means seed defined randomly')
        parser.add_option('-M', '--runmax', type='int', default=runmax, help='with runmax fixed, runmax=0 means no limit')
        parser.add_option(None, '--genmin', type='int', default=genmin, help='with genmin fixed')
        parser.add_option('-G', '--gensteady', type='int', default=gensteady, help='with gensteady fixed')
        parser.add_option(None, '--genmax', type='int', default=genmax, help='with genmax fixed')
        parser.add_option('-T', '--timelimit', type='int', default=timelimit, help='with timelimit fixed')

    def browse(self, options, tree):
        tree['MANGLENAME_PATTERN'] = options.manglename_pattern
        tree['TIMEFILENAME_PATTERN'] = options.timefilename_pattern
        tree['RESFILENAME_PATTERN'] = options.resfilename_pattern
        tree['PLANFILENAME_PATTERN'] = options.planfilename_pattern
        tree['COMMAND_PATTERN'] = options.command_patten

        if options.runmax: tree['RUNMAX'] = options.runmax
        tree['SEED'] = options.seed
        tree['GENMIN'] = options.genmin
        tree['GENSTEADY'] = options.gensteady
        tree['GENMAX'] = options.genmax
        tree['TIMELIMIT'] = options.timelimit
        tree['EXECUTE'] = options.execute

        browsers.Execute.browse(self, options, tree)
