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
Browser classes enable to choose the order of experiences you want to test. Sometimes it is useful to define priorities for each test in order to get faster the results wished. This is mainly the case when you have a long waiting time.
"""

import optparse, logging, sys, os, subprocess, shutil
from datetime import datetime
import common

class Browser(common.Base):
    """
    Base class for Browser classes
    """

    def __init__(self, parser, browser=None, stat=None, tracer=None):
        common.Base.__init__(self, parser)

        self.browsers = []
        self.stats = []
        self.tracers = []

        if browser:
            self.browsers.append(browser)

        if stat:
            self.stats.append(stat)

        if tracer:
            self.tracers.append(tracer)

    def callit(self, options, tree):
        """
        Here's the main method used by all browser classes in order to update the tree passed as argument.
        """

        self.browse(options, tree)
        self.statAll(tree)
        self.tracerAll(tree)

    def add(self, browser):
        """
        Useful if you want to link several calls to add method. The return instance is the new added browser in order to add the next browser into this last.
        Example: browser.add(browser1).add(browser2).add(browser3)...
        """

        assert browser != None
        self.browsers.append(browser)
        return browser

    def addC(self, browser):
        """
        Useful if you want to link several calls to add method together but in using the same instance
        Example: browser.addC(browser1).addC(browser2).addC(browser3)...
        """

        assert browser != None
        self.browsers.append(browser)
        return self

    def addStats(self, stats):
        assert stats != None
        self.stats += stats
        return self

    def addTracers(self, tracers):
        assert tracers != None
        self.tracers += tracers
        return self

    def addMany(self, browsers):
        assert browsers != None
        self.browsers += browsers
        return self

    def browseAll(self, tree):
        for browser in self.browsers:
            browser(tree)

    def statAll(self, tree):
        for stat in self.stats:
            stat(tree)

    def tracerAll(self, tree):
        for tracer in self.tracers:
            tracer(tree)

class Do(Browser):
    """
    Main class to call in passing in argument the parser
    and a browser class.
    Ugly name I know but called like that for historical reasons
    """

    def __init__(self, parser, browser=None, topic=None, other_topic=None, execute=False, plot=False,
                 manglename_pattern='%(FIELD)s_%(COMMAND)s_%(SCHEMA)s_S%(POPSIZE)d_C%(CORESIZE)d',
                 timefilename_pattern='%(TIMEDIR)s/%(NAME)s_%(MANGLENAME)s.time.%(NUM)s',
                 resfilename_pattern='%(RESDIR)s/%(NAME)s_%(MANGLENAME)s.out.%(NUM)s',
                 planfilename_pattern='%(RESDIR)s/%(NAME)s_%(MANGLENAME)s.soln.%(NUM)s',
                 command_pattern=\
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
                 description='No description\n'):

        Browser.__init__(self, parser, browser)

        self.datename = str(datetime.today())
        for char in [' ', ':', '-', '.']: self.datename = self.datename.replace(char, '_')

        parser.add_option('-t', '--topic', default=topic if topic else self.datename, help='give here a topic name used to create the folder')
        parser.add_option('-O', '--other_topic', default=other_topic, help='give here another topic name used to compare with the current one')

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
        if not options.topic:
            raise ValueError('option --topic (-t) is missing')

        def makedirs(dirname):
            try:
                os.makedirs(dirname)
            except OSError:
                pass

        tree['TOPIC'] = options.topic
        tree['OTHER_TOPIC'] = options.other_topic
        tree['DATENAME'] = self.datename

        tree['RESDIR'] = '%(TOPIC)s/Res' % tree
        tree['TIMEDIR'] = '%(TOPIC)s/Time' % tree
        tree['MAKEXPDIR'] = '%(TOPIC)s/makexp_%(DATENAME)s' % tree
        tree['GRAPHDIR'] = '%(TOPIC)s/graph_%(DATENAME)s' % tree

        if options.other_topic:
            tree['OTHER_RESDIR'] = '%(OTHER_TOPIC)s/Res' % tree
            tree['OTHER_TIMEDIR'] = '%(OTHER_TOPIC)s/Time' % tree
            tree['OTHER_MAKEXPDIR'] = '%(OTHER_TOPIC)s/makexp_%(DATENAME)s' % tree
            tree['OTHER_GRAPHDIR'] = '%(OTHER_TOPIC)s/graph_%(DATENAME)s' % tree

        # create needed directories
        if options.execute:
            for key in ['RESDIR', 'TIMEDIR', 'MAKEXPDIR']: makedirs(tree[key])
            dirname = os.path.dirname(sys.argv[0])
            script = os.path.basename(sys.argv[0])
            for f in [script, 'browsers.py', 'common.py', 'stats.py', 'tracers.py']:
                shutil.copy2("%s/%s" % (dirname, f), "%(MAKEXPDIR)s/" % tree)

            open('%(TOPIC)s/COMMAND' % tree, 'w').write("%s\n" % ' '.join(sys.argv))
            open('%(TOPIC)s/README' % tree, 'w').write(options.description)

        if not os.path.isdir(tree['TOPIC']):
            self.logger.error('the topic (directory) %(TOPIC)s doesnot exist.' % tree)
            return

        if options.plot: makedirs(tree["GRAPHDIR"])

        self.browseAll(tree)

class VariablesOnDo(Browser):
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
                'TIMEFILENAME_PATTERN': '%(TIMEDIR)s/%(NAME)s_%(MANGLENAME)s.time.%(NUM)s',
                'RESFILENAME_PATTERN': '%(RESDIR)s/%(NAME)s_%(MANGLENAME)s.out.%(NUM)s',
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

class VariablesOnSample(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        for tree['NAME'], tree['DOMAIN'], tree['INSTANCE'] in tree['SAMPLES']:
            self.browseAll(tree)

class Sample(VariablesOnSample):
    def __init__(self, parser, samples, browser=None):
        VariablesOnSample.__init__(self, parser, browser)
        self.samples = samples

    def browse(self, options, tree):
        tree['SAMPLES'] = self.samples
        VariablesOnSample.browse(self, options, tree)

class VariablesOnPop(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        for tree['POPSIZE'] in tree['POPSIZES']:
            self.browseAll(tree)

class Pop(VariablesOnPop):
    def __init__(self, parser, popsizes, browser=None):
        VariablesOnPop.__init__(self, parser, browser)
        self.popsizes = popsizes

    def browse(self, options, tree):
        tree['POPSIZES'] = self.popsizes
        VariablesOnPop.browse(self, options, tree)

class VariablesOnCore(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        for tree['CORESIZE'] in tree['CORESIZES']:
            self.browseAll(tree)

class Core(VariablesOnCore):
    def __init__(self, parser, coresizes, browser=None, parallelize=True):
        VariablesOnCore.__init__(self, parser, browser)

        parser.add_option('-L', '--parallelize', action='store_true', default=parallelize, help='with parallelization')

        self.coresizes = coresizes

    def browse(self, options, tree):
        tree['PARALLELIZE'] = options.parallelize
        tree['CORESIZES'] = self.coresizes
        VariablesOnCore.browse(self, options, tree)

class VariablesOnSequential(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        tree['CORESIZE'] = 1
        tree['PARALLELIZE'] = False

        self.browseAll(tree)

class Sequential(VariablesOnSequential):
    def __init__(self, parser, browser=None):
        VariablesOnSequential.__init__(self, parser, browser)

    def browse(self, options, tree):
        VariablesOnSequential.browse(self, options, tree)

class VariablesOnRestart(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        tree['FIELD'] = 'RESTART' if tree['RESTART'] else ''
        tree['RUNMAX'] = 0 if tree['RESTART'] else 1

        self.browseAll(tree)

class Restart(VariablesOnRestart):
    def __init__(self, parser, browser=None, restart=False):
        VariablesOnRestart.__init__(self, parser, browser)

        parser.add_option('-R', '--restart', action='store_true', default=restart, help='with restarts')

    def browse(self, options, tree):
        tree['RESTART'] = options.restart
        VariablesOnRestart.browse(self, options, tree)

class VariablesOnStarting(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        for tree['FIELD'], tree['RUNMAX'] in [('', 1), ('RESTART', 0)]:
            self.browseAll(tree)

class Starting(VariablesOnStarting):
    def __init__(self, parser, browser=None):
        VariablesOnStarting.__init__(self, parser, browser)

    def browse(self, options, tree):
        VariablesOnStarting.browse(self, options, browser)

class VariablesOnDynamic(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        tree['SCHEMA'] = 'DYNAMIC' if tree['DYNAMIC'] else 'STATIC'
        tree['SCHEMABOOL'] = tree['DYNAMIC']

        self.browseAll(tree)

class Dynamic(VariablesOnDynamic):
    def __init__(self, parser, browser=None, dynamic=False):
        VariablesOnDynamic.__init__(self, parser, browser)

        parser.add_option('-D', '--dynamic', action='store_true', default=dynamic, help='use the dynamic scheduler in openmp')

    def browse(self, options, tree):
        tree['DYNAMIC'] = options.dynamic
        VariablesOnDynamic.browse(self, options, tree)

class VariablesOnSchema(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        for tree['SCHEMA'], tree['SCHEMABOOL'] in [('STATIC', 0), ('DYNAMIC', 1)]:
            self.browseAll(tree)

class Schema(VariablesOnSchema):
    def __init__(self, parser, browser=None):
        VariablesOnSchema.__init__(self, parser, browser)

    def browse(self, options, tree):
        VariablesOnSchema.browse(self, options, tree)

class VariablesOnCommand(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        for tree['COMMAND'] in tree['BINARIES']:
            if tree['EXECUTE']:
                shutil.copy2('%(BINARYPATH)s/%(COMMAND)s' % tree, '%(MAKEXPDIR)s/' % tree)

            self.browseAll(tree)

class Command(VariablesOnCommand):
    def __init__(self, parser, commands, browser=None, binarypath='.'):
        VariablesOnCommand.__init__(self, parser, browser)

        parser.add_option('-B', '--binarypath', default=binarypath, help='give here binaries\' path')

        self.commands = commands

    def browse(self, options, tree):
        tree['BINARYPATH'] = options.binarypath
        tree['BINARIES'] = self.commands
        VariablesOnCommand.browse(self, options, tree)

class VariablesOnRange(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        for tree['NUM'] in xrange(1, tree['NRUNS']+1):
            self.browseAll(tree)

class Range(VariablesOnRange):
    def __init__(self, parser, browser=None, nruns=1):
        VariablesOnRange.__init__(self, parser, browser)

        parser.add_option('-N', '--nruns', type='int', default=nruns, help='give here a number of runs')

    def browse(self, options, tree):
        tree['NRUNS'] = options.nruns
        VariablesOnRange.browse(self, options, tree)

class VariablesOnExecute(Browser):
    def __init__(self, parser, stat=None):
        Browser.__init__(self, parser, stat=stat)

    def browse(self, options, tree):
        tree['MANGLENAME'] = '%(MANGLENAME_PATTERN)s' % tree % tree
        tree['TIME_FILENAME'] = '%(TIMEFILENAME_PATTERN)s' % tree % tree
        tree['RES_FILENAME'] = '%(RESFILENAME_PATTERN)s' % tree % tree
        tree['PLAN_FILENAME'] = '%(PLANFILENAME_PATTERN)s' % tree % tree
        tree['PROCESS_COMMAND'] = '%(COMMAND_PATTERN)s' % tree % tree

        self.logger.debug('%(PROCESS_COMMAND)s' % tree)

        if tree['EXECUTE']:
            p = subprocess.Popen('%(PROCESS_COMMAND)s' % tree, shell=True)
            p.wait()

class Execute(VariablesOnExecute):
    def __init__(self, parser, seed=0, runmax=0, gensteady=50, timelimit=1800, stat=None):
        VariablesOnExecute.__init__(self, parser, stat=stat)

        parser.add_option('-s', '--seed', type='int', default=seed, help='with seed fixed, seed=0 means seed defined randomly')
        parser.add_option('-M', '--runmax', type='int', default=runmax, help='with runmax fixed, runmax=0 means no limit')
        parser.add_option('-G', '--gensteady', type='int', default=gensteady, help='with gensteady fixed')
        parser.add_option('-T', '--timelimit', type='int', default=timelimit, help='with timelimit fixed')

    def browse(self, options, tree):
        tree['MANGLENAME_PATTERN'] = options.manglename_pattern
        tree['TIMEFILENAME_PATTERN'] = options.timefilename_pattern
        tree['RESFILENAME_PATTERN'] = options.resfilename_pattern
        tree['PLANFILENAME_PATTERN'] = options.planfilename_pattern
        tree['COMMAND_PATTERN'] = options.command_patten

        if options.runmax: tree['RUNMAX'] = options.runmax
        tree['SEED'] = options.seed
        tree['GENSTEADY'] = options.gensteady
        tree['TIMELIMIT'] = options.timelimit
        tree['EXECUTE'] = options.execute

        VariablesOnExecute.browse(self, options, tree)

class Dummy(Browser):
    def __init__(self, parser):
        Browser.__init__(self, parser)

    def browse(self, options, tree): pass
