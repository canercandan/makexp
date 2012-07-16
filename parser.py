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
How to use the program parsing and logging features ?

(1) Add at the header of your program the following lines:

import parser as p, logging

(2) Define a logging context:

logger = logging.getLogger("YOUR_PROGRAM")

(3) Define the options parser:

parser = p.Parser()
options = parser()

(3bis) You can also define your own options:

parser = p.Parser()
parser.add_option('-f', '--filename', help='give a filename')
options = parser()
"""

import optparse, logging, sys

class Parser(optparse.OptionParser):
    def __init__(self):
        optparse.OptionParser.__init__(self)

        self.levels = {'debug': logging.DEBUG,
                       'info': logging.INFO,
                       'warning': logging.WARNING,
                       'error': logging.ERROR,
                       'critical': logging.CRITICAL
                       }

        self.add_option('-v', '--verbose', choices=[x for x in self.levels.keys()], default='info', help='set a verbose level, default: info')
        self.add_option('-l', '--levels', action='store_true', default=False, help='list verbose levels')
        self.add_option('-o', '--output', help='give an output filename for logging', default='')

    def _logging_config(self, level_name, filename=''):
        if (filename != ''):
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                filename=filename, filemode='a'
                )
            return

        logging.basicConfig(
            level=self.levels.get(level_name, logging.NOTSET),
            format='%(name)-12s: %(levelname)-8s %(message)s'
            )

    def _list_verbose_levels(self):
        print("Here's the verbose levels available:")
        for keys in self.levels.keys():
            print("\t", keys)
        sys.exit()

    def __call__(self):
        options, args = self.parse_args()
        if options.levels: self._list_verbose_levels()
        self._logging_config(options.verbose, options.output)
        return options
