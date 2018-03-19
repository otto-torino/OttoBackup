from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout

from utils import icon, style


class InfoDialog(QDialog):
    def __init__(self):
        super(InfoDialog, self).__init__()
        self.translate = QtCore.QCoreApplication.translate
        self.init_ui()

    def init_ui(self):
        # styles
        sshFile = style()
        with open(sshFile, "r") as fh:
            self.setStyleSheet(fh.read())
        # dimensions and positioning
        self.resize(500, 300)
        # window props
        self.setObjectName("Info")
        self.setWindowTitle(self.translate('InfoDialog', 'Info'))

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)

        title = QLabel('<h1>Otto Backup - v1.0.0</h1>')
        title.setAlignment(QtCore.Qt.AlignCenter)
        description = QLabel(
            self.translate(
                'InfoDialog',
                'GUI for the rsnapshot command, manage your backups with ease.'
            ))
        description.setAlignment(QtCore.Qt.AlignCenter)
        image = QLabel('<img src="%s" />' % icon('icon.png'))
        image.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(title)
        main_layout.addWidget(description)
        main_layout.addWidget(image)
        main_layout.addStretch()

        self.setLayout(main_layout)

        self.show()
