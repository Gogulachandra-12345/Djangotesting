Emailing Service
=======
## Dir structure:
    Emailing_Service
    |_ Emailing_Service (server & settings)
    |_ core_app (code_repo)
    |_ requirements.txt
    |_ others (logs)

## Commands
    Follow the sequence of commands
    1. screen
    2. press Enter
    3. python3 manage.py runserver 2>&1 | tee -a server.out
    4. Press ctrl+A
    5. Press D
    6. source start.sh
    7. The server would have started now, to verify status you can check either:
        a. ps aux | grep runserver (Shows if server process has spawned)
        b. tail logs/services/log_..(start_of_week - end_of_week)

## Status Codes
1.  Vendor (tbl_vendors) - **'cleaned'** field
    1. STATUS_DEFAULT = 1
    2. STATUS_SCHEDULED = 2
    3. STATUS_CLEANED = 3

2. Schedulers/Templates (tbl_vendor_schedulers) - **status** field
    1. STATUS_FRESH = '1'
    2. STATUS_SUCCESS = '2'
    3. STATUS_DELAYED = '3'
    4. STATUS_FAILED = '4'
    

---
###  ToDo:
- Sync all datetimes
- Add DKIM message
- Check the auto-reply on Gmail responders
- Remove loglevel set on SMTP xchange
- Add regex pattern match
- Investigate the common connection closed unexcpectedly error
- Add monitoring of the CPU, Memory and add signaling (maybe Prometheus)
- Remove the initial REST call
- Debug the django.setup() mandatory call, seems like it might break



