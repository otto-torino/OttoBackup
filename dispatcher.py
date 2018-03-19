from PyQt5 import QtCore

from singleton import Singleton


@Singleton
class Dispatcher(QtCore.QObject):
    error = QtCore.pyqtSignal(str, name='commandError')
    command_complete = QtCore.pyqtSignal(int, name='commandComplete')
    rsnapshot_firstset = QtCore.pyqtSignal(
        name='rsnapshotConfPathFirstSet')
