"""
File Upload Service
Handles file upload functionality
"""

import os
import requests
from requests.auth import HTTPBasicAuth
from werkzeug.utils import secure_filename
from flask import current_app
from urllib.parse import quote

class FileUploadService:
    # Lokale configuratie
    UPLOAD_FOLDER = 'app/static/uploads'
    ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 
        'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', 'mp4', 'mp3', 'wav'
    }
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    
    @classmethod
    def allowed_file(cls, filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in cls.ALLOWED_EXTENSIONS
    
    @classmethod
    def upload_to_nextcloud(cls, file_path, filename):
        """Upload file to Nextcloud"""
        try:
            server_url = current_app.config['NEXTCLOUD_SERVER_URL']
            username = current_app.config['NEXTCLOUD_USERNAME']
            password = current_app.config['NEXTCLOUD_PASSWORD']
            folder = current_app.config['NEXTCLOUD_FOLDER']
            
            # URL encode the filename to handle special characters
            encoded_filename = quote(filename, safe='')
            url = f"{server_url}/remote.php/dav/files/{username}/{folder}/{encoded_filename}"
            
            print(f"Uploading to: {url}")  # Debug info
            
            with open(file_path, 'rb') as file:
                response = requests.put(
                    url,
                    data=file,
                    auth=HTTPBasicAuth(username, password),
                    timeout=30
                )
            
            print(f"Response status: {response.status_code}")  # Debug info
            print(f"Response text: {response.text}")  # Debug info
            
            return response.status_code == 201 or response.status_code == 204
            
        except Exception as e:
            print(f"Nextcloud upload error: {e}")  # Debug info
            return False
    
    @classmethod
    def list_files(cls):
        """List all files in Nextcloud folder"""
        try:
            server_url = current_app.config['NEXTCLOUD_SERVER_URL']
            username = current_app.config['NEXTCLOUD_USERNAME']
            password = current_app.config['NEXTCLOUD_PASSWORD']
            folder = current_app.config['NEXTCLOUD_FOLDER']
            
            folder_url = f"{server_url}/remote.php/dav/files/{username}/{folder}/"
            
            response = requests.request(
                'PROPFIND',
                folder_url,
                auth=HTTPBasicAuth(username, password),
                timeout=10,
                headers={'Depth': '1'}
            )
            
            if response.status_code == 207:
                # Parse XML response to extract filenames
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.text)
                files = []
                
                for response_elem in root.findall('.//{DAV:}response'):
                    href = response_elem.find('.//{DAV:}href')
                    if href is not None and href.text:
                        filename = href.text.split('/')[-1]
                        if filename and filename != folder:  # Skip folder itself
                            files.append(filename)
                
                return files
            else:
                return []
                
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    @classmethod
    def download_file(cls, filename):
        """Download file from Nextcloud"""
        try:
            server_url = current_app.config['NEXTCLOUD_SERVER_URL']
            username = current_app.config['NEXTCLOUD_USERNAME']
            password = current_app.config['NEXTCLOUD_PASSWORD']
            folder = current_app.config['NEXTCLOUD_FOLDER']
            
            encoded_filename = quote(filename, safe='')
            url = f"{server_url}/remote.php/dav/files/{username}/{folder}/{encoded_filename}"
            
            response = requests.get(
                url,
                auth=HTTPBasicAuth(username, password),
                timeout=30
            )
            
            if response.status_code == 200:
                return response.content
            else:
                return None
                
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None

    @classmethod
    def upload_file(cls, file):
        """Main upload method"""
        if not file or file.filename == '':
            return False, "Geen bestand geselecteerd"
        
        if not cls.allowed_file(file.filename):
            return False, f"Bestandstype niet toegestaan: {file.filename}"
        
        try:
            # Tijdelijk opslaan
            filename = secure_filename(file.filename)
            temp_path = os.path.join(cls.UPLOAD_FOLDER, filename)
            os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
            file.save(temp_path)
            
            # Upload naar Nextcloud
            success = cls.upload_to_nextcloud(temp_path, filename)
            
            # Temp file verwijderen
            os.remove(temp_path)
            
            if success:
                return True, f"Bestand '{file.filename}' succesvol geüpload naar Nextcloud!"
            else:
                return False, "Fout bij uploaden naar Nextcloud"
                
        except Exception as e:
            return False, f"Fout bij uploaden: {str(e)}"