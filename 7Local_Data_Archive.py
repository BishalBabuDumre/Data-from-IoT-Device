"""
Code to archive data locally and on the cloud
"""
import os
import shutil
from pathlib import Path

def copyFile(source_path, destination_folder):
    try:
        # Check if the file exists before attempting to move
        if os.path.exists(source_path):
            # Extract the filename from the source path
            file_name = os.path.basename(source_path)
            destination_path = os.path.join(destination_folder, file_name)

            # Move the file to the destination folder
            shutil.copy(source_path, destination_path)
            print(f"File '{file_name}' has been copied to '{destination_folder}'.")
        else:
            print(f"File '{source_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

def moveFile(source_path, destination_folder):
    try:
        # Check if the file exists before attempting to move
        if os.path.exists(source_path):
            # Extract the filename from the source path
            file_name = os.path.basename(source_path)
            destination_path = os.path.join(destination_folder, file_name)

            # Move the file to the destination folder
            shutil.move(source_path, destination_path)
            print(f"File '{file_name}' has been moved to '{destination_folder}'.")
        else:
            print(f"File '{source_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Get todays Date
from datetime import date, timedelta, datetime
# Get today's date
today = date.today()
print('today',today)

# Calculate the date 5 weeks ago
two_weeks_ago = today - timedelta(weeks=5)
#two_weeks_ago = two_weeks_ago.strftime("%m%d%Y")
# Print the date in the format: YYYY-MM-DD
end_date = two_weeks_ago
print('two weeks ago:',end_date)

# Define the start date
start_date = date(2020, 1, 1)

# Get a list of the files in the folder
localDataPath = os.path.join(Path.home(), 'SolarFarm/XMLlocal')
localDataFiles = os.listdir(localDataPath)
localArchivePath = os.path.join(Path.home(), 'SolarFarm/XMLarchive')
cloudArchivePath = os.path.join(Path.home(), 'Library/CloudStorage/Box-Box/Data_archive')

os.makedirs(localArchivePath, exist_ok=True)
os.makedirs(cloudArchivePath, exist_ok=True)

localArchiveFiles = os.listdir(localArchivePath)
cloudArchiveFiles = os.listdir(cloudArchivePath)

# Lists all the files that we already have in the xml folder to only download missing ones
# Compares the two lists
missing = list(sorted(set(localDataFiles) - set(cloudArchiveFiles)))

print("total files in folder:",len(localDataFiles))
print("missing in backups:",len(missing))
# Get the date from each file name
for fileName in localDataFiles:
    if not '.xml' in fileName or 'last_iv' in fileName:
        continue

    # Extract MMDDYYYY using string slicing
    test_date_str = fileName.split('_')[1]
    if test_date_str == 'iv':
        continue

    filePath = os.path.join(localDataPath, fileName)
    
    if(fileName in missing):
        copyFile(filePath, localArchivePath)
        copyFile(filePath, cloudArchivePath)

    # Convert the test date string to a datetime object in the format MMDDYYYY
    test_date = datetime.strptime(test_date_str, "%m%d%Y").date()

    # Check if the test date is older than a set period
    if test_date <= end_date:
        moveFile(filePath, localArchivePath)

localDataFiles = os.listdir(localDataPath)
print('this many files exist after:',len(localDataFiles))