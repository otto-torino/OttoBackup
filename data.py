import subprocess
import datetime
import os


class ApplicationData(object):
    def __init__(self):
        self.data_dir = os.path.expanduser(
            os.path.join(
                '~',
                '.ottobackup'
            )
        )
        self.history_file = os.path.join(
            self.data_dir,
            'history'
        )

    def setup(self):
        if not os.path.isdir(self.data_dir):
            os.makedirs(self.data_dir)

        if not os.path.isfile(self.history_file):
            open(self.history_file, 'a').close()

    def get_last_sync(self):
        line = subprocess.check_output(['tail', '-1', self.history_file])
        if not line:
            return None
        else:
            try:
                date = datetime.datetime.fromtimestamp(float(line))
                return date.strftime('%d/%m/%Y %H:%M')
            except ValueError:
                # corrupted history file
                open(self.history_file, 'w').close()
                return None

    def store_las_sync(self, utc):
        with open(self.history_file, 'a') as file:
            seconds = (utc - datetime.datetime(1970, 1, 1)).total_seconds()
            file.write(str(seconds) + '\n')
