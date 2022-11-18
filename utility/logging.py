import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

logger.addHandler(handler)

class StderrLogger(object):
    def __init__(self, logger: logging.Logger):
       self.logger = logger

    def write(self, buf: str):
       self.logger.exception(buf)

    def flush(self):
        pass