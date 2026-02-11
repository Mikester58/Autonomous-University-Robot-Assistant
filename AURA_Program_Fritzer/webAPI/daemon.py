import requests
import time
import os

#SERVER_URL = GET FROM MUHAMMED
DOWNLOAD_PATH = "/home/jetson/incoming_files"
last_downloaded = None

while True:
    try:
        # 1. Ask the server if there is a new file
        response = requests.get(f"{SERVER_URL}/check-for-files")
        status = response.json()
        
        filename = status.get("filename")
        
        # 2. If there is a new file we haven't seen yet, download it
        if filename and filename != last_downloaded:
            print(f"New file detected: {filename}. Downloading...")
            
            file_data = requests.get(f"{SERVER_URL}/download/{filename}")
            
            with open(os.path.join(DOWNLOAD_PATH, filename), 'wb') as f:
                f.write(file_data.content)
            
            last_downloaded = filename
            print("Download complete.")

    except Exception as e:
        print(f"Connection error: {e}")

    time.sleep(10) # Wait 10 seconds before checking again