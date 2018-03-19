import os
import sys

if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))


def icon(name):
    return bundle_dir + os.path.sep + 'assets' + os.path.sep + name


def style():
    return bundle_dir + os.path.sep + 'style.qss'
