#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@TODO add hourly, daily, weekly settings! as combobox
"""

import sys

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QTextCursor, QMovie
from PyQt5.QtWidgets import (QAction, QApplication, QDesktopWidget,
                             QFileDialog, QLabel, QMainWindow, QMessageBox,
                             QTextEdit, QVBoxLayout, QWidget, )

from dialog_info import InfoDialog
from dialog_settings import SettingsDialog
from utils import icon
from worker import Worker, EmittingStream
from dispatcher import Dispatcher


class MainWindow(QMainWindow):
    def __init__(self, app):
        super(MainWindow, self).__init__()

        self.dispatcher = Dispatcher.instance()
        self.app = app
        self.settings = QtCore.QSettings('app', 'settings')
        self.worker = Worker(self.settings)
        self.busy = False

        # connect to events
        self.dispatcher.error.connect(self.command_error)
        self.dispatcher.command_complete.connect(self.command_complete)

        # Install the custom output stream
        sys.stdout = EmittingStream(text_written=self.log_command)

        self.init_ui()
        self.check_settings()

    def closeEvent(self, event):
        # do stuff
        if not self.busy:
            event.accept()
        else:
            event.ignore()
            QMessageBox.warning(
                self, 'Otto Backup',
                "Il programma sta ancora effettuando operazioni",
                QMessageBox.Ok)

    def init_ui(self):
        # styles
        sshFile = "style.qss"
        with open(sshFile, "r") as fh:
            self.setStyleSheet(fh.read())
        # dimensions and positioning
        self.resize(800, 400)
        self.center()
        # window props
        self.setWindowTitle('Otto Backup')
        self.setWindowIcon(QIcon(icon('icon.png')))
        # toolbar
        # settings
        settingsAct = QAction(QIcon(icon('settings-icon.png')), 'Exit', self)
        settingsAct.setShortcut('Ctrl+S')
        settingsAct.triggered.connect(self.open_settings_dialog)
        # info
        infoAct = QAction(QIcon(icon('info-icon.png')), 'Exit', self)
        infoAct.setShortcut('Ctrl+S')
        infoAct.triggered.connect(self.open_info_dialog)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(settingsAct)
        self.toolbar.addAction(infoAct)

        # layout
        self.wid = QWidget(self)
        self.setCentralWidget(self.wid)
        self.main_layout = QVBoxLayout()
        self.init_ui_body()
        self.main_layout.addStretch()
        self.wid.setLayout(self.main_layout)

        # show
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_ui_body(self):
        rsnapshot_config_path = self.settings.value('rsnapshot_config_path')
        if rsnapshot_config_path:
            self.text_info = QTextEdit()
            self.text_info.setReadOnly(True)
            self.text_info.setText('ready...')
            self.start_button = QLabel(
                '<img src="%s" />' % icon('backup-icon.png'))
            self.start_button.mousePressEvent = self.start_backup
            self.start_button.setAlignment(QtCore.Qt.AlignCenter)
            self.start_description = QLabel(
                '<p>Clicca il bottone per iniziare la sincronizzazione</p>')
            self.start_description.setAlignment(QtCore.Qt.AlignCenter)

            self.loading_movie = QMovie(icon('loader.gif'))
            self.loading = QLabel()
            self.loading.setAlignment(QtCore.Qt.AlignCenter)
            self.loading.setMovie(self.loading_movie)

            self.main_layout.addWidget(self.start_button)
            self.main_layout.addWidget(self.start_description)
            self.main_layout.addWidget(self.loading)
            self.main_layout.addWidget(self.text_info)

    def check_settings(self):
        data = self.settings.value('rsnapshot_config_path')

        if data is None:
            reply = QMessageBox.warning(
                self, 'Otto Backup',
                "Devi selezionare il file di configurazione per rsnapshot!",
                QMessageBox.Ok, QMessageBox.Abort)

            if reply == QMessageBox.Ok:
                self.choose_rsnapshot_config()
            else:
                sys.exit()
                return

    def choose_rsnapshot_config(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')

        if fname[0]:
            self.settings.setValue('rsnapshot_config_path', fname[0])

    def open_settings_dialog(self):
        settings_dialog = SettingsDialog(self.settings)
        settings_dialog.exec_()

    def open_info_dialog(self):
        info_dialog = InfoDialog()
        info_dialog.exec_()

    def start_backup(self, event):
        if not self.busy:
            self.set_busy(True)
            self.text_info.setText('starting rsnapshot backup...\n')
            self.worker.run_backup()

    def log_command(self, text):
        cursor = self.text_info.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.text_info.setTextCursor(cursor)
        self.text_info.ensureCursorVisible()

    def command_error(self, message):
        if message == 'error-cannot-find-dest':
            reply = QMessageBox.warning(
                self, 'Otto Backup',
                "Si è verificato un errore. Controlla di aver montato l'HD" +
                " in cui viene salvato il backup.",
                QMessageBox.Ok)
            if reply == QMessageBox.Ok:
                self.text_info.setText('ready...')

    def command_complete(self, returncode):
        if returncode == 0 or returncode == 2:
            reply = QMessageBox.information(
                self, 'Otto Backup',
                "Backup effettuato con successo.",
                QMessageBox.Ok)
            if reply == QMessageBox.Ok:
                self.text_info.setText('ready...')
        self.set_busy(False)

    def set_busy(self, busy):
        if busy:
            self.loading.show()
            self.loading_movie.start()
        else:
            self.loading.hide()
            self.loading_movie.stop()
        self.busy = busy


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow(app)
    sys.exit(app.exec_())
