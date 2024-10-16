##script created by scavengerrr for geofencing a small group of macs

import os
import subprocess
import json
import requests
from geopy.distance import geodesic
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Prerequisites:
# 1. Install CoreLocationCLI: brew install corelocationcli
# 2. Install required Python libraries: pip install requests geopy
# 3. Set up environment variables for API credentials and email password:
#    export JAMF_API_USER="your_api_username"
#    export JAMF_API_PASS="your_api_password"
#    export EMAIL_PASSWORD="your_email_password"

#Informational
#1. This is a manual check in script - you can automate it by setting up using cron

# Jamf Pro API URL and Credentials
JAMF_URL = "yourjamfURL"  # Your Jamf Pro URL
API_USER = os.getenv("JAMF_API_USER", "your_api_username")
API_PASS = os.getenv("JAMF_API_PASS", "your_api_password")

# Approved geofence coordinates (Your University/Location)
APPROVED_LAT = Lat Coordinates
APPROVED_LONG = Long Coordinates
GEOFENCE_RADIUS_MILES = 3.1  #Written in miles, can be changed to KM

# Email settings (set up your SMTP server credentials)
SMTP_SERVER = "smtp.yourmailserver.com"
SMTP_PORT = 587
EMAIL_SENDER = "noreply@yourdomain.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your_email_password")  # Store this securely

# Function to get the current location using CoreLocationCLI
def get_current_location():
    try:
        result = subprocess.run(["CoreLocationCLI", "-json"], capture_output=True, text=True)
        location_data = json.loads(result.stdout)
        current_lat = location_data['latitude']
        current_long = location_data['longitude']
        return current_lat, current_long
    except Exception as e:
        print(f"Error getting location: {e}")
        return None, None

# Function to calculate the distance from the approved geofence in miles
def is_within_geofence(current_lat, current_long, approved_lat, approved_long, radius_miles):
    current_coords = (current_lat, current_long)
    approved_coords = (approved_lat, approved_long)
    distance = geodesic(current_coords, approved_coords).miles  # Distance in miles
    return distance <= radius_miles, distance

# Function to send email notification
def send_email_notification(device_name, current_lat, current_long, distance):
    recipient = "admin@yourdomain.com"  # Set the email recipient
    subject = "Device Outside Geofence Alert"
    
    # Email body content
    body = f"""
    Alert: Device "{device_name}" is outside the geofence.
    Current Location: Latitude {current_lat}, Longitude {current_long}
    Distance from approved location: {distance:.2f} miles.
    """
    
    # Create email message
    message = MIMEMultipart()
    message["From"] = EMAIL_SENDER
    message["To"] = recipient
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    
    try:
        # Set up the SMTP server and send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, recipient, message.as_string())
        print("Email notification sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

# Main function to run the geofencing check
def main():
    # Get the current location
    current_lat, current_long = get_current_location()

    if current_lat is None or current_long is None:
        print("Could not retrieve current location.")
        return

    # Check if the current location is within the geofence
    within_geofence, distance = is_within_geofence(current_lat, current_long, APPROVED_LAT, APPROVED_LONG, GEOFENCE_RADIUS_MILES)

    if within_geofence:
        print(f"Device is within the geofence. Distance from approved location: {distance:.2f} miles.")
    else:
        print(f"Device is OUTSIDE the geofence. Distance from approved location: {distance:.2f} miles.")
        
        # For demonstration, set a device name or retrieve dynamically
        device_name = "MacBook Pro"

        # Send email notification
        send_email_notification(device_name, current_lat, current_long, distance)

# Run the script
if __name__ == "__main__":
    main()
