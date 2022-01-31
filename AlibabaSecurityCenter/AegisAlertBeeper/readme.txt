===========================================================================
Script Overview: 
This python script allows the user to fetch Alibaba Security Center Alerts and send them to a Mango chat group as a message.

Prerequisites
1.) Install a python 3.6 or above.
2.) Install the packages listed in the "requirements.txt" file.
3.) In order to connect to the Alibaba API server. You need to have an access ID and secret key.
4.) In order to send messages to a Mango chat group. You need to have a Mango Bot ID, Token and Mango Room ID.
5.) Make sure your IP is whitelisted on Mango's Server. Else the script won't get a response.

Installation: 
1.) Copy and paste the following files into your working directory:
    - AegisAlertBeeper.py
    - MangoBot.py
    - AccessKeyPair.py
    - config.json
    - script_runner.sh
2.) Open the following files:
    - AegisAlertBeeper.py
    - MangoBot.py
    - AccessKeyPair.py
3.) Edit the line:
    >> script_path = ""
    replace with:
    >> script_path = "<path/to/your/working/directory"
4.) Edit the config.json file:
    - Fill up with your Alibaba Access ID, Secret Key, Mango Bot ID, Token, and Room ID accordingly.

How To Use
1.) In your working directory, type in the command line: 
    >> python AegisAlertBeeper.py
    or
    >> python3 AegisAlertBeeper.py
2.) Upon running the script. It will regularly check for Alibaba Security Alerts every 2nd minute.
3.) New files will also be generated on the same directory. These are log files.
    - AegisAlertBeeper.log - This is the log file, it also mirrors the output of the messages sent to Mango group chat
    - AegisAlertBeeperDebug.log - Used for debugging
    - MangoBotDebug.log - Used for debugging

In case you want to ensure that the script is always running in a linux server: 
1.) Add a job to the cron service
  a.) Create or edit the cron file using crontab command: 
    >> crontab -e
  b.) Put this line. Make sure a new line is included.
    >>SHELL=/bin/bash
    >>PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin
    >>
    >> * * * * * sudo bash /path/to/file/script_runner.sh 2>&1 | logger -t alert_beeper_tag
    >>
    * The 4th line specifies to cron that every minute, run the script_running.sh script.
  c.) To check the scheduled job, use the "-l" flag. Sample usage:
    >> crontab -l
  d.) Make sure the cron service is running. Use the command: 
    >> service crond status
===========================================================================

