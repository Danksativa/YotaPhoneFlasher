# -*- coding: utf-8 -*-

__author__ = 'Egor Vasilyev'
__email__ = 'egor.vasilyev@yotadevices.com'
__version__ = '0.1.0'
if __name__ == "__main__":

import shutil
import os
import optparse
import zipfile
import ftplib
import progressbar
import configparser

def currentFirmwarePrint():
    config.read('config.ini')
    currentFirmware = config['YotaPhoneFlasher']['currentFirmware']
    if currentFirmware != '':
        print("Your current firmware is: "+currentFirmware+'\n')


global ftp
def wayChooser():
    currentFirmwarePrint()
    print("1. Flash the cellphone")
    print("2. Download new firmware")
    print("3. Exit")
    way = input("What would you like to do?\n")
    if way == '1':
        flash()
    elif way == "2":
        global ftp
        ftp = ftplib.FTP(ftpURL)
        ftp.login(ftpUser, ftpPass)
        ftp.cwd(ftpPath)
        regionChooser()
    elif way == "3":
        os.system("exit")
    else:
        print ("Please, choose a number")
        wayChooser()

def regionChooser():
    currentFirmwarePrint()
    ftp.cwd(ftpPath)
    regions = []
    regions = ftp.nlst()
    counter = 1
    print ("0. Back")
    for i in regions:
        print(str(counter)+". "+i)
        counter = counter +1
    try:
        regionNumber = int(input("Please, choose the Region: "))
        if regionNumber != 0:
            region = regions[regionNumber -1]
            firmwareChooser(region)
        else:
            wayChooser()
    except:
        print("Please choose region number")
        regionChooser()

def firmwareChooser(region):
    currentFirmwarePrint()
    ftp.cwd(ftpPath+"/"+region)
    firmwares = []
    firmwares = ftp.nlst()
    counter = 1
    print ("0. Back")
    for j in firmwares:
        print(str(counter)+". "+j)
        counter = counter +1
    try:
        firmwareNumber = int(input("Please, choose the Firmware: "))
        if firmwareNumber != 0:
            firmware = firmwares[firmwareNumber-1]
            ftpDownlaod(firmware,region)
        else:
            
            regionChooser()
except:
    print("Please choose firmware number")
        firmwareChooser(region)
    return firmware

config = configparser.ConfigParser()
config.read('config.ini')
ftpURL   =config['YotaPhoneFlasher']['ftpURL']
ftpUser  =config['YotaPhoneFlasher']['ftpUser']
ftpPass  =config['YotaPhoneFlasher']['ftpPass']
ftpPath=config['YotaPhoneFlasher']['ftpPath']

def ftpDownlaod(firmware,region):
    ftp.cwd(ftpPath+"/"+region)
    ftp.voidcmd('TYPE I')
    print("Wait for Downloading")
    if os.path.exists("firmware"):
        shutil.rmtree('firmware')
    os.makedirs("firmware")
    filesize = ftp.size(firmware)
    progress = progressbar.AnimatedProgressBar(end=filesize, width=50)
    with open("firmware/"+firmware, 'wb') as f:
        def callback(chunk):
            f.write(chunk)
            progress + len(chunk)
            progress.show_progress()
        ftp.retrbinary("RETR " + firmware , callback)
    print("Downloading finished")
    z=zipfile.ZipFile('firmware/'+firmware, "r")
    z.extractall("firmware")
    z.close()
    if os.path.isfile('firmware/'+firmware):
        os.remove('firmware/'+firmware)
    config['YotaPhoneFlasher']['currentFirmware'] = firmware
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    wayChooser()

def flash():
    os.system("fastboot flash aboot firmware/emmc_appsboot.mbn")
    os.system("fastboot flash boot firmware/boot.img")
    os.system("fastboot flash system firmware/system.img")
    os.system("fastboot flash recovery firmware/recovery.img")
    os.system("fastboot flash cache firmware/cache.img")
    os.system("fastboot flash modem firmware/radio/NON-HLOS.bin")
    os.system("fastboot flash sbl1 radio/sbl1.mbn")
    os.system("fastboot flash rpm firmware/radio/rpm.mbn")
    os.system("fastboot flash tz firmware/radio/tz.mbn  ")
    os.system("fastboot flash aboot firmware/emmc_appsboot.mbn")
    userdata = input("Would you like to flash userdata[Y/N]: ")
    if userdata == "Y" or userdata == "y" or userdata == "yes" or userdata == "Yes" or userdata == "Yes":
        os.system("fastboot flash userdata firmware/userdata.img")
    os.system("fastboot reboot")
    wayChooser()

parser = optparse.OptionParser()
parser.add_option('-f', '--folder',
                  action="store", dest="folder",
                  help="set the folder", default="")
parser.add_option('-t', '--task',
                  action="store", dest="task",
                  help="set the task", default="")
arg, args = parser.parse_args()

wayChooser()