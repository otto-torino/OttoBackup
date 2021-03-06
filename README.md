# Otto Backup

Otto Backup Application.

![image](https://raw.githubusercontent.com/otto-torino/OttoBackup/master/app.png "App")

A PyQt5 application which acts as an interface to rsnapshot.

## Features

rsnapshot gui:

- select the rsnapshot bin
- select the rsnapshot config
- set the first rsnapshot interval
- run the backup
- display rsnapshot stdout in a text field
- report errors
- report success and save last sync datetime
- it and en locales provided

## Run on Mac OSX

The packaged Mac OSX app is included:

`dist/osx/OttoBacup.app`

It requires some stuff, though:

- install [homebrew](https://brew.sh/)
- install rsnapshot:    
  `$ brew install rsnapshot`
- install a package whici provides `cp` command with linux like options:    
  `$ brew install coreutils`

Make sure to set the right binaries path in the `rsnapshot.conf` file (use `which BINARY_NAME` in a terminal to find them)

## Settings

- rsnapshot bin path: needed because when packaging the application with pyinstaller the environment is not the same as running
through python interpreter and commands are not found if not with absolute path
- rsnapshot configuration file: needed because it is the source if truth, this application just
launches rsnapshot which manages all the backup stuff
- rsnapshot first interval: needed in order to save the last backup datetime. rsnapshot will fetch remote
contents only when performing the first interval, while when performing the other intervals, it will create symlink to
existing directories.

### rsnapshot confiiguration file

OttoBackup will not let you interact with the rsnapshot command, so it is necessary to use the `ssh_args` options and set a private ssh key, i.e.:

    ssh_args	-i /home/user/.ssh/id_rsa

Obviously the pub key must be enabled on the remote server and associated to the user which will perform the backup.

## Usage

Download the project and then

    $ python ottobackup.py

or make it executable.

The rsnapshot configuration file must define at least one of 'daily', 'weekly' or 'monthly' backup intervals.
If only some are defined, then choose the right one from the interval combo box below the sync button.
