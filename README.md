# Otto Backup

Otto Backup Application.

![image](https://raw.githubusercontent.com/otto-torino/OttoBackup/master/app.png "App")

A PyQt5 application which acts as an interface to rsnapshot.

## Features

rsnapshot gui:

- select the rsnapshot config
- set the first rsnapshot interval
- run the backup
- display rsnapshot stdout in a text field
- report errors
- report success and save last sync datetime
- it and en locales provided

## Settings

- rsnapshot configuration file: needed because it is the source if truth, this application just
launches rsnapshot which manages all the backup stuff
- rsnapshot first interval: needed in order to save the last backup datetime. rsnapshot will fetch remote
contents only when performing the first interval, while when performing the other intervals, it will create symlink to
existing directories.

## Usage

Download the project and then

    $ python ottobackup.py

or make it executable.

The rsnapshot configuration file must define at least one of 'daily', 'weekly' or 'monthly' backup intervals.
If only some are defined, then choose the right one from the interval combo box below the sync button.
