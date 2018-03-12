import os


def icon(name):
    app_dir = os.path.dirname(os.path.realpath(__file__))
    return app_dir + os.path.sep + 'assets' + os.path.sep + name
