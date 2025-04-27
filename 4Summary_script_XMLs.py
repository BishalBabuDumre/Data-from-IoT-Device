"""
Code to Summarize the IV data into one file per channel
"""
#### import csv
import re
import xml.etree.ElementTree as ET
import sys
import pandas as pd
import xml
import time
from collections import OrderedDict, defaultdict
from pathlib import Path
import numpy as np
import os
import warnings

# Suppress RankWarning
warnings.simplefilter('ignore', np.RankWarning)


meta_data = OrderedDict({})
unnested_params = 'Date_Time,Name,PeakPower,Vpeak,Ipeak,Isc,Voc,FillFactor'
nested_params = {
                'Temp1': 'Value',
                'Temp2': 'Value',
                 }

localDataPath = os.path.join(Path.home(), 'SolarFarm/XMLlocal')
savePath = os.path.join(Path.home(), 'SolarFarm/XML_Summary_As_CSV')
startTime = time.time()

localDataFiles = os.listdir(localDataPath)

regex = '(\d\d\d)_([01][0-9])([0-3][0-9])(20\d\d)_([0-2][0-9])([0-5][0-9])'

module_list = []

groups = defaultdict(list)
for fileName in localDataFiles:
    if not '.xml' in fileName or 'last_iv' in fileName:
        continue
    filePath = os.path.join(localDataPath, fileName)
    fileSize = os.path.getsize(filePath)
    if fileSize <= 10:
        continue

    m = re.search(regex, fileName)
    module_id = m.group(1)
    date_time = '{year}-{month}-{day}'.format(year=m.group(4),
            month=m.group(2), day=m.group(3), hour=m.group(5),
            minutes=m.group(6))
    module_list.append(module_id)

    if not module_id in groups:
        groups[module_id] = {}
    if not date_time in groups[module_id]:
        groups[module_id][date_time] = []

    groups[module_id][date_time].append(filePath)

print(len(localDataFiles),'files to process')

for module_id in module_list:
    folder = os.path.join(savePath, module_id)
    os.makedirs(folder, exist_ok=True)

for key in groups:
    folder = os.path.join(savePath, key)
    for date in groups[key]:
        daily_files = []
        for filePath in groups[key][date]:
            fileSize = os.path.getsize(filePath)
            if fileSize >= 10485:
                try:
                    meta_data = OrderedDict({})
                    tree = ET.parse(filePath)
                    for param in unnested_params.split(','):
                        meta_data[param] = tree.find("./Curve/{0}".format(param)).text
                    for param, value in nested_params.items():
                        try:
                            meta_data[param] = tree.find("./Curve/{0}/{1}".format(param, value)).text
                        except:
                            continue

                    for temperature in tree.findall('./Curve/Temperatures/Temperature'):
                        meta_temp = temperature.attrib
                        name = meta_temp['description']
                        meta_data[f'Temperature_{name}'] = float(meta_temp['value'])

                    ####### Find the MPP #######
                    voltages = []                                  #Creates a list to store the voltages
                    currents = []                                  #Creates a list to store the voltages

                    # Get the voltage points from the xml
                    for volts in tree.findall('./Curve/Points/Point/Volts'):
                        voltages.append(float(volts.text))

                    # Get the Current points from the xml
                    for amps in tree.findall('./Curve/Points/Point/Amps'):
                        currents.append(float(amps.text))

                    #voltages = voltages[2:-1] # throws out spurrious points at begining and end of IV curve
                    #currents = currents[2:-1] # throws out spurrious points at begining and end of IV curve
                    voltages = voltages[:-1] # throws out spurrious points at begining and end of IV curve
                    currents = currents[:-1] # throws out spurrious points at begining and end of IV curve

                    meta_data[f'volts_curve'] = voltages
                    meta_data[f'amps_curve'] = currents

                    meta_data[f'Calculated_Voc'] = voltages[-1]
                    meta_data[f'Calculated_Isc'] = currents[0]

                    try:
                        ####### Do the curve fit #######
                        data = {'voltage':voltages,'current':currents}  # combines IV data into one list
                        df = pd.DataFrame(data)                         # makes a dataframe out of the combined list
                        df['mpp'] = df['voltage']*df['current']         # creates a max power point column
                        s = df.idxmax()                                 # Identifies the maximum values for each collumn
                        s['mpp']                                        # finds maximum power point
                        df1=df.iloc[s['mpp']-5:s['mpp']+5]              # creates dataframe with 3 points on either side of the mpp
                        polynomial_coefficients = np.polyfit(df1['voltage'],df1['mpp'],4) # finds coefficients for the 4th degree polynomial fit
                        xnewvalues=np.linspace(np.min(df1['voltage']),np.max(df1['voltage']),1000) # makes a list of 1000 points between max and min voltages
                        ynewvalues=np.poly1d(polynomial_coefficients)
                        ynewvalues2=ynewvalues(xnewvalues)
                        data2 = {'voltage':xnewvalues,'MPP':ynewvalues2}
                        df3 = pd.DataFrame(data2)
                        s1 = df3.idxmax()
                        s1['MPP']
                        maxPower = df3.MPP.at[s1['MPP']]
                        maxVoltage = df3.voltage.at[s1['MPP']]
                        ####### End curve fit #######
                    except:
                        maxPower = 1
                        maxVoltage = 1

                    ####### Print in the summary file #######
                    meta_data[f'Calculated_Imp'] = round(maxPower/maxVoltage,8)
                    meta_data[f'Calculated_Vmp'] = round(maxVoltage,8)
                    ####### End find the MPP #######

                    for auxInput in tree.findall('./Curve/AuxInputs/AuxInput'):
                        meta_auxInput = auxInput.attrib
                        name = meta_auxInput['description']
                        meta_data[f'auxInput_converted_value_{name}'] = float(meta_auxInput['converted_value'])

                    for irradiance in tree.findall('./Curve/Irradiances/Irrad'):
                        meta_irrad = irradiance.attrib
                        name = meta_irrad['description']
                        meta_data[f'Irradiance_before_{name}'] = float(meta_irrad['converted_value'])

                    for afterIrradiance in tree.findall('./Curve/AfterIrradiances/Irrad'):
                        meta_afterIrrad = afterIrradiance.attrib
                        name = meta_afterIrrad['description']
                        meta_data[f'Irradiance_after_{name}'] = float(meta_afterIrrad['converted_value'])

                    for param in 'PeakPower,Vpeak,Ipeak,Isc,Voc,FillFactor'.split(','):
                        meta_data[param] = float(meta_data[param])

                    daily_files.append(meta_data)
                except xml.etree.ElementTree.ParseError:
                    print('-- BREAK inner loop')
                    break
        output_df = pd.DataFrame(daily_files)
        sort_column = 'Date_Time'  # Specify the column you want to sort by
        try:
            output_df = output_df.sort_values(by=sort_column)
        except:
            continue
        output_df.to_csv(os.path.join(folder, date + ".csv"), index=False)
        

fNames = '101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,Keithley' # after move

for fName in fNames.split(','):
    try:
        localSummaryPath = os.path.join(savePath, fName)
        os.makedirs(localSummaryPath, exist_ok=True)
        localDataFiles = os.listdir(localSummaryPath)
        significantDataFiles = []

        for fileName in localDataFiles:
            if not '.csv' in fileName or'last_iv' in fileName:
                continue
            filePath = os.path.join(localSummaryPath, fileName)
            fileSize = os.path.getsize(filePath)
            if fileSize <= 10:
                continue
            significantDataFiles.append(filePath)
        
        df = pd.concat([pd.read_csv(f) for f in significantDataFiles], sort=True)
        df = df.sort_values(by=sort_column)
        df.to_csv(os.path.join(savePath, fName + '.csv'), index=False)
    except:
        print("Error with " + fName)
        raise
        # continue
print("Summary Complete!")