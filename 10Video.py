import pandas as pd
import matplotlib
matplotlib.use('agg')  # Use Agg backend for non-GUI environments
import matplotlib.pyplot as plt
import numpy as np
import cv2
from io import BytesIO
from PIL import Image
from datetime import date, timedelta
import os
import json

# Set global plot properties
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"
plt.rcParams["axes.linewidth"] = 1.5
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.titlesize"] = 14

# Get yesterday's date
yesterday = date.today() - timedelta(days=1)
yesterday = yesterday.strftime('%Y-%m-%d')

# OpenCV video setup
def create_video_from_plots(csv_file, output_video, frame_delay=0.3):
    # Read CSV using pandas and sort by 'Date_Time'
    df = pd.read_csv(csv_file)
    df = df.sort_values(by="Date_Time", ascending=True)  # Sort by 'Date_Time' column

    # Get the first plot to determine the video frame size
    plt.figure(figsize=(7, 5))
    first_frame = plot_graph(df.iloc[0], csv_file)  # Generate the first plot
    frame_height, frame_width, _ = first_frame.shape

    # Video writer setup
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_video, fourcc, 1.0 / frame_delay, (frame_width, frame_height))

    # Iterate over each row of data and create the plots
    for _, row in df.iterrows():
        frame = plot_graph(row, csv_file)  # Generate the plot
        video.write(frame)  # Add frame to the video

    video.release()
    print(f"Video saved as {output_video}")

def yLim(dataCSV):
    values = []
    dff = pd.read_csv(dataCSV)
    for i in dff["amps_curve"]:
        i = max(list(map(float, i[1:-1].split(","))))
        values.append(i)
    return max(values)

# Function to plot the graph and return it as an OpenCV-compatible frame
def plot_graph(data, fileCSV):
    pv = float(data["Vpeak"])
    pc = float(data["Ipeak"])
    c = float(data["Isc"])
    v = float(data["Voc"])
    x = data["volts_curve"]
    y = data["amps_curve"]
    z = data["Date_Time"]
    n = data["Name"]

    x = list(map(float, x[1:-1].split(",")))
    y = list(map(float, y[1:-1].split(",")))

    plt.clf()  # Clear the current figure to avoid overlaps
    plt.plot(x, y, c='k')
    plt.plot(0, c, c='b', marker='o', markersize=20)
    plt.plot(v, 0, c='g', marker='X', markersize=20)
    plt.plot(pv, pc, c='r', marker='P', markersize=20)
    plt.title(f"{n}, {z}")
    plt.xlim(-0.05, x[-1] + 0.07)
    plt.ylim(yLim(fileCSV)*(-0.1),yLim(fileCSV)+(yLim(fileCSV)*0.1))
    plt.xlabel("Voltage (V)")
    plt.ylabel("Current in Circuit (A)")

    # Convert the plot to a PIL image in memory
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = Image.open(buf)

    # Convert PIL image to OpenCV format (BGR)
    img = np.array(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    return img

status_file = "ConfigurationFile.csv"

def company_channels_dict(status_file):
    df = pd.read_csv(status_file)
    company_channels_dict = {}

    # Step 3: Iterate over each row
    for idx, row in df.iterrows():
        companies = str(row['Company']).strip()
        channel = str(row['Channel #']).strip()
        module = str(row['Module Name']).strip()       
        
        # Skip rows where Company or Channel is nan or empty
        if companies.lower() == 'nan' or companies == '' or channel.lower() == 'nan' or channel == '':
            continue

        # Step 4: Split multiple companies, strip spaces
        company_list = [c.strip() for c in companies.split(',')]
        
        # Step 5: Add channel to each company in dict
        for company in company_list:
            if company not in company_channels_dict:
                company_channels_dict[company] = {"channel_nos" : [], "module_names" : []}
        
        for key in company_channels_dict:
            if key in company_list:
                company_channels_dict[key]["channel_nos"].append(channel)
                company_channels_dict[key]["module_names"].append(module)

    return company_channels_dict

full_dict = company_channels_dict(status_file)
for company in full_dict:
    for idx, channel_no in enumerate(full_dict[company]["channel_nos"]):
        csv_file = f"../../../SolarFarm/XML_Summary_As_CSV/{channel_no}/{yesterday}.csv"  # Your CSV file path
        if not os.path.exists(csv_file):
            print(f"Warning: File {csv_file} not found. Skipping...")
        else:
            os.makedirs(f"/Users/user_name/SolarFarm/{company}/"+"Videos/", exist_ok=True)
            output_video1 = f"/Users/user_name/SolarFarm/{company}/Videos/{full_dict[company]['module_names'][idx]}-{yesterday}.mp4"  # Name of the output video
            create_video_from_plots(csv_file, output_video1)