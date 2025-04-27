"""
Code to request data from the ftp folder from server
Run the code every day to download previous day
"""
# System packages
import os
import ftplib
from ftplib import FTP
from pathlib import Path

# Get home directory
localDataPath = os.path.join(Path.home(), 'SolarFarm/XMLlocal')
os.makedirs(localDataPath, exist_ok=True)

# Environment variables to connect to Daystard FTP server
website = os.getenv('IP_ADDRESS')
username = os.getenv('IoT_USERNAME')    
password = os.getenv('IoT_PASSWORD')

# Start FTP connection
ftp = FTP(website, username, password)

# Change to folder of IV curves
folder = 'curves'  # Other option is: mtd

ftp.cwd(folder)
try:
    # Get list of files in folder
    files = ftp.nlst()
except ftplib.error_perm as resp:
    if str(resp) == "550 No files found":
        print("No files in this directory")
    else:
        raise

# Lists all the files that we already have in the xml folder to only download missing ones
localDataFiles = os.listdir(localDataPath)

# Compares the two lists
missing = list(sorted(set(files) - set(localDataFiles)))

# Print the names of the missing files
print(f'In total there are missing: {len(missing)}')
if (missing != 0):
    print("Downloading...")
    for filename in missing:
        with open(os.path.join(localDataPath, filename), 'wb') as f:
            try:
                ftp.retrbinary("RETR " + filename, f.write, 8*1024)
            except:
                print(filename, 'is empty')
    print("Downloading Complete")
ftp.close()