"""
File Upload Service (OOP versie)
Beheert uploaden, downloaden en ophalen van bestanden via Nextcloud.
"""

import os
import requests
from flask import current_app
from requests.auth import HTTPBasicAuth
from werkzeug.utils import secure_filename
from urllib.parse import quote
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
        encoded = quote(filename, safe='')
        return f"{self.server_url}/remote.php/dav/files/{self.username}/{self.folder}/{encoded}"

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    # ---------------------------------------------------
    # LIST FILES
    # ---------------------------------------------------

    def list_files(self):
        try:
            url = self._build_url()
            response = requests.request(
                "PROPFIND",
                url,
                auth=self._auth(),
                headers={"Depth": "1"},
                timeout=10
            )

            if response.status_code != 207:
                return []

            root = ET.fromstring(response.text)
            files = []

            for elem in root.findall(".//{DAV:}response"):
                href = elem.find(".//{DAV:}href")
                if href is not None:
                    name = href.text.split("/")[-1]
                    if name and name != self.folder:
                        files.append(name)

            return files

        except Exception as e:
            print("Error listing files:", e)
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

        if not self.allowed_file(file.filename):
            return False, "Bestandstype niet toegestaan"

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
