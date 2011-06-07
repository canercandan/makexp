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
from datetime import datetime
import common

import os.path

DATE = str(datetime.today())

logger = logging.getLogger("make_experience")

parser = optparse.OptionParser()

parser.add_option('-n', '--name', default='EXP', help='give an experience name')

parser.add_option('-b', '--binary', default='', help='give the path to the binary to make an experience')

parser.add_option('-s', '--script', default='', help='give the path to the script to launch experiences')

topic = DATE
for char in [' ', ':', '-', '.']: topic = topic.replace(char, '_')
parser.add_option('-t', '--topic', default=topic, help='give here a topic name used to create the folder')

options = common.parser(parser)

if __name__ == '__main__':

    dirname = "%s-%s" % (options.topic, options.name)

    logger.info("Create experience directory %s ..." % dirname)

    os.mkdir(dirname)

    open('%s/README' % dirname, 'w').write("""\
NAME: %(name)s
DATE: %(date)s
PATH: %(dirname)s
""" % {'name': options.name,
       'date': DATE,
       'dirname': dirname})

    if options.binary:
        if os.path.exists(options.binary):
            os.system('cp %s %s/' % (options.binary, dirname))
            logger.info('The binary file %s has been copied.' % options.binary)
        else:
            logger.error('The binary file %s doesnot exist.' % options.binary)

    if options.script:
        if os.path.exists(options.script):
            os.system('cp %s %s/' % (options.script, dirname))
            logger.info('The script file %s has been copied.' % options.binary)
        else:
            logger.error('The script file %s doesnot exist.' % options.binary)

    logger.info("Directory created.")

    logger.info("You can go to the directory %(dirname)s to start your experiencies (cd %(dirname)s)" % {"dirname": dirname})
