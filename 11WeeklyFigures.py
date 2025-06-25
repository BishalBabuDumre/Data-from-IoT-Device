#Imports
import os
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import date
from datetime import timedelta
from sklearn.ensemble import IsolationForest
import numpy as np
import matplotlib.colors as mcolors
import json

# Set the option to display all rows
pd.set_option('display.max_rows', None)

#Creating Bold Graph Edges and Fonts
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"
plt.rcParams["axes.linewidth"] = 1.5
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.titlesize"] = 14

status_file = "ConfigurationFile.csv"
yesterday = date.today() - timedelta(days = 1)

def company_channels_dict(status_file):
    df = pd.read_csv(status_file)
    company_channels_dict = {}

    # Step 3: Iterate over each row
    for idx, row in df.iterrows():
        companies = str(row['Company']).strip()
        channel = str(row['Channel #']).strip()
        module_name = str(row['Module Name']).strip()       
        module_area = str(row['Area (cm2)']).strip()
        module_isc = str(row['Isc (A)']).strip()
        module_ipeak = str(row['Imp (A)']).strip()
        
        # Skip rows where Company or Channel is nan or empty
        if companies.lower() == 'nan' or companies == '' or channel.lower() == 'nan' or channel == '':
            continue

        # Step 4: Split multiple companies, strip spaces
        company_list = [c.strip() for c in companies.split(',')]
        
        # Step 5: Add channel to each company in dict
        for company in company_list:
            if company not in company_channels_dict:
                company_channels_dict[company] = {"channel_nos" : [], "module_names" : [], "module_area" : [], "isc" : [], "ipeak" : []}
        
        for key in company_channels_dict:
            if key in company_list:
                company_channels_dict[key]["channel_nos"].append(channel)
                company_channels_dict[key]["module_names"].append(module_name)
                company_channels_dict[key]["module_area"].append(module_area)
                company_channels_dict[key]["isc"].append(module_isc)
                company_channels_dict[key]["ipeak"].append(module_ipeak)

    return company_channels_dict

full_dict = company_channels_dict(status_file)

#Data clean function that generates two data frames for plotting
def dataClean(fileRoad, area):
    if not os.path.exists(fileRoad):
        print(f"Warning: File {fileRoad} not found. Skipping...")
    else:
        df = pd.read_csv(fileRoad)

        df["Si_ref_058_delta"] = (df["Irradiance_after_Irrad Si-Ref 058"]
                                - df["Irradiance_before_Irrad Si-Ref 058"])

        df = df.query("-3 < Si_ref_058_delta < 3").copy()
        df = df.query("days_on_sun > 0").copy()

        df.loc[:, "Irrad_Si_Ref_058"] = df["Irradiance_before_Irrad Si-Ref 058"]
        df.loc[:, 'Efficiency'] = (df['PeakPower'] / df["Irrad_Si_Ref_058"])*1000000/area
        columns_to_extract = ['Vpeak', 'Ipeak', 'Voc', 'Isc', 'Temp1', 'Temp2', 'Temperature_Ambient', 'Temperature_Top of MT',
                    'auxInput_converted_value_Humidity (relative)', 'auxInput_converted_value_Wind Speed', 
                    'Irradiance_before_Irrad Si-Ref 058', 'Irradiance_before_Irrad Si-Ref 061']
        
        X = df[columns_to_extract]
        clf = IsolationForest('n_estimators': 50, 'max_samples': 0.9084561500050461, 'max_features': 12, contamination='auto')#Hyperparameters obtained from Bayesian Optimization as in hyperparameterTuningForAnomalyDetection.py
        outliers = clf.fit_predict(X)
        df['outlier'] = outliers 
        df = df[df['outlier'] == 1]

        df1 = df.query('850 < Irrad_Si_Ref_058 < 950').copy()
        df1.loc[:, "Isc"] = (df1["Isc"] / df1["Irrad_Si_Ref_058"])*900
        df1.loc[:, "Ipeak"] = (df1["Ipeak"] / df1["Irrad_Si_Ref_058"])*900
        df2 = df.query('500 < Irrad_Si_Ref_058 < 600').copy()
        df2.loc[:, "Isc"] = (df2["Isc"] / df2["Irrad_Si_Ref_058"])*550
        df2.loc[:, "Ipeak"] = (df2["Ipeak"] / df2["Irrad_Si_Ref_058"])*550
        return df1, df2

#Plotting function
def plotGraph(dataFr1, dataFr2, isc_value, ipeak_value, panelName, company_name):
    plt.figure()
    #norm = mcolors.Normalize(vmin=60, vmax=72)
    with open('weeklyGraphConditions.json', 'r') as f:
        figure_dict = json.load(f)
    for fig_key, fig_value in figure_dict.items():
        plt.scatter(dataFr1['days_on_sun'], dataFr1[fig_key], c=dataFr1[fig_value["map"]], cmap='jet', marker = 'x', s = 20, linewidth=0.5, label = '(850-950)W/m$\mathregular{^2}$')
        plt.scatter(dataFr2['days_on_sun'], dataFr2[fig_key], c=dataFr2[fig_value["map"]], cmap='jet', marker = '+', s = 20, linewidth=0.5, label = '(500-600)W/m$\mathregular{^2}$')

        if fig_key in ("Isc", "Ipeak"):
            x_var = locals().get(f'{fig_key.lower()}_value', None)
            plt.axhline(x_var*0.9, c = 'k', ls = '--', lw = 1.5, label = f'{x_var*0.9:.3f} Amps')
            plt.axhline(x_var*0.55, c = 'brown', ls = '-.', lw = 1.5, label = f'{x_var*0.55:.3f} Amps')
        
        plt.colorbar(label=fig_value["map"])
        plt.legend(loc='upper left', bbox_to_anchor=(-0.1, 1.1), fontsize=8, frameon = False, columnspacing=1.25,handlelength=3, ncols = 4)
        plt.text(0.55, 1.085, fig_key + " Evolution, " + panelName, ha="center", va="bottom", fontsize = 18, fontweight = 'bold', transform=plt.gca().transAxes)
        plt.ylabel(fig_value["label"], fontsize = 15)
        plt.xlabel('Number of Days', fontsize = 15)
        plt.grid('on')
        plt.xticks(rotation='vertical', fontsize = 8)
        plt.tight_layout()
        os.makedirs(f"/Users/user_name/SolarFarm/{company_name}/"+"WeeklyFigures/", exist_ok=True)
        plt.savefig(f'../../../SolarFarm/{company_name}/WeeklyFigures/{fig_key}VSdays{yesterday}-{panelName}.png')
        plt.close()

if yesterday.weekday() == 6:
    #Defining paths
    cleanedFolder = os.path.join(Path.home(), "SolarFarm/XML_Summary_As_CSV/Cleaned/")
    os.makedirs(cleanedFolder, exist_ok=True)

    for com_name, channel_details in full_dict.items():
        file_paths = []
        for channel_no, module_name, panel_area, panel_isc, panel_ipeak in zip(channel_details["channel_nos"], channel_details["module_names"],
                    channel_details["module_area"], channel_details["isc"], channel_details["ipeak"]):
            if module_name in ["Module_1", "Module_2"]: continue
            file_paths.append([f'{cleanedFolder}{channel_no}_{module_name}.csv', module_name, panel_area, panel_isc, panel_ipeak])

        #Calling data cleaning function to generate data frames
        for data_path, panel_name, areal_value, solar_isc, solar_ipeak in file_paths:
            if dataClean(data_path, float(areal_value)) == None:
                continue
            else:
                data1, data2 = dataClean(data_path, float(areal_value))
                plotGraph(data1, data2, float(solar_isc), float(solar_ipeak), panel_name, com_name)
