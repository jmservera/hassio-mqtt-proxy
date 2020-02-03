import os

def getFixturePath(filename):
    return os.path.join(os.path.dirname(__file__), "fixtures", filename)