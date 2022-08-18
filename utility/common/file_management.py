import os

def delete_temps(*args):
    for temp in args:
        if os.path.exists(temp):
            os.remove(temp)