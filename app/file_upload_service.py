"""
File Upload Service (OOP versie)
Beheert uploaden, downloaden en ophalen van bestanden via Nextcloud.
"""

import os
import requests
from flask import current_app
from requests.auth import HTTPBasicAuth
from werkzeug.utils import secure_filename
from urllib.parse import quote, unquote
import xml.etree.ElementTree as ET


class FileUploadService:
    def __init__(self):
        self.server_url = current_app.config['NEXTCLOUD_SERVER_URL']
        self.username = current_app.config['NEXTCLOUD_USERNAME']
        self.password = current_app.config['NEXTCLOUD_PASSWORD']
        self.folder = current_app.config['NEXTCLOUD_FOLDER']

        self.upload_folder = current_app.config.get('UPLOAD_FOLDER', 'app/static/uploads')

        self.allowed_extensions = {
            'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx',
            'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', 'mp4', 'mp3', 'wav'
        }

        self.max_file_size = 100 * 1024 * 1024  # 100 MB

    # ---------------------------------------------------
    # Helpers
    # ---------------------------------------------------

    def _auth(self):
        return HTTPBasicAuth(self.username, self.password)

    def _build_url(self, filename=""):
        if filename:
            encoded = quote(filename, safe='')
            return f"{self.server_url}/remote.php/dav/files/{self.username}/{self.folder}/{encoded}"
        else:
            # Voor folder listing moet URL eindigen met /
            return f"{self.server_url}/remote.php/dav/files/{self.username}/{self.folder}/"

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    # ---------------------------------------------------
    # LIST FILES
    # ---------------------------------------------------

    def list_files(self):
        """Haal bestandenlijst op van Nextcloud."""
        try:
            url = self._build_url()  # Geeft folder URL met trailing /
            print(f"DEBUG: list_files() called - URL: {url}")
            
            response = requests.request(
                "PROPFIND",
                url,
                auth=self._auth(),
                headers={"Depth": "1"},
                timeout=30  # Verhoogd van 10 naar 30 seconden
            )

            print(f"DEBUG: PROPFIND response status: {response.status_code}")

            if response.status_code != 207:
                print(f"PROPFIND failed with status {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return []

            root = ET.fromstring(response.text)
            files = []
            
            # Expected folder path (can be in href as full URL or just path)
            folder_path_pattern = f"/remote.php/dav/files/{self.username}/{self.folder}/"
            print(f"DEBUG: Looking for files in folder pattern: {folder_path_pattern}")

            for elem in root.findall(".//{DAV:}response"):
                href = elem.find(".//{DAV:}href")
                if href is not None and href.text:
                    # Decode URL-encoded characters
                    decoded_href = unquote(href.text)
                    
                    # Skip if it's a directory (ends with /)
                    if decoded_href.endswith('/'):
                        print(f"DEBUG: Skipping directory: {decoded_href}")
                        continue
                    
                    # Check if this file is in our target folder
                    # href can be full URL or just path, so check for folder pattern
                    if folder_path_pattern in decoded_href:
                        # Get just the filename (last part after /)
                        filename = decoded_href.split('/')[-1]
                        
                        # Skip empty names
                        if filename:
                            files.append(filename)
                            print(f"DEBUG: Added file: {filename}")

            print(f"DEBUG: Total files found: {len(files)} - {files}")
            return files

        except requests.exceptions.Timeout as e:
            print(f"Timeout error listing files: {e}")
            print("Nextcloud server reageert te traag. Probeer het later opnieuw.")
            return []
        except requests.exceptions.RequestException as e:
            print(f"Network error listing files: {e}")
            return []
        except Exception as e:
            print("Error listing files:", e)
            import traceback
            traceback.print_exc()
            return []

    # ---------------------------------------------------
    # DOWNLOAD
    # ---------------------------------------------------

    def download_file(self, filename):
        try:
            url = self._build_url(filename)
            response = requests.get(url, auth=self._auth(), timeout=30)

            if response.status_code == 200:
                return response.content

            print("Download failed:", response.status_code)
            return None

        except Exception as e:
            print("Error downloading:", e)
            return None

    # ---------------------------------------------------
    # UPLOAD
    # ---------------------------------------------------

    def upload_file(self, file):
        if not file or file.filename == "":
            return False, "Geen bestand geselecteerd"

        # size check
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)

        if size > self.max_file_size:
            return False, f"Bestand groter dan {self.max_file_size/1024/1024}MB"

        try:
            filename = secure_filename(file.filename)
            temp_path = os.path.join(self.upload_folder, filename)

            os.makedirs(self.upload_folder, exist_ok=True)
            file.save(temp_path)

            # upload to nextcloud
            url = self._build_url(filename)
            with open(temp_path, "rb") as f:
                response = requests.put(url, data=f, auth=self._auth(), timeout=30)

            os.remove(temp_path)

            if response.status_code in (201, 204):
                return True, f"'{filename}' geüpload naar Nextcloud"
            return False, "Upload mislukt"

        except Exception as e:
            return False, f"Fout: {e}"
