import logging

__file_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
__terminal_handler = logging.StreamHandler()

__formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')

__file_handler.setFormatter(__formatter)
__terminal_handler.setFormatter(__formatter)

__file_handler.setLevel(logging.INFO)
__terminal_handler.setLevel(logging.ERROR)

handlers = [
   __file_handler,
   __terminal_handler
]