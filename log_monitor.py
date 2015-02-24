# Don't forget to set up environment var SMTP_PASS_MAIL befor running script
# Command to set up (UNIX shell): export SMTP_PASS_MAIL='pass_from_mail_box'


import datetime
import os
import smtplib
import socket
import subprocess
import time

from email.mime.text import MIMEText

ERR_LOG = "/var/log/nginx/error.log"  # Log file of service which we observe.
FROM_MAIL_SERV = "mail.ru"
TO_MAIL = "reciever@gmail.com"  # Email of mail recipient.
LOGIN = "sender_box"  # Login to our email box.
PASS = os.environ["SMTP_PASS_MAIL"]  # Password from our email box.
LOG_FILE = "smtp_log.txt"  # Log file with results of our script acting.
SLEEP_INTERVAL = 5  # Interval in secs before new checking of service log.


def write_to_file(file_adr, data):
    print("Writting to file was started.")
    try:
        f = open(file_adr, 'a')
        f.write(data)
        f.close()
        print("Writting was finished.")
    except:
        return "LogFileError"
    return 0


previous_data = ''  # Var with error.log data from previous circle.
err_mess_was_sent = True  # Flag informs that email with error was sent.

while True:
    print("New circle.")
    # Get the last part of service error.log (*NIX OS):
    data = subprocess.check_output(['tail', ERR_LOG])
    print(datetime.datetime.now())
    print("hash data: ", hash(data))
    print("hash prev: ", hash(previous_data))

    # Check if there are any new information in error.log:    
    if (previous_data != data and data) or not err_mess_was_sent:
        err_mess_was_sent = False

        smtp = smtplib.SMTP_SSL(port=465, timeout=6)
        try:
            smtp_reply = smtp.connect("smtp."+FROM_MAIL_SERV)
            print("smtp_reply: ", smtp_reply)
            try:
                smtp_login = smtp.login(LOGIN, PASS)
                print ("smtp login: ", smtp_login)
                log_file_data = ("\n" + "="*30 + str(datetime.datetime.now()) +
                                 "\nemail message:\n" + str(data))
                try:
                    smtp.sendmail(LOGIN + "@" + FROM_MAIL_SERV, TO_MAIL, 
                                  log_file_data)
                    print("Mail was sent.")
                    err_mess_was_sent = True 
                except:
                    log_file_data = ("\n" + "="*30 + str(datetime.datetime.now()) + 
                                     "\nSMTP sending mail error")
            except:
                print("SMTP login to mailbox error.")
                log_file_data = ("\n" + "="*30 + str(datetime.datetime.now()) + 
                                 "\nSMTP login to mailbox error")
            smtp.quit()
        except: 
            print("SMTP connection error.")
            log_file_data = ("\n" + "="*30 + str(datetime.datetime.now()) + 
                             "\nSMTP connection error")

        write_to_file(LOG_FILE, log_file_data)

    previous_data = data
    time.sleep(SLEEP_INTERVAL)
