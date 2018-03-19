import os
import re
import subprocess

from PyQt5 import QtCore

from dispatcher import Dispatcher


class EmittingStream(QtCore.QObject):
    text_written = QtCore.pyqtSignal(str)

    def write(self, text):
        self.text_written.emit(str(text))

    def flush(self):
        pass


class Worker(QtCore.QThread):
    def __init__(self, settings, parent=None):
        super(Worker, self).__init__(parent)
        self.exiting = False
        self.settings = settings
        self.dispatcher = Dispatcher.instance()

    def run_backup(self, interval):
        self.interval = interval
        self.start()

    def run(self):
        stream = subprocess.Popen(
            "%s -vvv -c %s %s" % (self.settings.value('rsnapshot_bin_path'),
                                  self.settings.value('rsnapshot_config_path'),
                                  self.interval),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            universal_newlines=True)

        # output, error = stream.communicate()
        while True:
            try:
                line = stream.stdout.readline(
                )  # .replace('\r', '').replace('\n', '')
                if line != '':
                    print(line.decode('utf-8').rstrip())
                else:
                    break
            except UnicodeDecodeError:
                print('unicode decode error')

        while True:
            try:
                line = stream.stderr.readline()
                if line != '':
                    # the real code does filtering here
                    if re.search(r'rsnapshot refuses to create snapshot_root',
                                 line) is not None:
                        self.dispatcher.error.emit('error-cannot-find-dest')
                    print(line.rstrip())
                else:
                    break
            except UnicodeDecodeError:
                print('unicode decode error')

        while True:
            poll = stream.poll()
            if poll is not None:
                self.dispatcher.command_complete.emit(stream.returncode)
                break
