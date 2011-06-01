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
                 manglename_pattern="%(FIELD)s_%(COMMAND)s_%(SCHEMA)s_S%(POPSIZE)d_C%(CORESIZE)d",
                 timefilename_pattern="%(TIMEDIR)s/%(NAME)s_%(MANGLENAME)s.time.%(NUM)s",
                 resfilename_pattern="%(RESDIR)s/%(NAME)s_%(MANGLENAME)s.out.%(NUM)s",
                 planfilename_pattern="%(RESDIR)s/%(NAME)s_%(MANGLENAME)s.soln.%(NUM)s",
                 command_pattern=\
                     "/usr/bin/time -v -o %(TIME_FILENAME)s "\
                     "timelimit -t %(TIMELIMIT)d "\
                     "%(MAKEXPDIR)s/%(COMMAND)s "\
                     "--seed=%(SEED)d "\
                     "--domain=%(DOMAIN)s "\
                     "--instance=%(INSTANCE)s "\
                     "--plan-file=%(PLAN_FILENAME)s "\
                     "--runs-max=%(RUNMAX)d "\
                     "--popSize=%(POPSIZE)d "\
                     "--gen-steady=%(GENSTEADY)d "\
                     "--parallelize-loop=%(PARALLELIZE)d "\
                     "--parallelize-nthreads=%(CORESIZE)d "\
                     "--parallelize-dynamic=%(SCHEMABOOL)d "\
                     "> %(RES_FILENAME)s",
                 description="No description\n"):

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

        def makedirs(dirname):
            try:
                os.makedirs(dirname)
            except OSError:
                pass

        tree["TOPIC"] = options.topic
        tree["OTHER_TOPIC"] = options.other_topic
        tree["DATENAME"] = self.datename

        tree["RESDIR"] = "%(TOPIC)s/Res" % tree
        tree["TIMEDIR"] = "%(TOPIC)s/Time" % tree
        tree["MAKEXPDIR"] = "%(TOPIC)s/makexp_%(DATENAME)s" % tree
        tree["GRAPHDIR"] = "%(TOPIC)s/graph_%(DATENAME)s" % tree

        if options.other_topic:
            tree["OTHER_RESDIR"] = "%(OTHER_TOPIC)s/Res" % tree
            tree["OTHER_TIMEDIR"] = "%(OTHER_TOPIC)s/Time" % tree
            tree["OTHER_MAKEXPDIR"] = "%(OTHER_TOPIC)s/makexp_%(DATENAME)s" % tree
            tree["OTHER_GRAPHDIR"] = "%(OTHER_TOPIC)s/graph_%(DATENAME)s" % tree

        # create needed directories
        if options.execute:
            for key in ["RESDIR", "TIMEDIR", "MAKEXPDIR"]: makedirs(tree[key])
            dirname = os.path.dirname(sys.argv[0])
            script = os.path.basename(sys.argv[0])
            for f in [script, 'browsers.py', 'common.py', 'stats.py', 'tracers.py']:
                shutil.copy2("%s/%s" % (dirname, f), "%(MAKEXPDIR)s/" % tree)

            open('%(TOPIC)s/COMMAND' % tree, 'w').write("%s\n" % ' '.join(sys.argv))
            open('%(TOPIC)s/README' % tree, 'w').write(options.description)

        if not os.path.isdir(tree["TOPIC"]):
            self.logger.error('the topic (directory) %(TOPIC)s doesnot exist.' % tree)
            return

        if options.plot: makedirs(tree["GRAPHDIR"])

        self.browseAll(tree)

class Sample(Browser):
    def __init__(self, parser, samples, browser=None):
        Browser.__init__(self, parser, browser)
        self.samples = samples

    def browse(self, options, tree):
        for name, domain, instance in self.samples:
            tree["NAME"] = name
            tree["DOMAIN"] = domain
            tree["INSTANCE"] = instance

            self.browseAll(tree)

class Pop(Browser):
    def __init__(self, parser, popsizes, browser=None):
        Browser.__init__(self, parser, browser)
        self.popsizes = popsizes

    def browse(self, options, tree):
        tree['POPSIZES'] = self.popsizes
        for size in self.popsizes:
            tree["POPSIZE"] = size

            self.browseAll(tree)

class Core(Browser):
    def __init__(self, parser, coresizes, browser=None, parallelize=True):
        Browser.__init__(self, parser, browser)

        parser.add_option('-L', '--parallelize', action='store_true', default=parallelize, help='with parallelization')

        self.coresizes = coresizes

    def browse(self, options, tree):
        tree['CORESIZES'] = self.coresizes
        for size in self.coresizes:
            tree["CORESIZE"] = size
            tree["PARALLELIZE"] = options.parallelize

            self.browseAll(tree)

class Sequential(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        tree["CORESIZE"] = 1
        tree["PARALLELIZE"] = False

        self.browseAll(tree)

class Restart(Browser):
    def __init__(self, parser, browser=None, restart=False):
        Browser.__init__(self, parser, browser)

        parser.add_option('-R', '--restart', action='store_true', default=restart, help='with restarts')

    def browse(self, options, tree):
        tree["FIELD"] = "RESTART" if options.restart else ""
        tree["RUNMAX"] = 0 if options.restart else 1

        self.browseAll(tree)

class Starting(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        for field in ["", "RESTART"]:
            tree["FIELD"] = field
            tree["RUNMAX"] = 0 if field == "RESTART" else 1

            self.browseAll(tree)

class Dynamic(Browser):
    def __init__(self, parser, browser=None, dynamic=False):
        Browser.__init__(self, parser, browser)

        parser.add_option('-D', '--dynamic', action='store_true', default=dynamic, help='use the dynamic scheduler in openmp')

    def browse(self, options, tree):
        tree["SCHEMA"] = "DYNAMIC" if options.dynamic else "STATIC"
        tree["SCHEMABOOL"] = options.dynamic

        self.browseAll(tree)

class Schema(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        for schema in ["STATIC", "DYNAMIC"]:
            tree["SCHEMA"] = schema
            tree["SCHEMABOOL"] = 1 if schema == "DYNAMIC" else 0

            self.browseAll(tree)

class Command(Browser):
    def __init__(self, parser, commands, browser=None, binarypath='.'):
        Browser.__init__(self, parser, browser)

        parser.add_option('-B', '--binarypath', default=binarypath, help='give here binaries\' path')

        self.commands = commands

    def browse(self, options, tree):
        tree["BINARYPATH"] = options.binarypath

        for command in self.commands:
            tree["COMMAND"] = command

            if options.execute:
                shutil.copy2("%(BINARYPATH)s/%(COMMAND)s" % tree, "%(MAKEXPDIR)s/" % tree)

            self.browseAll(tree)

class Range(Browser):
    def __init__(self, parser, browser=None, nruns=1):
        Browser.__init__(self, parser, browser)

        parser.add_option('-N', '--nruns', type='int', default=nruns, help='give here a number of runs')

    def browse(self, options, tree):
        for num in xrange(1, options.nruns+1):
            tree["NUM"] = num

            self.browseAll(tree)

class Execute(Browser):
    def __init__(self, parser, seed=0, runmax=0, gensteady=50, timelimit=1800, stat=None):
        Browser.__init__(self, parser, stat=stat)

        parser.add_option('-s', '--seed', type='int', default=seed, help='with seed fixed, seed=0 means seed defined randomly')
        parser.add_option('-M', '--runmax', type='int', default=runmax, help='with runmax fixed, runmax=0 means no limit')
        parser.add_option('-G', '--gensteady', type='int', default=gensteady, help='with gensteady fixed')
        parser.add_option('-T', '--timelimit', type='int', default=timelimit, help='with timelimit fixed')

    def browse(self, options, tree):
        tree["MANGLENAME"] = options.manglename_pattern % tree
        tree["TIME_FILENAME"] = options.timefilename_pattern % tree
        tree["RES_FILENAME"] = options.resfilename_pattern % tree
        tree["PLAN_FILENAME"] = options.planfilename_pattern % tree

        if options.runmax:
            tree["RUNMAX"] = options.runmax

        tree["SEED"] = options.seed
        tree["GENSTEADY"] = options.gensteady
        tree["TIMELIMIT"] = options.timelimit

        cmd = options.command_pattern % tree

        self.logger.debug(cmd)

        if options.execute:
            p = subprocess.Popen( cmd, shell=True )
            p.wait()

class Dummy(Browser):
    def __init__(self, parser):
        Browser.__init__(self, parser)

    def browse(self, options, tree): pass
