# System packages
import os
import ftplib
from ftplib import FTP_TLS
from pathlib import Path

# Get home directory
localPath = os.path.join(Path.home(), 'SolarFarm')

# Environment variables to connect to Box
website = os.getenv('IP_ADDRESS')
username = os.getenv('IoT_USERNAME')    
password = os.getenv('IoT_PASSWORD')

# Change to folder of IV curves

folders = ['/Data/mtd','/Data/Temp&Irr&Wind&Hum','/Data/stcFigures','/Data/Videos','/Data/WeeklyFigures','/Data/Cleaned','/Data/101','/Data/102',
           '/Data/112','/Data/103','/Data/104','/Data/105','/Data/106','/Data/108','/Data/109','/Data/110','/Data/111','/Data/113','/Data/114','/Data/115']
for folder in folders:
    # Start FTP connection
    ftp = FTP_TLS(website, username, password)
    try:
        ftp.cwd(folder)
    except ftplib.error_perm:
        continue
    try:
    # Get list of files in folder
        files = ftp.nlst()
    except ftplib.error_perm as resp:
        if str(resp) == "550 No files found":
            print("No files in this directory")
        else:
            raise

# Lists all the files that we already have in the local folders to only upload missing ones
    if folder[38:]=='mtd':
        localDataPath = os.path.join(localPath, 'MTDlocal')
    elif folder[38:] in ('Temp&Irr&Wind&Hum', 'stcFigures', 'Videos', 'WeeklyFigures', 'CleanedForSTC'):
        localDataPath = os.path.join(localPath, 'Company_1', folder[38:])
    else:
        localDataPath = os.path.join(localPath, "XML_Summary_As_CSV", folder[38:])

    localDataFiles = os.listdir(localDataPath)

# Compares the two lists
    missing = list(sorted(set(localDataFiles) - set(files)))

# Print the names of the missing files
    print(f'In total there are missing: {len(missing)}')
    if (missing != 0):
        print("Uploading...")
        for filename in missing:
            with open(os.path.join(localDataPath, filename), 'rb') as f:
                try:
                    ftp.storbinary(f'STOR {filename}', f)
                except:
                    print(filename, 'is empty')  
    ftp.close()