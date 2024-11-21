#Imports
import os
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import date
from datetime import timedelta

#Creating Bold Graph Edges and Fonts
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"
plt.rcParams["axes.linewidth"] = 1.5
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.titlesize"] = 14

#Data clean function that generates two data frames for plotting
def dataClean(fileRoad):
    df = pd.read_csv(fileRoad)

    df["Si_ref_058_delta"] = (df["Irradiance_after_Irrad Si-Ref 058"]
	                		- df["Irradiance_before_Irrad Si-Ref 058"])

    df = df.query("-3 < Si_ref_058_delta < 3").copy()
    df = df.query("days_on_sun > 0").copy()
    df = df.query("0 < FillFactor < 100").copy()

    df.loc[:, "Irrad_Si_Ref_058"] = df["Irradiance_before_Irrad Si-Ref 058"]
    df.loc[:, 'Efficiency'] = (df['PeakPower'] / df["Irrad_Si_Ref_058"]) / 0.00022046

    df1 = df.query('850 < Irrad_Si_Ref_058 < 950').copy()
    df2 = df.query('500 < Irrad_Si_Ref_058 < 600').copy()
    return df1, df2

#Plotting function
def plotGraph(dataFr1, dataFr2, dateY, panelName, value, unit, map):
    plt.figure()
    plt.scatter(dataFr1['days_on_sun'], dataFr1[value], c=dataFr1[map], cmap='jet', marker = 'x', s = 20, linewidth=0.5, label = '(850-950)W/m$\mathregular{^2}$')
    plt.scatter(dataFr2['days_on_sun'], dataFr2[value], c=dataFr2[map], cmap='jet', marker = '+', s = 20, linewidth=0.5, label = '(500-600)W/m$\mathregular{^2}$')
    #plt.scatter(df1['days_on_sun'], df1['Eff'], c='b', marker = 'x', s = 20, linewidth=0.5, label = '(850-950)W/m$\mathregular{^2}$')
    #plt.scatter(df2['days_on_sun'], df2['Eff'], c='r', marker = '+', s = 20, linewidth=0.5, label = '(500-600)W/m$\mathregular{^2}$')
    if map in ("Temperature_T", "Temperature_R"): map = "Temperature of Module"
    if map == "FillFactor": map = "Fill Factor"
    plt.colorbar(label=map)
    plt.legend(loc='upper left', bbox_to_anchor=(0.15, 1.1), fontsize=8, frameon = False, columnspacing=1.25,handlelength=3, ncols = 2)
    plt.text(0.55, 1.085, value + " Evolution over Time, " + panelName, ha="center", va="bottom", fontsize = 19, fontweight = 'bold', transform=plt.gca().transAxes)
    plt.ylabel(value + " " + unit, fontsize = 15)
    plt.xlabel('Number of Days', fontsize = 15)
    plt.grid('on')
    plt.xticks(rotation='vertical', fontsize = 8)
    plt.tight_layout()
    plt.savefig('../../../SolarFarm/WeeklyFigures/'+value+'VSdays'+panelName+str(dateY)+map[:4]+'.png')
    plt.close()

#Getting yesterday's date
yesterday = date.today() - timedelta(days = 1)

if yesterday.weekday() == 5:
    #Defining paths
    cleanedFolder = os.path.join(Path.home(), "SolarFarm/XML_Summary_As_CSV/Cleaned")
    os.makedirs(cleanedFolder, exist_ok=True)

    filePath1 = os.path.join(cleanedFolder, "112_3.csv")
    filePath2 = os.path.join(cleanedFolder, "106_4.csv")
    filePath3 = os.path.join(cleanedFolder, "107_3.csv")
    filePath4 = os.path.join(cleanedFolder, "109_4.csv")

    #Calling data cleaning function to generate data frames
    SW3data11, SW3data21 = dataClean(filePath1)
    SW3data12, SW3data22 = dataClean(filePath3)
    SW3data1 = pd.concat([SW3data11, SW3data12], ignore_index=True)
    SW3data2 = pd.concat([SW3data21, SW3data22], ignore_index=True)
    SW4data11, SW4data21 = dataClean(filePath2)
    SW4data12, SW4data22 = dataClean(filePath4)
    SW4data1 = pd.concat([SW4data11, SW4data12], ignore_index=True)
    SW4data2 = pd.concat([SW4data21, SW4data22], ignore_index=True)

    #Getting string value of yesterday
    yester = yesterday.strftime('%Y-%m-%d')

    #Calling final plotting function
    plotGraph(SW3data1, SW3data2, yester, "SW3", "Efficiency", "(%)", "FillFactor")
    plotGraph(SW4data1, SW4data2, yester, "SW4", "Efficiency", "(%)", "FillFactor")
    plotGraph(SW3data1, SW3data2, yester, "SW3", "Voc", "(V)", "FillFactor")
    plotGraph(SW4data1, SW4data2, yester, "SW4", "Voc", "(V)", "FillFactor")
    plotGraph(SW3data1, SW3data2, yester, "SW3", "PeakPower", "(W)", "FillFactor")
    plotGraph(SW4data1, SW4data2, yester, "SW4", "PeakPower", "(W)", "FillFactor")
    plotGraph(SW3data1, SW3data2, yester, "SW3", "Vpeak", "(V)", "FillFactor")
    plotGraph(SW4data1, SW4data2, yester, "SW4", "Vpeak", "(V)", "FillFactor")
    plotGraph(SW3data1, SW3data2, yester, "SW3", "Ipeak", "(A)", "FillFactor")
    plotGraph(SW4data1, SW4data2, yester, "SW4", "Ipeak", "(A)", "FillFactor")
    plotGraph(SW3data1, SW3data2, yester, "SW3", "Isc", "(A)", "FillFactor")
    plotGraph(SW4data1, SW4data2, yester, "SW4", "Isc", "(A)", "FillFactor")
    plotGraph(SW3data1, SW3data2, yester, "SW3", "Efficiency", "(%)", "Temperature_T")
    plotGraph(SW4data1, SW4data2, yester, "SW4", "Efficiency", "(%)", "Temperature_R")
    plotGraph(SW3data1, SW3data2, yester, "SW3", "Voc", "(V)", "Temperature_T")
    plotGraph(SW4data1, SW4data2, yester, "SW4", "Voc", "(V)", "Temperature_R")
    plotGraph(SW3data1, SW3data2, yester, "SW3", "PeakPower", "(W)", "Temperature_T")
    plotGraph(SW4data1, SW4data2, yester, "SW4", "PeakPower", "(W)", "Temperature_R")
    plotGraph(SW3data1, SW3data2, yester, "SW3", "Vpeak", "(V)", "Temperature_T")
    plotGraph(SW4data1, SW4data2, yester, "SW4", "Vpeak", "(V)", "Temperature_R")
    plotGraph(SW3data1, SW3data2, yester, "SW3", "Ipeak", "(A)", "Temperature_T")
    plotGraph(SW4data1, SW4data2, yester, "SW4", "Ipeak", "(A)", "Temperature_R")
    plotGraph(SW3data1, SW3data2, yester, "SW3", "Isc", "(A)", "Temperature_T")
    plotGraph(SW4data1, SW4data2, yester, "SW4", "Isc", "(A)", "Temperature_R")