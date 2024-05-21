#Imports
import matplotlib
matplotlib.use('agg')
from matplotlib import pyplot as plt
import pandas as pd
from datetime import date
from datetime import datetime
from datetime import timedelta
import numpy as np

#Creating Bold Graph Edges and Fonts
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"
plt.rcParams["axes.linewidth"] = 1.5

#Getting yesterday's date
yesterday = date.today() - timedelta(days = 1)
yesterday = yesterday.strftime('%Y-%m-%d')

#Sort the CSV
def sort_csv(input_file, sort_column):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_file)
    
    # Sort the DataFrame based on the specified column
    df_sorted = df.sort_values(by=sort_column)
    return df_sorted

#Extract only Times from the DateTime
def exDT(dateTime):
    aList = []
    start_index = 11
    end_index = 16
    for original_string in dateTime:
        selected_section = original_string[start_index:end_index]
        aList.append(selected_section)
    return aList

#Change date time object to string times
def tchange(tList):
    time_format = "%H:%M"
    k = []
    for j in tList:
        a = datetime.strptime(j, time_format)
        k.append(a)
    return k

#Extracting various information from files at different locations
input_file1 = f"../../../Project/XML_Summary/103/{yesterday}.csv"
input_file2 = f"../../../Project/XML_Summary/108/{yesterday}.csv"
input_file3 = f"../../../Project/XML_Summary/111/{yesterday}.csv"
input_file4 = f"../../../Project/XML_Summary/113/{yesterday}.csv"
sort_column = 'Date_Time'  # Specify the column you want to sort by

sorted1 = sort_csv(input_file1, sort_column)
dateTime1 = sorted1["Date_Time"].tolist() #Channel 103 Date and Time
tempW = sorted1["Temperature_W"].tolist() #Channel 103 Module Temp
time1 = exDT(dateTime1)
time1 = tchange(time1)

sorted2 = sort_csv(input_file2, sort_column)
dateTime2 = sorted2["Date_Time"].tolist() #Channel 108 Date and Time
tempA = sorted2["Temperature_Ambient"].tolist() #Ambient Temp
tempMT = sorted2["Temperature_Top of MT"].tolist() #Top of MT5 Temp
tempU = sorted2["Temperature_U"].tolist() #Channel 108 Module Temp 1
tempQ = sorted2["Temperature_Q"].tolist() #Channel 108 Module Temp 2
time2 = exDT(dateTime2)
time2 = tchange(time2)

sorted3 = sort_csv(input_file3, sort_column)
dateTime3 = sorted3["Date_Time"].tolist() #Channel 111 Date and Time
tempG = sorted3["Temperature_G"].tolist() #Channel 111 Module Temp 1
tempJ = sorted3["Temperature_J"].tolist() #Channel 111 Module Temp 2
time3 = exDT(dateTime3)
time3 = tchange(time3)

sorted4 = sort_csv(input_file4, sort_column)
dateTime4 = sorted4["Date_Time"].tolist() #Channel 113 Date and Time
tempAF = sorted4["Temperature_AF"].tolist() #Channel 113 Module Temp 1
tempZ = sorted4["Temperature_Z"].tolist() #Channel 113 Module Temp 2

time4 = exDT(dateTime4)
time4 = tchange(time4)

#Finding extreme temp of the day
allTemp = np.concatenate((tempW, tempA, tempMT, tempU, tempQ, tempG, tempJ, tempAF, tempZ))
maxValue = max(allTemp)
minValue = min(allTemp)

#Making x-axis ticks
# Convert lists to sets to remove duplicates
set1 = set(time1)
set2 = set(time2)
set3 = set(time3)
set4 = set(time4)

# Combine all sets and remove duplicates
combined_set = set1.union(set2).union(set3).union(set4)

#Plotting Temperature VS Time
plt.figure()
plt.plot(time1, tempW, c = '#1f77b4', ls = "solid", lw = 1, label = 'Channel 103')
plt.plot(time2, tempA, c = '#ff7f0e', ls = "dotted", lw = 1, label = 'Ambient')
plt.plot(time2, tempMT, c = '#2ca02c', ls = "dashed", lw = 1, label = 'Top of MT5')
plt.plot(time2, tempU, c = '#d62728', ls = "dashdot", lw = 1, label = 'Channel 108 Temp 1')
plt.plot(time2, tempQ, c = '#9467bd', ls = (0, (1, 10)), lw = 1, label = 'Channel 108 Temp 2')
plt.plot(time3, tempG, c = '#8c564b', ls = (0, (5, 10)), lw = 1, label = 'Channel 111 Temp 1')
plt.plot(time3, tempJ, c = '#e377c2', ls = (0, (3, 10, 1, 10)), lw = 1, label = 'Channel 111 Temp 2')
plt.plot(time4, tempAF, c = '#7f7f7f', ls = (0, (3, 5, 1, 5, 1, 5)), lw = 1, label = 'Channel 113 Temp 1')
plt.plot(time4, tempZ, c = '#bcbd22', ls = (0, (3, 1, 1, 1, 1, 1)), lw = 1, label = 'Channel 113 Temp 2')
plt.ylim(minValue - 1, maxValue + 8)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
plt.legend(loc='upper left', bbox_to_anchor=(0, 1.02), fontsize=8, frameon = False, columnspacing=1.25,handlelength=1.75, ncols = 3)
plt.title('Temperature VS Time of the Day', fontsize = 20, fontweight = "bold")
plt.ylabel('Temperature ($\mathregular{^{\circ}}$C)', fontsize = 15)
plt.xlabel('Time of the Day', fontsize = 15)
plt.grid('on')
plt.xticks(rotation='vertical', fontsize = 8)
plt.tight_layout()
plt.savefig('../../../Project/XML_Summary/Temp&Irr/Temp'+str(yesterday)+'.png')
plt.close()

#Getting Irradiance data from Channel 113 data
pyro1 = sorted4["Irradiance_Pyranometer_1"].tolist()
si1 = sorted4["Irradiance_Si_1"].tolist()
si2 = sorted4["Irradiance_Si_2"].tolist()
gaas1 = sorted4["Irradiance_GaAs_1"].tolist()
gaas2 = sorted4["Irradiance_GaAs_2"].tolist()
pyro2 = sorted4["Irradiance_Pyranometer_2"].tolist()

#Finding extreme irradiance of the day
allIrr = np.concatenate((pyro1, si1, si2, gaas1, gaas1, pyro2))
maxValueI = max(allIrr)
minValueI = min(allIrr)

#Plotting Irradiance VS Time
plt.figure()
plt.plot(time4, pyro1, '#1f77b4', ls = "solid", lw = 1, label = 
'Pyranometer_1')
plt.plot(time4, si1, '#ff7f0e', ls = "dotted", lw = 1, label = 'Si_1')
plt.plot(time4, si2, '#2ca02c', ls = "dashed", lw = 1, label = 'Si_2')
plt.plot(time4, gaas1, '#d62728', ls = "dashdot", lw = 1, label = 'GaAs_1')
plt.plot(time4, gaas2, '#9467bd', ls = (0, (1, 10)), lw = 1, label = 'GaAs_2')
plt.plot(time4, pyro2, '#8c564b', ls = (0, (5, 10)), lw = 1, label = 
'Pyranometer_2')
plt.ylim(minValueI - 10, maxValueI + 100)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
plt.legend(loc='upper left', bbox_to_anchor=(0, 1.02), fontsize=8, frameon = False, columnspacing=1.25,handlelength=1.75, ncols = 3)
plt.title('Irradiance VS Time of the Day', fontsize = 20, fontweight = "bold")
plt.ylabel('Irradiance (Wm$\mathregular{^{-2}}$)', fontsize = 15)
plt.xlabel('Time of the Day', fontsize = 15)
plt.grid('on')
plt.xticks(rotation='vertical', fontsize = 8)
plt.tight_layout()
plt.savefig('../../../Project/XML_Summary/Temp&Irr/Irr'+str(yesterday)+'.png')
plt.close()
