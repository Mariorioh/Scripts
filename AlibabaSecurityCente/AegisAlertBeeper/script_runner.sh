#!/bin/bash
#make-run.sh
#make sure a process is always running.
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin

export DISPLAY=:0 #needed if you are running a simple gui app.

process_name="AegisAlertBeeper.py"
command="sudo python3 /path/to/file/AegisAlertBeeper.py"

if ps ax | grep -v grep | grep $process_name > /dev/null
then
    exit
else
    $command &
fi

exit