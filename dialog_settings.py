from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QDialog, QFileDialog, QGridLayout,
                             QLabel, QPushButton, QVBoxLayout)
from utils import icon


class SettingsDialog(QDialog):
    def __init__(self, settings):
        super(SettingsDialog, self).__init__()
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
        self.setWindowTitle('Settings')

        main_layout = QVBoxLayout()

        # rsnapshot path
        rsnapshot_conf_title = QLabel('rsnapshot')
        rsnapshot_conf_title.setProperty('labelClass', 'settingsTitle')
        rsnapshot_conf_label = QLabel('File di configurazione di rsnapshot')
        rsnapshot_conf_label.setProperty('labelClass', 'settingsLabel')
        self.rsnapshot_conf_value = QLabel(
            self.settings.value('rsnapshot_config_path'))
        self.rsnapshot_conf_value.setProperty('labelClass', 'settingsValue')
        rsnapshot_conf_edit = QPushButton(QIcon(icon('edit-icon.png')), '')
        rsnapshot_conf_edit.clicked.connect(self.choose_rsnapshot_config)

        grid = QGridLayout()

        grid.addWidget(rsnapshot_conf_title, 1, 0)
        grid.addWidget(rsnapshot_conf_label, 2, 0)
        grid.addWidget(self.rsnapshot_conf_value, 2, 1)
        grid.addWidget(rsnapshot_conf_edit, 2, 2)

        main_layout.addLayout(grid)
        main_layout.addStretch()

        self.setLayout(main_layout)

        self.show()

    def choose_rsnapshot_config(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')

        if fname[0]:
            self.settings.setValue('rsnapshot_config_path', fname[0])
            self.refresh()

    def choose_ssh_key(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')

        if fname[0]:
            self.settings.setValue('ssh_key_path', fname[0])
            self.refresh()

    def refresh(self):
        self.rsnapshot_conf_value.setText(
            self.settings.value('rsnapshot_config_path'))
        self.ssh_conf_value.setText(
            self.settings.value('ssh_key_path'))
