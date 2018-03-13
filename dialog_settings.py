import os

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QComboBox, QDialog, QFileDialog, QGridLayout,
                             QLabel, QPushButton, QVBoxLayout)

from utils import icon


class SettingsDialog(QDialog):
    def __init__(self, settings):
        super(SettingsDialog, self).__init__()
        self.translate = QtCore.QCoreApplication.translate
        self.settings = settings
        self.init_ui()

    def init_ui(self):
        # styles
        sshFile = "style.qss"
        with open(sshFile, "r") as fh:
            self.setStyleSheet(fh.read())
        # dimensions and positioning
        self.resize(500, 300)
        # window props
        self.setObjectName("Settings")
        self.setWindowTitle(self.translate('SettingsDialog', 'Settings'))

        main_layout = QVBoxLayout()

        # rsnapshot configuration
        r_conf_title = QLabel('rsnapshot')
        r_conf_title.setProperty('labelClass', 'settingsTitle')
        # rsnapshot configuration path
        r_conf_label = QLabel(
            self.translate('SettingsDialog', 'rsnapshot configuration file'))
        r_conf_label.setProperty('labelClass', 'settingsLabel')
        self.r_conf_value = QLabel(
            self.settings.value('rsnapshot_config_path'))
        self.r_conf_value.setProperty('labelClass', 'settingsValue')
        r_conf_edit = QPushButton(QIcon(icon('edit-icon.png')), '')
        r_conf_edit.clicked.connect(self.choose_rsnapshot_config)
        # rsnapshot first interval
        r_first_interval_label = QLabel(
            self.translate('SettingsDialog', 'first backup interval'))
        r_first_interval_label.setProperty('labelClass', 'settingsLabel')
        items = ['', 'daily', 'weekly', 'monthly']
        r_first_interval_value = QComboBox(self)
        r_first_interval_value.addItems(items)
        r_first_interval_value.setProperty('labelClass', 'settingsValue')
        r_first_interval_value.setCurrentIndex(
            items.index(self.settings.value('rsnapshot_first_interval') or ''))
        # onchange
        r_first_interval_value.activated[str].connect(
            self.on_select_first_interval)

        grid = QGridLayout()

        grid.addWidget(r_conf_title, 1, 0)
        grid.addWidget(r_conf_label, 2, 0)
        grid.addWidget(self.r_conf_value, 2, 1)
        grid.addWidget(r_conf_edit, 2, 2)
        grid.addWidget(r_first_interval_label, 3, 0)
        grid.addWidget(r_first_interval_value, 3, 1)

        main_layout.addLayout(grid)
        main_layout.addStretch()

        self.setLayout(main_layout)

        self.show()

    def choose_rsnapshot_config(self):
        fname = QFileDialog.getOpenFileName(self,
                                            self.translate(
                                                'SettingsDialog', 'Open file'),
                                            os.path.expanduser('~'))

        if fname[0]:
            self.settings.setValue('rsnapshot_config_path', fname[0])
            self.refresh()

    def on_select_first_interval(self, text):
        self.settings.setValue('rsnapshot_first_interval', text)

    def refresh(self):
        self.r_conf_value.setText(self.settings.value('rsnapshot_config_path'))
