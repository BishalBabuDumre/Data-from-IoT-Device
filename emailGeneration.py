#Imports
import email, smtplib, ssl
from datetime import date
from datetime import timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

#Getting yesterday's date
yesterday = date.today() - timedelta(days = 1)
yesterday = yesterday.strftime('%Y-%m-%d')

#HTML email writeup
body = """<html><head></head><body><p><strong>Dr. ABCD,</strong></p>
<p>This is an email from yesterday's <b>("""+yesterday+""")</b> solar performance.</p>
<p>Please find the images below:</p>
<p>Yours,<br><strong>IoT Device</strong></p>
<img src="cid:image1" /><p><strong>Figure 1:</strong> Irradiance VS Time of the Day</p>
<img src="cid:image2" /><p><strong>Figure 2:</strong> Temperature VS Time of the Day</p>
</body></html>"""

#Login Details
sender_email = "abc123@gmail.com"
receiver_email = ["abc123@gmail.com", "abc123@gmail.com"]
password = "xxxxxxxxxxxxxxxxxxxx"

# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = sender_email
message["Bcc"] = ", ".join(receiver_email)
message["Subject"] = "Meteorological Data"

# Add body to email
message.attach(MIMEText(body, "html"))

# We assume that the image file is in the same directory that you run your Python script from
fp1 = open('../../../Project/XML_Summary/Temp&Irr/Temp'+str(yesterday)+'.png', 'rb')
image1 = MIMEImage(fp1.read())
fp1.close()

# Specify the  ID according to the img src in the HTML part
image1.add_header('Content-ID', '<image1>')
message.attach(image1)

# We assume that the image file is in the same directory that you run your Python script from
fp2 = open('../../../Project/XML_Summary/Temp&Irr/Irr'+str(yesterday)+'.png', 'rb')
image2 = MIMEImage(fp2.read())
fp2.close()

# Specify the  ID according to the img src in the HTML part
image2.add_header('Content-ID', '<image2>')
message.attach(image2)

# Log in to server using secure context and send email
context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
