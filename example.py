#!/usr/bin/env python

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

import optparse, logging, sys, os
import common
from browser import *
from stat import *

logger = logging.getLogger("example")

def main():

    parser = optparse.OptionParser()

    do = Do(parser, execute=True)
    cmd = CommandBrowser(parser, ['ls'], binarypath='/bin')
    rang = RangeBrowser(parser, nruns=11)
    schema = DynamicBrowser(parser)
    sample = SampleBrowser(parser, [("PROBLEM1", "domain1", "instance1")])
    core = SequentialBrowser(parser)
    pop = PopBrowser(parser, [1, 2, 4, 8, 16, 32, 64, 128])
    mangle = MangleBrowser(parser)
    execute = ExecuteBrowser(parser, seed=1)
    start = RestartBrowser(parser, restart=True)

    common.parser(parser)

    do\
        .add(sample)\
        .add(rang)\
        .add(cmd)\
        .add(schema)\
        .add(core)\
        .add(pop)\
        .add(start)\
        .add(mangle)\
        .add(execute)

    do()

# when executed, just run main():
if __name__ == '__main__':
    logger.debug('### script started ###')
    main()
    logger.debug('### script ended ###')
