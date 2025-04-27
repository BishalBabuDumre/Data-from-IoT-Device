#Imports
import matplotlib
matplotlib.use('agg')
from matplotlib import pyplot as plt
import pandas as pd
from datetime import date
from datetime import datetime
from datetime import timedelta
import numpy as np
import json
import os

#Creating Bold Graph Edges and Fonts
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"
plt.rcParams["axes.linewidth"] = 1.5

#Getting yesterday's date
yesterday = date.today() - timedelta(days = 1)
yesterday = yesterday.strftime('%Y-%m-%d')

# Recursive function to replace {date} in both keys and values of nested dictionaries
def replace_in_dict(d, replaced, replacer):
    new_dict = {}
    for key, value in d.items():
        new_key = key.replace(replaced, replacer)
        # If value is a dictionary, recurse
        if isinstance(value, dict):
            new_value = replace_in_dict(value, replaced, replacer)
        # If value is a string, replace {date} in the value
        elif isinstance(value, str):
            new_value = value.replace(replaced, replacer)
        else:
            new_value = value  # Leave other types unchanged (int, bool, etc.)
        new_dict[new_key] = new_value
    return new_dict

#Sort the CSV
def sort_csv(input_file, sort_column):
    df = pd.read_csv(input_file) # Read the CSV file into a DataFrame
    df_sorted = df.sort_values(by=sort_column) # Sort the DataFrame based on the specified column
    return df_sorted

#Extract only Times from the DateTime

def exTime(dateTime):
    time_list = []
    for original_string in dateTime:
        selected_section = original_string[11:16]
        time_list.append(selected_section)
    return time_list

business_requirement_file = "ConfigurationFile.csv"
#Function to develop a dictionary of all the variables associated with the channels.
def develop_dict(channels_list):
    yesterday = date.today() - timedelta(days = 1)
    yesterday = yesterday.strftime('%Y-%m-%d')
    sort_col = 'Date_Time'  # Specify the column you want to sort by
    variables_dict = {}
    norm_dict = {}
    for channel in channels_list.split(', '):
        channel_file = f"../../../SolarFarm/XML_Summary_As_CSV/{channel}/{yesterday}.csv"
        if not os.path.exists(channel_file):
            print(f"Warning: File {channel_file} not found. Skipping...")
        else:
            #Getting some data in the dictionary from Configuration File.
            df1 = pd.read_csv(business_requirement_file)
            keys1 = ["Vmax", "Pmax", "Imax", "Voc", "Isc"]
            cols1 = ["Vmp (V)", "Pmax (W)", "Imp (A)", "Voc (V)", "Isc (A)"]
            norm_dict.update(dict(zip(keys1, df1.loc[df1['Channel #'] == channel, cols1].values[0])))
            norm_dict["Irr"] = '1000'
            norm_dict["One"] = '1'
            norm_dict["imaxBYirr"] = df1.loc[df1['Channel #'] == channel, 'Imp (A)'].values[0]/1000
            variables_dict['norm'] = norm_dict
            variables_dict['sample_name'] = df1.loc[df1['Channel #'] == channel, 'Module Name'].values[0]
            if channel != "Keithley":
                #Getting data from the MTD file.
                yesterday = date.today() - timedelta(days = 1)
                yesterday = yesterday.strftime('%m%d%Y')
                mtd_file = f"../../../SolarFarm/MTDlocal/mt{yesterday}.mtd"
                df2 = pd.read_csv(mtd_file)
                variables_dict['vmax_mtd'] = df2[channel + ' Volts'].iloc[2:].astype(float).tolist()
                variables_dict['pmax_mtd'] = df2[channel + ' Power'].iloc[2:].astype(float).tolist()
                df2.loc[2:, 'ImaxByIrr'] = df2.loc[2:, channel + ' Amps'].astype(float)/df2.loc[2:, "6 Aux"].astype(float)
                variables_dict['imax_by_irr_mtd'] = df2['ImaxByIrr'].tolist()[2:]
                variables_dict["time_of_day_mtd"] = df2['Time'].str[:5].tolist()[2:]
            #Getting data from the daily CSV file.
            sorted = sort_csv(channel_file, sort_col)
            dateTime = sorted["Date_Time"].tolist() #LG Date and Time
            time = exTime(dateTime)
            variables_dict['time_of_day'] = time
            if "Irradiance_after_Irrad Si-Ref 061" in sorted.columns:
                imaxIrr = (sorted["Ipeak"]/sorted["Irradiance_after_Irrad Si-Ref 061"]).tolist()
                variables_dict['imax_by_irr'] = imaxIrr
            with open("column_map.json", "r") as file:
                column_map = json.load(file)
            variables_dict.update({v: sorted[k].tolist() for k, v in column_map.items() if k in sorted.columns})
            temp_count = 1 
            for column in sorted.columns:
                if column.startswith("Temperature_") and column not in ["Temperature_Ambient", "Temperature_Top of MT"]:
                    key = f'temp_{temp_count}_xml'
                    variables_dict[key] = sorted[column].tolist()
                    temp_count += 1
    return variables_dict

yesterday = date.today() - timedelta(days = 1)
yesterday = yesterday.strftime('%Y-%m-%d')

#Defining normalizer function
def normalize(list_to_norm, normalizer_value): #Normalizing various variables
    norm_list = []
    for j in list_to_norm:
        if type(j) == str:
            return list_to_norm
            break
        else:
            j = j/normalizer_value
        norm_list.append(j)
    return norm_list

#Defining plot function.
def plot_graphs(all_data_dict):
    colr = ["r", "b", "g", "k", "cyan", "brown", "orange", "teal", "magenta", "olive", '#AA336A']
    l_s = ["-", "--", ":", "-.", (0, (5, 5)), (0, (3, 1, 1, 1, 1, 1)), (0, (3, 1, 1, 1)), (0, (10, 5)), (0, (3, 3)), (0, (2, 2)), (0, (4, 1, 2, 1, 2, 1))]
    with open('graphConditions.json', 'r') as f:
        figure_dict = json.load(f)
        figure_dict = replace_in_dict(figure_dict, "{yesterday}", yesterday)      
    for company_name, module_info in all_data_dict.items():
        for fig_key, fig_value in figure_dict.items():
            count = 0
            fig, ax = plt.subplots()
            if fig_value.get('twin') == "True":
                ax2 = ax.twinx()
            for idx, (sample_channel_no, all_variables) in enumerate(module_info.items()):
                if all_variables == {}: continue                                               
                fig_value = replace_in_dict(fig_value, '{sample_name}', all_variables['sample_name'])
                if fig_value.get('twin') == "True" and all_variables['sample_name'] in ["LG", "SunPower"]:
                    for k3, v3 in fig_value["y"]["var"].items():
                        x_var = all_variables[list(fig_value["x"]["var"].values())[0]]
                        y_var = normalize(all_variables[v3["val"]], float(all_variables["norm"][v3["norm"]]))
                        if not all_variables.get(v3["val"], False):continue
                        ax2.plot(x_var, y_var, c=colr[count], ls=l_s[count], lw=1.5, label=k3)
                        count += 1
                    # Set y-axis label once
                    ax2.set_ylabel(fig_value["y"]["label"], fontsize=14)
                    # Add legend once after plotting all lines
                    ax2.legend(fontsize=8, facecolor='none', frameon=False, loc = 'upper left')
                    fig_value = replace_in_dict(fig_value, all_variables.get('sample_name'), '{sample_name}')
                    continue
                for k3, v3 in fig_value["y"]["var"].items():
                    if (idx > 0) and (v3["val"] in ['ambient_temp_xml', 'mt5_temp_xml', 'pyro_CMP3_xml', 'pyro_7F3_xml',
                    'si_ref_061_xml', 'si_ref_058_xml']): continue
                    if not all_variables.get(v3["val"], False): continue
                    if (idx > 1) and (v3["val"] in ["wind_speed_xml", "humidity_xml"]): continue
                    if fig_value.get('twin') == "True" and all_variables['sample_name'] in ["Company_1", "Company_2"]: continue
                    x_var = all_variables[list(fig_value["x"]["var"].values())[0]]
                    y_var = normalize(all_variables[v3["val"]], float(all_variables["norm"][v3["norm"]]))
                    if list(fig_value["x"]["var"].values())[0] in ('time_of_day', 'time_of_day_mtd'):
                        x_var = [datetime.strptime(t, "%H:%M") for t in all_variables[list(fig_value["x"]["var"].values())[0]]]
                    ax.plot(x_var, y_var, c = colr[count], ls = l_s[count], lw = 1.5, label = k3)
                    count+=1
                fig_value = replace_in_dict(fig_value, all_variables.get('sample_name'), '{sample_name}')
            ax.legend(fontsize = 8, facecolor='none', frameon=False)
            ax.set_xlabel(list(fig_value["x"]["var"].keys())[0], fontsize = 14)
            plt.grid('on')
            if fig_value['y'].get('limit'):
                ax.set_ylim(fig_value['y']['limit'][0], fig_value['y']['limit'][1])
            if fig_value['x'].get('limit'):
                ax.set_ylim(fig_value['x']['limit'][0], fig_value['x']['limit'][1])
            plt.xticks(rotation='vertical', fontsize = 8)
            plt.title(fig_key, fontsize = 16, fontweight = "bold")
            ax.set_ylabel(fig_value["y"]["label"], fontsize = 14)
            if list(fig_value["x"]["var"].values())[0] in ('time_of_day', 'time_of_day_mtd'):
                ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
            plt.tight_layout()
            os.makedirs(f"/Users/user_name/SolarFarm/{company_name}/"+"Temp&Irr&Wind&Hum/", exist_ok=True)
            plt.savefig(f"/Users/user_name/SolarFarm/{company_name}/"+"Temp&Irr&Wind&Hum/"+fig_value["file_name"]+f"{yesterday}.png")
            plt.close()
    return None
#Defining the main function.
def main(status_file):
    df = pd.read_csv(status_file)
    company_channels_dict = {}

    # Step 3: Iterate over each row
    for idx, row in df.iterrows():
        companies = str(row['Company']).strip()
        channel = str(row['Channel #']).strip()
        
        # Skip rows where Company or Channel is nan or empty
        if companies.lower() == 'nan' or companies == '' or channel.lower() == 'nan' or channel == '':
            continue

        # Step 4: Split multiple companies, strip spaces
        company_list = [c.strip() for c in companies.split(',')]
        
        # Step 5: Add channel to each company in dict
        for company in company_list:
            if company not in company_channels_dict:
                company_channels_dict[company] = {}
            
        for company in company_list:
            company_channels_dict[company][channel.split(".")[0]] = develop_dict(channel.split(".")[0])

    #print(company_channels_dict)

    plot_graphs(company_channels_dict)
    return None

#Bringing status of the system.
final_implementation = main(business_requirement_file)
savePath = "/Users/user_name/SolarFarm/"