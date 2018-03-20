#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Otto Backup
MIT License
@author abidibo <abidibo@gmail.com>
Company Otto srl <https://www.otto.to.it>
"""

import datetime
import os
import sys

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QMovie, QTextCursor
from PyQt5.QtWidgets import (QAction, QApplication, QComboBox, QDesktopWidget,
                             QFileDialog, QLabel, QMainWindow, QMenu,
                             QMessageBox, QSystemTrayIcon, QTextEdit,
                             QVBoxLayout, QWidget, qApp)

from data import ApplicationData
from dialog_info import InfoDialog
from dialog_settings import SettingsDialog
from dispatcher import Dispatcher
from utils import icon, style, bundle_dir
from worker import EmittingStream, Worker


class MainWindow(QMainWindow):
    """ Main Application Window"""

    def __init__(self, application_data):
        super(MainWindow, self).__init__()
        # event dispatcher
        self.dispatcher = Dispatcher.instance()
        # translations
        self.translate = QtCore.QCoreApplication.translate
        # appication data
        self.application_data = application_data
        self.interval = 'daily'
        # application settings
        self.settings = QtCore.QSettings('OttoBackup', 'settings')
        # thread which runs rsnapshot
        self.worker = Worker(self.settings)
        # is rsnapshot still running?
        self.busy = False

        # connect to events
        self.dispatcher.error.connect(self.command_error)
        self.dispatcher.command_complete.connect(self.command_complete)
        self.dispatcher.rsnapshot_firstset.connect(
            self.on_rsnapshot_firstset)

        # Install the custom output stream
        sys.stdout = EmittingStream(text_written=self.log_command)

        # init ui
        self.init_ui()
        # check required settings
        self.check_settings()

    def closeEvent(self, event):
        """ Do not close the app if rsnapshot is still running """
        if not self.busy:
            event.accept()
        else:
            event.ignore()
            QMessageBox.warning(
                self, 'Otto Backup',
                self.translate("MainWindow",
                               "The program is still performing operations"),
                QMessageBox.Ok)

    def init_ui(self):
        # styles
        ssh_file = style()
        with open(ssh_file, "r") as fh:
            self.setStyleSheet(fh.read())
        # dimensions and positioning
        self.resize(800, 500)
        self.center()
        # window props
        self.setWindowTitle('Otto Backup')
        self.setWindowIcon(QIcon(icon('icon.png')))
        # system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(icon('icon.png')))
        settings_action = QAction(
            self.translate('MainWindow', 'Settings'), self)
        settings_action.triggered.connect(self.open_settings_dialog)
        quit_action = QAction(self.translate('MainWindow', 'Quit'), self)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(settings_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        # settings
        settingsAct = QAction(QIcon(icon('settings-icon.png')), 'Exit', self)
        settingsAct.setShortcut('Ctrl+S')
        settingsAct.triggered.connect(self.open_settings_dialog)
        # info
        infoAct = QAction(QIcon(icon('info-icon.png')), 'Exit', self)
        infoAct.triggered.connect(self.open_info_dialog)
        # toolbar
        self.toolbar = self.addToolBar('Toolbar')
        self.toolbar.addAction(settingsAct)
        self.toolbar.addAction(infoAct)
        # layout
        self.wid = QWidget(self)
        self.setCentralWidget(self.wid)
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)
        self.init_ui_body()
        self.main_layout.addStretch()
        self.wid.setLayout(self.main_layout)
        # status bar
        self.last_sync_message()

        # show
        self.show()

    def center(self):
        """ Place the window in the center of the screen """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_ui_body(self):
        """ The ui body """
        rsnapshot_config_path = self.settings.value('rsnapshot_config_path')
        if rsnapshot_config_path:
            # text info (displays rsnapshot output)
            self.text_info = QTextEdit()
            self.text_info.setReadOnly(True)
            self.text_info.setText('ready...')
            # start button
            self.start_button = QLabel(
                '<img src="%s" />' % icon('backup-icon.png'))
            self.start_button.mousePressEvent = self.start_backup
            self.start_button.setFixedSize(128, 128)
            # select interval
            items = ['daily', 'weekly', 'monthly']
            self.select_interval = QComboBox(self)
            self.select_interval.addItems(items)
            self.select_interval.setCurrentIndex(0)
            self.select_interval.setFixedSize(140, 30)
            # onchange
            self.select_interval.activated[str].connect(
                self.on_change_interval)
            # noobs description
            self.start_description = QLabel(
                self.translate('MainWindow', '''<p>Select the backup type and
click the button to start syncing</p>'''))
            self.start_description.setAlignment(QtCore.Qt.AlignCenter)
            # loading icon
            self.loading_movie = QMovie(icon('loader.gif'))
            self.loading = QLabel()
            self.loading.setAlignment(QtCore.Qt.AlignCenter)
            self.loading.setMovie(self.loading_movie)
            self.loading.setHidden(True)

            # add all the stuff to the layout
            self.main_layout.addWidget(self.start_button)
            self.main_layout.addWidget(self.select_interval)
            self.main_layout.addWidget(self.start_description)
            self.main_layout.addWidget(self.loading)
            self.main_layout.addWidget(self.text_info)
            self.main_layout.setAlignment(self.start_button,
                                          QtCore.Qt.AlignCenter)
            self.main_layout.setAlignment(self.select_interval,
                                          QtCore.Qt.AlignCenter)

    def check_settings(self):
        """ rsnapshot conf file settings is required! """
        bin = self.settings.value('rsnapshot_bin_path')
        conf = self.settings.value('rsnapshot_config_path')

        if bin is None:
            reply = QMessageBox.warning(
                self, 'Otto Backup',
                self.translate('MainWindow', 'You must configure the rsnapshot bin path'),
                QMessageBox.Ok, QMessageBox.Abort)

            if reply == QMessageBox.Ok:
                self.choose_rsnapshot_bin()
            else:
                sys.exit()
                return

        if conf is None:
            reply = QMessageBox.warning(
                self, 'Otto Backup',
                self.translate('MainWindow', 'You must configure the rsnaphot configuration path'),
                QMessageBox.Ok, QMessageBox.Abort)

            if reply == QMessageBox.Ok:
                self.choose_rsnapshot_config()
            else:
                sys.exit()
                return

    def choose_rsnapshot_config(self):
        """ dialog to choose rsnapshot conf file """
        fname = QFileDialog.getOpenFileName(self,
                                            self.translate(
                                                'MainWindow', 'Open file'),
                                            os.path.expanduser('~'))

        if fname[0]:
            self.settings.setValue('rsnapshot_config_path', fname[0])
            if self.settings.value('rsnapshot_bin_path'):
                self.dispatcher.rsnapshot_firstset.emit()

    def choose_rsnapshot_bin(self):
        """ dialog to choose rsnapshot bin file """
        fname = QFileDialog.getOpenFileName(self,
                                            self.translate(
                                                'MainWindow', 'Open file'),
                                            os.path.expanduser('~'))

        if fname[0]:
            self.settings.setValue('rsnapshot_bin_path', fname[0])
            if self.settings.value('rsnapshot_conf_path'):
                self.dispatcher.rsnapshot_firstset.emit()

    def open_settings_dialog(self):
        """ opens the settings window """
        settings_dialog = SettingsDialog(self.settings)
        settings_dialog.exec_()

    def open_info_dialog(self):
        """ opens the info window """
        info_dialog = InfoDialog()
        info_dialog.exec_()

    def start_backup(self, event):
        """ Starts the backup if not yet busy """
        if not self.busy:
            self.set_busy(True)
            self.text_info.setText('starting rsnapshot backup...\n')
            self.worker.run_backup(self.interval)

    def log_command(self, text):
        """ Logs rsnapshot sys.stdout in the text field """
        cursor = self.text_info.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.text_info.setTextCursor(cursor)
        self.text_info.ensureCursorVisible()

    def command_error(self, message):
        """ Used to filter rsnapshot errors and perform actions or display
            info in some cases """
        if message == 'error-cannot-find-dest':
            reply = QMessageBox.warning(self, 'Otto Backup',
                                        self.translate('MainWindow',
                                                       '''An error occurred.
Check if the backup destination HD is mounted.'''), QMessageBox.Ok)
            if reply == QMessageBox.Ok:
                self.text_info.setText('ready...')

    def command_complete(self, returncode):
        """ rsnapshot command complete """
        self.set_busy(False)
        # success with or without warnings
        if returncode == 0 or returncode == 2:
            # save last sync
            if self.interval == self.settings.value(
                    'rsnapshot_first_interval'):
                application_data.store_las_sync(datetime.datetime.utcnow())
                self.last_sync_message()
            # show success dialog
            reply = QMessageBox.information(
                self, 'Otto Backup',
                self.translate('MainWindow',
                               'The backup was successfully executed'),
                QMessageBox.Ok)
            if reply == QMessageBox.Ok:
                self.text_info.setText('ready...')

    def set_busy(self, busy):
        """ Is the application busy? """
        if busy:
            self.select_interval.setDisabled(True)
            self.loading.setHidden(False)
            self.loading_movie.start()
        else:
            self.select_interval.setDisabled(False)
            self.loading.setHidden(True)
            self.loading_movie.stop()
        self.busy = busy

    def on_rsnapshot_firstset(self):
        """ When rsnapshot conf file is set the first time, the ui
            body must be redrawn """
        self.init_ui_body()

    def last_sync_message(self):
        """ Displays the last sync message in the status bar """
        last_sync = application_data.get_last_sync()
        if last_sync:
            self.statusBar().showMessage(
                self.translate('MainWindow',
                               'Last backup: %s' % str(last_sync)))

    def on_change_interval(self, text):
        """ When the rsnapshot interval is changed """
        self.interval = text


def setup():
    """ Init folder and files if necessary """
    application_data = ApplicationData()
    application_data.setup()
    return application_data


if __name__ == '__main__':
    app = QApplication(sys.argv)
    translator = QtCore.QTranslator(app)
    lc_path = os.path.join(
        bundle_dir, 'i18n',
        'ottobackup_%s.qm' % QtCore.QLocale.system().name()[:2])
    translator.load(lc_path)
    app.installTranslator(translator)
    application_data = setup()
    main_window = MainWindow(application_data)
    sys.exit(app.exec_())
