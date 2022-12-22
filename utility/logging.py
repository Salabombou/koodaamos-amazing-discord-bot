import logging

file_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
terminal_handler = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')

file_handler.setFormatter(formatter)
terminal_handler.setFormatter(formatter)

handlers = [
   file_handler,
   terminal_handler
]