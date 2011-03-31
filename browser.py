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

import optparse, logging, sys, os, subprocess
from datetime import datetime

class Browser:
    """
    Base class for Browser classes
    """

    def __init__(self, parser, browser=None):
        self.parser = parser
        self.browsers = []

        if browser:
            self.browsers.append(browser)

        name = str(str(self).split('.')[1].split()[0])
        self.logger = logging.getLogger(name)

    def __call__(self, tree = {}):
        self.logger.debug('begins')
        options, args = self.parser.parse_args()
        self.callit(options, tree.copy())
        self.logger.debug('ends')

    def add(self, browser):
        assert browser != None
        self.browsers.append(browser)
        return browser

    def addC(self, browser):
        assert browser != None
        self.browsers.append(browser)
        return self

    def browseAll(self, tree):
        for browser in self.browsers:
            browser(tree)

class DummyBrowser(Browser):
    def __init__(self, parser):
        Browser.__init__(self, parser)

    def callit(self, options, tree): pass

class ExecuteBrowser(Browser):
    def __init__(self, parser, seed=0, runmax=0, gensteady=50, timelimit=1800):
        Browser.__init__(self, parser)

        parser.add_option('-s', '--seed', type='int', default=seed, help='with seed fixed, seed=0 means seed defined randomly')
        parser.add_option('-M', '--runmax', type='int', default=runmax, help='with runmax fixed, runmax=0 means no limit')
        parser.add_option('-G', '--gensteady', type='int', default=gensteady, help='with gensteady fixed')
        parser.add_option('-T', '--timelimit', type='int', default=timelimit, help='with timelimit fixed')

    def callit(self, options, tree):
        if options.runmax:
            tree["RUNMAX"] = options.runmax

        tree["SEED"] = options.seed
        tree["GENSTEADY"] = options.gensteady
        tree["TIMELIMIT"] = options.timelimit
        tree["BINARYPATH"] = options.binarypath

        cmd = \
            "/usr/bin/time -v -o %(TIME_FILENAME)s "\
            "timelimit -t %(TIMELIMIT)d "\
            "%(BINARYPATH)s/%(COMMAND)s "\
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
            "> %(RES_FILENAME)s" % tree

        self.logger.debug(cmd)

        if options.execute:
            open('%(TOPIC)s/COMMAND' % tree, 'w').write("%s\n" % ' '.join(sys.argv))

            p = subprocess.Popen( cmd, shell=True )
            p.wait()

class PopBrowser(Browser):
    def __init__(self, parser, popsizes, browser=None):
        Browser.__init__(self, parser, browser)
        self.popsizes = popsizes

    def callit(self, options, tree):
        for size in self.popsizes:
            tree["POPSIZE"] = size

            self.browseAll(tree)

class CoreBrowser(Browser):
    def __init__(self, parser, coresizes, browser=None, parallelize=True):
        Browser.__init__(self, parser, browser)

        parser.add_option('-L', '--parallelize', action='store_true', default=parallelize, help='with parallelization')

        self.coresizes = coresizes

    def callit(self, options, tree):
        for size in self.coresizes:
            tree["CORESIZE"] = size
            tree["PARALLELIZE"] = options.parallelize

            self.browseAll(tree)

class SequentialBrowser(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def callit(self, options, tree):
        tree["CORESIZE"] = 1
        tree["PARALLELIZE"] = False

        self.browseAll(tree)

class MangleBrowser(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def callit(self, options, tree):
        tree["MANGLENAME"] = "%(FIELD)s_%(COMMAND)s_%(SCHEMA)s_S%(POPSIZE)d_C%(CORESIZE)d" % tree
        tree["TIME_FILENAME"] = "%(TIMEDIR)s/%(NAME)s_%(MANGLENAME)s.time.%(NUM)s" % tree
        tree["RES_FILENAME"] = "%(RESDIR)s/%(NAME)s_%(MANGLENAME)s.out.%(NUM)s" % tree
        tree["PLAN_FILENAME"] = "%(RESDIR)s/%(NAME)s_%(MANGLENAME)s.soln.%(NUM)s" % tree

        self.browseAll(tree)

class RestartBrowser(Browser):
    def __init__(self, parser, browser=None, restart=False):
        Browser.__init__(self, parser, browser)

        parser.add_option('-R', '--restart', action='store_true', default=restart, help='with restarts')

    def callit(self, options, tree):
        tree["FIELD"] = "RESTART" if options.restart else ""
        tree["RUNMAX"] = 0 if options.restart else 1

        self.browseAll(tree)

class StartingBrowser(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def callit(self, options, tree):
        for field in ["", "RESTART"]:
            tree["FIELD"] = field
            tree["RUNMAX"] = 0 if field == "RESTART" else 1

            self.browseAll(tree)

class DynamicBrowser(Browser):
    def __init__(self, parser, browser=None, dynamic=False):
        Browser.__init__(self, parser, browser)

        parser.add_option('-D', '--dynamic', action='store_true', default=dynamic, help='use the dynamic scheduler in openmp')

    def callit(self, options, tree):
        tree["SCHEMA"] = "DYNAMIC" if options.dynamic else "STATIC"
        tree["SCHEMABOOL"] = options.dynamic

        self.browseAll(tree)

class SchemaBrowser(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def callit(self, options, tree):
        for schema in ["STATIC", "DYNAMIC"]:
            tree["SCHEMA"] = schema
            tree["SCHEMABOOL"] = 1 if schema == "DYNAMIC" else 0

            self.browseAll(tree)

class RangeBrowser(Browser):
    def __init__(self, parser, browser=None, nruns=1):
        Browser.__init__(self, parser, browser)

        parser.add_option('-N', '--nruns', type='int', default=nruns, help='give here a number of runs')

    def callit(self, options, tree):
        for num in range(1, options.nruns+1):
            tree["NUM"] = num

            self.browseAll(tree)

class CommandBrowser(Browser):
    def __init__(self, parser, commands, browser=None, binarypath='.'):
        Browser.__init__(self, parser, browser)

        parser.add_option('-B', '--binarypath', default=binarypath, help='give here binaries\' path')

        self.commands = commands

    def callit(self, options, tree):
        for command in self.commands:
            tree["COMMAND"] = command

            self.browseAll(tree)

class SampleBrowser(Browser):
    def __init__(self, parser, samples, browser=None):
        Browser.__init__(self, parser, browser)
        self.samples = samples

    def callit(self, options, tree):
        for name, domain, instance in self.samples:
            tree["NAME"] = name
            tree["DOMAIN"] = domain
            tree["INSTANCE"] = instance

            self.browseAll(tree)

class Do(Browser):
    """
    Main class to call in passing in argument the parser
    and a browser class.
    Ugly name I know but called like that for historical reasons
    """

    def __init__(self, parser, browser=None, topic=str(datetime.today()), execute=False):
        Browser.__init__(self, parser, browser)

        for char in [' ', ':', '-', '.']: topic = topic.replace(char, '_')
        parser.add_option('-t', '--topic', default=topic, help='give here a topic name used to create the folder')

        parser.add_option('-e', '--execute', action='store_true', default=execute, help='execute experiences')

    def callit(self, options, tree):
        resdir = "%s/Res" % options.topic
        timedir = "%s/Time" % options.topic

        # create needed directories
        if options.execute:
            for d in [resdir, timedir]:
                try:
                    os.makedirs(d)
                except OSError:
                    pass

        tree["TOPIC"] = options.topic
        tree["RESDIR"] = resdir
        tree["TIMEDIR"] = timedir

        self.browseAll(tree)