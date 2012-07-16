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
