"""
Code to remove files from server
"""
# System packages
import os
import ftplib
from ftplib import FTP
from pathlib import Path
from datetime import date, timedelta, datetime

# Get todays Date
today = date.today()
print('today',today)

# Calculate the date 2 weeks ago
two_weeks_ago = today - timedelta(weeks=2)

# Print the date in the format: YYYY-MM-DD
end_date = two_weeks_ago
print('two weeks ago:',end_date)

# Define the start date
start_date = date(2020, 1, 1)

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

print('this many files exist before:',len(files))
# Get the date from each file name
for file in files:
    # Extract MMDDYYYY using string slicing
    test_date_str = file.split('_')[1]
    if test_date_str == 'iv':
        continue

    # Convert the test date string to a datetime object in the format MMDDYYYY
    test_date = datetime.strptime(test_date_str, "%m%d%Y").date()

    # Check if the test date is older than 2 weeks
    if test_date <= end_date:
        ftp.delete(file)

try:
    # Get list of files in folder
    files = ftp.nlst()
except ftplib.error_perm as resp:
    if str(resp) == "550 No files found":
        print("No files in this directory")
    else:
        raise
print('this many files exist after:',len(files))

ftp.quit()