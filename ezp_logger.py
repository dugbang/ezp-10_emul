import logging.handlers


class Ezp10Logging:
    def __init__(self):
        self.root_logger = logging.getLogger('ezp-10')
        file_handler = logging.handlers.RotatingFileHandler(filename='./log/ezp-10.log', encoding='utf-8',
                                                            maxBytes=1024 * 1024, backupCount=10)

        file_handler.setFormatter(logging.Formatter(fmt='[%(asctime)s] <%(name)s:%(levelname)s> '
                                                    '(%(filename)s:%(lineno)-3d:%(funcName)s) > %(message)s',
                                                    datefmt="%Y-%m-%d %H:%M:%S"))
        self.root_logger.addHandler(file_handler)

        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter(fmt='<%(name)s: %(levelname)s> '
                                               '(%(filename)s:%(lineno)-3d) > %(message)s',
                                               datefmt="%Y-%m-%d %H:%M:%S"))
        self.root_logger.addHandler(console)
        self.root_logger.setLevel(logging.DEBUG)

    def get_logger(self, child=''):
        if child == '':
            return self.root_logger
        else:
            return logging.getLogger('ezp-10.{}'.format(child))


class EzpLog:
    log = Ezp10Logging()
    pass

