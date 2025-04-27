import os
from datetime import date
import pandas as pd
from pathlib import Path

today = date.today()
today = today.strftime("%m%d%Y")
print("Today's date:", today)
# inputting the date here appends the file name on each of the generated images.
Date_Report_Generated = str(today) # format MMDDYYYY

pd.options.mode.chained_assignment = None  # default = 'warn'

savePath = os.path.join(Path.home(), "SolarFarm/XML_Summary_As_CSV")

indoorMeasurements = pd.read_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ConfigurationFile.csv"))
cleanedFolder = os.path.join(savePath, "Cleaned")
os.makedirs(cleanedFolder, exist_ok=True)

processedFiles = os.listdir(savePath)

for file in processedFiles:
	if not ".csv" in file: #Means do not care folders
		continue
	channel = file[:-4]
	df = pd.read_csv(os.path.join(savePath, file))
	names = df["Name"].unique()
	for name in names:
		indoor = indoorMeasurements.query(f"`Module Name` == '{name}'")
		if indoor.empty:
			print("{name} not found in existing indoor measurements! skipping channel {channel}".format(name=name, channel=channel))
			continue
		else:
			print(f"{name} found, processing!!!")
		indoorPmp = indoor["Pmax (W)"].iloc[0]

		df = df.query("Name == '{name}'".format(name=name))
		# format date
		df["date"] = df["Date_Time"].str[:10]
		df["hour_of_day"] = df["Date_Time"].str[11:13]
		df["datetime"] = pd.to_datetime(df.Date_Time, format="%Y-%m-%dT%H:%M:%S")
		day1 = pd.to_datetime(indoor['Starting Date and Time'].iloc[0])

		df["days_on_sun"] = (df["datetime"] - day1).dt.total_seconds() / 86400
		#df = df.query("date >= '2021-10-30' and date <= '2025-12-31'")
		
		if file!="Keithley.csv":
			df["Si_ref_058_delta"] = (
				df["Irradiance_after_Irrad Si-Ref 058"]
				- df["Irradiance_before_Irrad Si-Ref 058"]
			)

			df = df.query("-3 < Si_ref_058_delta < 3")
			df["peak_power"] = df["Calculated_Imp"] * df["Calculated_Vmp"]
			df["Irrad_Si_Ref_058"] = df["Irradiance_before_Irrad Si-Ref 058"]
			df["Calculated_FF"] = (
				df["Calculated_Imp"] * df["Calculated_Vmp"]
			) / (df["Calculated_Isc"] * df["Calculated_Voc"])
			df = df.query("0 < Calculated_FF < 1.1")


			# Isc normalized and corrected to 1 Sun
			df["normalized_corrected_Isc"] = (df["Calculated_Isc"] / indoor["Isc (A)"].iloc[0]) * (
				1000 / df["Irrad_Si_Ref_058"]
			)

			# Imp normalized and corrected to 1 Sun
			df["normalized_corrected_Imp"] = (df["Calculated_Imp"] / indoor["Isc (A)"].iloc[0]) * (
				1000 / df["Irrad_Si_Ref_058"]
			)

			# Peak Power normalized and corrected to 1 Sun
			df["normalized_corrected_PeakPower"] = (df["peak_power"] / indoorPmp) * (
				1000 / df["Irrad_Si_Ref_058"]
			)

			# Voc and Vmp normalized
			df["normalized_Voc"] = df["Calculated_Voc"] / indoor["Voc (V)"].iloc[0]
			df["normalized_Calculated_Vmp"] = df["Calculated_Vmp"] / indoor["Voc (V)"].iloc[0]
			df = df.query("0 < Irrad_Si_Ref_058 < 1300")	

		# Test1 is Channel 102 is 8MB21_PK
		df.to_csv(os.path.join(cleanedFolder, "{channel}_{name}.csv".format(channel=channel, name=name)))
