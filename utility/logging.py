import logging

file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

terminal_handler = logging.StreamHandler()

file_handler.setLevel(logging.INFO)
terminal_handler.setLevel(logging.CRITICAL)
