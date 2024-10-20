import csv
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
import cv2
from io import BytesIO
from PIL import Image

#Creating Bold Graph Edges and Fonts
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"
plt.rcParams["axes.linewidth"] = 1.5
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.titlesize"] = 14

# OpenCV video setup
def create_video_from_plots(csv_file, output_video, frame_delay=0.3):
    # Open the CSV file for reading
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        data_list = []
        for row in csv_reader:
            data_list.append(row)
    
    # Get the first plot to determine the video frame size
    plt.figure(figsize=(7,5))
    first_frame = plot_graph(data_list[0])  # Generate the first plot
    frame_height, frame_width, _ = first_frame.shape

    # Video writer setup
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_video, fourcc, 1.0 / frame_delay, (frame_width, frame_height))

    # Iterate over each row of data and create the plots
    for data in data_list:
        frame = plot_graph(data)  # Generate the plot
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
csv_file = '2024-09-25.csv'  # Your CSV file
output_video = 'output_video.mp4'  # Name of the output video
create_video_from_plots(csv_file, output_video)
