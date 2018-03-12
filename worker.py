import os
import re
import subprocess

from PyQt5 import QtCore

from dispatcher import Dispatcher


class EmittingStream(QtCore.QObject):
    text_written = QtCore.pyqtSignal(str)

    def write(self, text):
        self.text_written.emit(str(text))


class Worker(QtCore.QThread):
    def __init__(self, settings, parent=None):
        super(Worker, self).__init__(parent)
        self.exiting = False
        self.settings = settings
        self.dispatcher = Dispatcher.instance()

    def run_backup(self):
        self.start()

    def run(self):
        stream = subprocess.Popen(
            "rsnapshot -vvv -c %s weekly" %
            self.settings.value('rsnapshot_config_path'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True)

        # output, error = stream.communicate()
        while True:
            line = stream.stdout.readline(
            )  # .replace('\r', '').replace('\n', '')
            if line != '':
                print line.rstrip()
            else:
                break

        while True:
            line = stream.stderr.readline()
            if line != '':
                # the real code does filtering here
                if re.search(r'rsnapshot refuses to create snapshot_root',
                             line) is not None:
                    self.dispatcher.error.emit('error-cannot-find-dest')
                print line.rstrip()
            else:
                break

        while True:
            poll = stream.poll()
            if poll is not None:
                self.dispatcher.command_complete.emit(stream.returncode)
                break
