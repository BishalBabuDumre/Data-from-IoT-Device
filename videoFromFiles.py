import cv2
import os
import re


# Helper function to sort file names with numbers properly
def natural_sort_key(s):
    # This will split strings by digits to allow numerical sorting
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def create_video_from_images(folder_path, output_video, frame_delay=0.3):
    # Get all the PNG files from the folder
    images = [img for img in os.listdir(folder_path) if img.endswith(".png")]
    images.sort(key=natural_sort_key)  # Sort the images alphabetically or by number

    if not images:
        print("No PNG files found in the folder.")
        return

    # Load the first image to get the frame size
    first_image_path = os.path.join(folder_path, images[0])
    frame = cv2.imread(first_image_path)
    height, width, layers = frame.shape

    # Define the video codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'mp4v' for .mp4 output
    video = cv2.VideoWriter(output_video, fourcc, 1.0 / frame_delay, (width, height))

    # Loop over all images and add them to the video
    for image in images:
        image_path = os.path.join(folder_path, image)
        frame = cv2.imread(image_path)

        # Check if the frame was loaded successfully
        if frame is None:
            print(f"Failed to load image {image}")
            continue

        video.write(frame)  # Add frame to the video

    # Release the video writer object
    video.release()
    print(f"Video saved as {output_video}")

# Usage example
folder_path = 'IV'  # Folder containing PNG files
output_video = 'output_video.mp4'  # Output video file name
create_video_from_images(folder_path, output_video)
