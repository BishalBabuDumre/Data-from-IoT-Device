import pandas as pd
import matplotlib
matplotlib.use('agg')  # Use Agg backend for non-GUI environments
import matplotlib.pyplot as plt
import numpy as np
import cv2
from io import BytesIO
from PIL import Image
from datetime import date, timedelta

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
    first_frame = plot_graph(df.iloc[0])  # Generate the first plot
    frame_height, frame_width, _ = first_frame.shape

    # Video writer setup
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_video, fourcc, 1.0 / frame_delay, (frame_width, frame_height))

    # Iterate over each row of data and create the plots
    for _, row in df.iterrows():
        frame = plot_graph(row)  # Generate the plot
        video.write(frame)  # Add frame to the video

    video.release()
    print(f"Video saved as {output_video}")

# Function to plot the graph and return it as an OpenCV-compatible frame
def plot_graph(data):
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
    plt.xlim(x[0] - 0.02, x[-1] + 0.05)
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

# Usage
csv_file = f"{yesterday}.csv"  # Your CSV file path
output_video = f"{yesterday}.mp4"  # Name of the output video
create_video_from_plots(csv_file, output_video)
