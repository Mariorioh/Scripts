===========================================================================
Script Overview: 
This python script allows the user to fetch Alibaba Security Center Alerts Servers which are online.

Prerequisites
1.) Install a python 3.6 or above.
2.) Install the packages listed in the "requirements.txt" file.
3.) In order to connect to the Alibaba API server. You need to have an access ID and secret key. Fill up the "config.json" file accordingly.

Installation: 
1.) Copy and paste the following files into your working directory:
    - AegisGetOnlineServers.py
    - config.json
2.) Open the following files:
    - AegisGetOnlineServers.py
3.) Edit the AegisGetOnlineServers.py, fill up the script_path with your working directory:
    >> script_path = ""
    replace with:
    >> script_path = "<path/to/your/working/directory>"
4.) Edit the config.json file and fill it up with your corresponding access ID and secret key.

How To Use
1.) In your working directory, type in the command line: 
    >> python AegisGetOnlineServers.py
    or
    >> python3 AegisGetOnlineServers.py
2.) Upon running the script. It will get all online servers from the Alibaba Security Center. Sample console output:
    >> python3 AegisGetOnlineservers.py
    >> Getting list of online servers (1234)...
    >> Done, list saved to 'aegis_online_servers.csv' file
    >>

    Sample console output from a failed connection:
    >>python3 AegisGetOnlineservers.py
    >>Alibaba Connection Failed.HTTPSConnectionPool(host='tds.aliyuncs.com', port=443): Max retries exceeded with url: /?Action=DescribeCloudCenterInstances&Format=json&Version=2018-12-03&Timestamp=2021-12-20T06%3A56%3A32Z&SignatureNonce=d41c02af-0d5d-509c-bcf9-c7b302577ac9&SignatureMethod=HMAC-SHA1&SignatureVersion=1.0&AccessKeyId=LTAI5tFuHXha9gEgnxeC2V2E&Signature=Li%2BibVPXy2HTlozSoJYRYgph3V0%3D (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x000001DD4FC088B0>: Failed to establish a new connection: [Errno 11001] getaddrinfo failed'))
    >>
3.) New files will be generated on the same directory.
    - aegis_online_servers.csv - A comma delimited file, this contains the list of online server's instance name and IP's
    - dcci_debug.log - Used for debugging

===========================================================================
