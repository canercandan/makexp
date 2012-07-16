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

import logging

from collections import UserDict
class AutoFillingDict(UserDict):
    """
    Another kind of dictionnary inheriting from UserDict and returning an empty string whether a key is not found.
    Thanks to David Mertz.
    """

    def __init__(self, dict={}):
        UserDict.__init__(self, dict)

    def __getitem__(self, key):
        return self.data.get(key, '')
        #return UserDict.get(self, key, '')

class Base:
    """
    This is the base for all classes.
    """

    def __init__(self, parser):
        self.parser = parser

        name = str(str(self).split('.')[1].split()[0])
        self.logger = logging.getLogger(name)

    def __call__(self, tree = AutoFillingDict()):
        self.logger.debug('begins')
        options, args = self.parser.parse_args()
        if options.topic: self.callit(options, tree.copy())
        self.logger.debug('ends')
