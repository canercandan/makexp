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
        cf. browser.add(browser1).add(browser2).add(browser3)...
        is equal to:
        - browser .add(browser1)
        - browser1.add(browser2)
        - browser2.add(browser3)
        """

        assert browser != None
        self.browsers.append(browser)
        return browser

    def addC(self, browser):
        """
        Useful if you want to link several calls to add method together but in using the same instance
        cf. browser.addC(browser1).addC(browser2).addC(browser3)...
        is equal to:
        - browser.add(browser1)
        - browser.add(browser2)
        - browser.add(browser3)
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

class Sample(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        tree['PROGRESSBAR_SIZE'] *= len(tree['SAMPLES'])

        for tree['INSTANCE'] in tree['SAMPLES']:
            self.browseAll(tree)

class Generation(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        tree['PROGRESSBAR_SIZE'] *= len(tree['GENERATIONS'])

        for tree['GENMAX'] in tree['GENERATIONS']:
            self.browseAll(tree)

class Pop(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        tree['PROGRESSBAR_SIZE'] *= len(tree['POPSIZES'])

        for tree['POPSIZE'] in tree['POPSIZES']:
            self.browseAll(tree)

class Core(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        tree['PROGRESSBAR_SIZE'] *= len(tree['CORESIZES']) * 2  # temporary patch, taking in account the sequential execution, has to be changed

        for tree['CORESIZE'] in tree['CORESIZES']:
            self.browseAll(tree)

class Sequential(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        tree['PROGRESSBAR_SIZE'] *= 2

        tree['CORESIZE'] = 1
        tree['PARALLELIZE'] = False

        self.browseAll(tree)

class Restart(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        tree['FIELD'] = 'RESTART' if tree['RESTART'] else ''
        tree['RUNMAX'] = 0 if tree['RESTART'] else 1
        # tree['TIMELIMIT_COMMAND'] = '%(TIMELIMIT_COMMAND_PATTERN)s' % tree % tree if tree['RESTART'] else ''
        tree['TIMEOUT_COMMAND'] = '%(TIMEOUT_COMMAND_PATTERN)s' % tree % tree if tree['RESTART'] else ''

        self.browseAll(tree)

class Starting(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        tree['PROGRESSBAR_SIZE'] *= 2

        # for tree['FIELD'], tree['RUNMAX'], tree['TIMELIMIT_COMMAND'] in [
        for tree['FIELD'], tree['RUNMAX'], tree['TIMEOUT_COMMAND'] in [
            ('', 1, ''),
            # ('RESTART', 0, '%(TIMELIMIT_COMMAND_PATTERN)s' % tree % tree)
            ('RESTART', 0, '%(TIMEOUT_COMMAND_PATTERN)s' % tree % tree)
            ]:
            self.browseAll(tree)

class Dynamic(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        tree['SCHEMA'] = 'DYNAMIC' if tree['DYNAMIC'] else 'STATIC'
        tree['SCHEMABOOL'] = tree['DYNAMIC']

        self.browseAll(tree)

class Schema(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        tree['PROGRESSBAR_SIZE'] *= 2

        for tree['SCHEMA'], tree['SCHEMABOOL'] in [('STATIC', 0), ('DYNAMIC', 1)]:
            self.browseAll(tree)

class Command(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        tree['PROGRESSBAR_SIZE'] *= len(tree['BINARIES'])

        for tree['COMMAND'] in tree['BINARIES']:
            if tree['EXECUTE']:
                shutil.copy('%(BINARYPATH)s/%(COMMAND)s' % tree, '%(MAKEXPDIR)s/' % tree)

            self.browseAll(tree)

class Range(Browser):
    def __init__(self, parser, browser=None):
        Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        tree['PROGRESSBAR_SIZE'] *= tree['NRUNS']

        for tree['NUM'] in range(1, tree['NRUNS']+1):
            self.browseAll(tree)

class Execute(Browser):
    def __init__(self, parser, stat=None):
        Browser.__init__(self, parser, stat=stat)

    def browse(self, options, tree):
        tree['MANGLENAME'] = '%(MANGLENAME_PATTERN)s' % tree % tree
        tree['TIME_FILENAME'] = '%(TIMEFILENAME_PATTERN)s' % tree % tree
        tree['RES_FILENAME'] = '%(RESFILENAME_PATTERN)s' % tree % tree
        tree['PROCESS_COMMAND'] = '%(COMMAND_PATTERN)s' % tree % tree

        self.logger.debug('%(PROCESS_COMMAND)s' % tree)

        if tree['EXECUTE']:
            p = subprocess.Popen('%(PROCESS_COMMAND)s' % tree, shell=True)
            p.wait()

        self.browseAll(tree)

class ProgressBar(Browser):
    def __init__(self, parser, stat=None):
        Browser.__init__(self, parser, stat=stat)

        self.pos = 0

    def browse(self, options, tree):
        self.pos += 1
        tree['PROGRESSBAR_POSITION'] = (float(self.pos) / float(tree['PROGRESSBAR_SIZE']) * 100) % 100
        tree['PROGRESSBAR_DONECHARS'] = '=' * int(int(tree['PROGRESSBAR_POSITION']) / 2)
        tree['PROGRESSBAR_TODOCHARS'] = ' ' * int((100 - int(tree['PROGRESSBAR_POSITION'])) / 2)
        tree['PROGRESSBAR_VISUAL'] = '%(PROGRESSBAR_DONECHARS)s%(PROGRESSBAR_TODOCHARS)s' % tree

        # print('\rMAKexp:\t%(PROGRESSBAR_VISUAL)s\t%(PROGRESSBAR_POSITION)d %%' % tree, end=' ')

        self.browseAll(tree)

class Dummy(Browser):
    def __init__(self, parser):
        Browser.__init__(self, parser)

    def browse(self, options, tree):
        self.browseAll(tree)
