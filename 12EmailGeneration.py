# Imports
import email, smtplib, ssl
from datetime import date, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
import pandas as pd
import json
import re

# Getting yesterday's date
yester = date.today() - timedelta(days=1)
yesterday = yester.strftime('%Y-%m-%d')

status_file = "ConfigurationFile.csv"

def extract_target_string(path):
    match = re.search(r"([^/]+?)(?=\d{4}-\d{2}-\d{2})", path)
    return match.group(1) if match else None

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

# Function to attach videos
def attach_video(message, video_path, filename):
    try:
        with open(video_path, 'rb') as video_file:
            video = MIMEBase('application', 'octet-stream')
            video.set_payload(video_file.read())
            encoders.encode_base64(video)
            video.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            message.attach(video)
    except FileNotFoundError:
        print(f"Error: {video_path} not found")
    except Exception as e:
        print(f"An error occurred while attaching {video_path}: {e}")

savePath = "/Users/user_name/SolarFarm/"
# File paths for videos

# Function to attach images
def attach_image(message, image_path, content_id):
    try:
        with open(image_path, 'rb') as img_file:
            image = MIMEImage(img_file.read())
            image.add_header('Content-ID', f'<{content_id}>')
            message.attach(image)
    except FileNotFoundError:
        print(f"Error: {image_path} not found")
    except Exception as e:
        print(f"An error occurred while attaching {image_path}: {e}")

def company_channels_dict(status_file):
    df = pd.read_csv(status_file)
    company_channels_dict = {}

    # Step 3: Iterate over each row
    for idx, row in df.iterrows():
        companies = str(row['Company']).strip()
        channel = str(row['Module Name']).strip()       
        
        # Skip rows where Company or Channel is nan or empty
        if companies.lower() == 'nan' or companies == '' or channel.lower() == 'nan' or channel == '':
            continue

        # Step 4: Split multiple companies, strip spaces
        company_list = [c.strip() for c in companies.split(',')]
        
        # Step 5: Add channel to each company in dict
        for company in company_list:
            if company not in company_channels_dict:
                company_channels_dict[company] = []
        
        for key in company_channels_dict:
            if key in company_list:
                company_channels_dict[key].append(channel)

    return company_channels_dict

# Login Details
df = pd.read_csv(status_file)
df = df[df["Email"].notna()]
sender_email = "user_name@gmail.com"
password = os.getenv('GMAIL_PASSWORD')
for index, row in df.iterrows():
    receiver_email = list(json.loads(row['Email']).values())[0]
    company_name = list(json.loads(row['Email']).keys())[0]
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_email)  # Use "To" if you want recipients to see each other
    #message["Bcc"] = ", ".join(receiver_email)  # Or use "Bcc" to hide recipients from each other
    message["Subject"] = "Solar Data for " + company_name

    channel_dict = company_channels_dict(status_file)

    for key, value in channel_dict.items():
        if key == company_name:
            channel_names = value

    video_paths = []
    for name in channel_names:
        video_paths.append((savePath+company_name+f'/Videos/{name}-{yesterday}.mp4', f'iv_curve-{name}.mp4'))

    # Attach videos
    for video_path, filename in video_paths:
        if not os.path.exists(video_path):
            print(f"Warning: File {filename} not found. Skipping...")
        else:
            attach_video(message, video_path, filename)

    # List of images to attach
    image_paths_and_ids = []
    image_prefix = ["Irr", "Temp", "Ffac", "Ipeak", "Immax", "Imax", "Ppeak", "Vpeak", "Vmax", "Isc", "Voc", "ISCandVOC", "Wind", "Hum", "SerRes"]
    count = 1
    for prefix in image_prefix:
        image_paths_and_ids.append((savePath+company_name+f'/Temp&Irr&Wind&Hum/{prefix}{yesterday}.png', f'image{count}'))
        count+=1

    # Attach additional weekly images if it's Saturday
    if yester.weekday() == 6:
        weekly_images_paths_and_ids = []
        image_prefix_weekly = ["IscVSdays", "IpeakVSdays", "VocVSdays", "VpeakVSdays", "EfficiencyVSdays", "PeakPowerVSdays"]
        for name in channel_names:
            if any(x in name for x in ["Module_1", "Module_2"]): continue
            for prefix_weekly in image_prefix_weekly:
                weekly_images_paths_and_ids.append((savePath+company_name+f'/WeeklyFigures/{prefix_weekly}{yesterday}-{name}.png', f'image{count}'))
                count+=1
        image_paths_and_ids.extend(weekly_images_paths_and_ids)
    
    image_html = ""
    added_images = set()
    for name in channel_names:
        if any(x in name for x in ["Module_1", "Module_2"]): continue
        with open('emailConditions.json', 'r') as f:
            prefix_dict = json.load(f)
            prefix_dict = replace_in_dict(prefix_dict, "{sample}", name)     
        for img in image_paths_and_ids:
            img_count = img[1][5:]
            if img_count in added_images: continue   
            key = extract_target_string(img[0])
            if key and key in prefix_dict.keys():
                desc = prefix_dict[key]
                image_html+=f'<img src="cid:image{img_count}"/><p><strong>Figure{img_count}: </strong>{desc}</p>'
            added_images.add(img_count)
        prefix_dict = replace_in_dict(prefix_dict, name, "{sample}")

    # HTML email writeup
    body = f"""<html><head></head><body>
    <p><strong>Dear Someone,</strong></p>
    <p>This is an email from yesterday's <b>({yesterday})</b> solar performance.</p>
    <p>Please find the images below:</p>
    <p>Yours,<br><strong>MT5</strong></p>
    {image_html}
    </body></html>
    """
    #print(image_html)

    # Add body to email
    message.attach(MIMEText(body, "html"))

    # Attach all images
    for image_path, content_id in image_paths_and_ids:
        attach_image(message, image_path, content_id)

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())