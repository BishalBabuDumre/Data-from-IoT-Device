# System packages
import os
import ftplib
from ftplib import FTP_TLS, error_perm
from pathlib import Path
from datetime import date
from datetime import timedelta

# Get home directory
localPath = os.path.join(Path.home(), 'SolarFarm/XML_Summary_As_CSV/Keithley/')

#Getting yesterday's date
yesterday = date.today() - timedelta(days = 1)
yesterday = yesterday.strftime('%Y-%m-%d')

#Function to check whether a folder exist or not.
def ftp_folder_exists(ftp, folder_path):
    current_dir = ftp.pwd()
    try:
        ftp.cwd(folder_path)
        ftp.cwd(current_dir)  # Go back to original directory
        return True
    except error_perm:
        return False


# Environment variables to connect to an online platform (eg. Box)
website = 'ftp.box.com'
username = 'user@company.com'
password = 'password'

# Start FTP connection
ftp = FTP_TLS(website, username, password)
if ftp_folder_exists(ftp, f'/Data/Keithley/{yesterday}'):
    try:
        ftp.cwd(f'/Data/Keithley/{yesterday}')
        with open(os.path.join(localPath, f'{yesterday}.csv'), 'wb') as f:
            try:
                ftp.retrbinary("RETR " + f"Summary{yesterday}.csv", f.write, 8*1024)
            except:
                print("Summary file", 'is empty')
        print("Downloading Complete")
    except ftplib.error_perm:
        raise
else:
    print("Folder does not exist")
ftp.close()