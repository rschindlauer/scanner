#!/usr/bin/python
from time import sleep
from subprocess import *
import commands
import Adafruit_CharLCD as LCD
import logging
logging.basicConfig(filename='/var/local/share/scanlog.txt', level=logging.INFO)
import scanner

# Initialize the LCD using the pins
lcd = LCD.Adafruit_CharLCDPlate()
lcd.set_backlight(0)

scanner.config(folder='/var/local/share',
               tmp_folder='/var/local/share/tmp',
               log='/var/local/share/scanlog.txt')

def upload(local_filepath, onedrive_folder):
    import sys
    import onedrivesdk
    import os
    from onedrivesdk.helpers import GetAuthCodeServer

    onedrive_client_id = os.environ.get('ONEDRIVE_CLIENT_ID')
    if onedrive_client_id == None:
        logging.error('env var ONEDRIVE_CLIENT_ID not found.')
        return

    import ntpath
    filename = ntpath.basename(local_filepath)

    client = onedrivesdk.get_default_client(client_id=onedrive_client_id,
                                            scopes=['wl.signin',
                                                    'wl.offline_access',
                                                    'onedrive.readwrite'])

    # this assumes you have run get_onedrive_auth.py to obtain an authorized
    # and pickled session

    client.auth_provider.load_session()

    logging.info("Uploading %s to %s" % (filename, onedrive_folder))
    client.item(drive="me", path=onedrive_folder).children[filename].upload(local_filepath)

def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output 

def DoScan(mode):
    lcd.clear()
    lcd.message('Scanning...')
    filename = scanner.scan(mode)
    if not filename:
        lcd.message('error')
    else:
        lcd.clear()
        lcd.message('Uploading...')
        upload(filename, 'current work/To File/')
        lcd.message('Completed.')
    sleep(1)

def DoShutdown():
    lcd.clear()
    lcd.message('Are you sure?\nPress Sel for Y')
    while 1:
        if lcd.is_pressed(LCD.LEFT):
            break
        if lcd.is_pressed(LCD.SELECT):
            lcd.clear()
            commands.getoutput("sudo shutdown -h now")
            quit()
        sleep(0.25)

def MainMenu():
    lcd.clear()
    lcd.message('    photo\nfront  duplex')

MainMenu()
while True:
    if lcd.is_pressed(LCD.DOWN):
        DoShutdown()
    if lcd.is_pressed(LCD.LEFT):
        DoScan(mode='front')
        MainMenu()
    if lcd.is_pressed(LCD.RIGHT):
        DoScan(mode='duplex')
        MainMenu()
    if lcd.is_pressed(LCD.UP):
        DoScan(mode='photo')
        MainMenu()
    sleep(0.25)

