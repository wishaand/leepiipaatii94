# nextcloud_client.py
# praat met nextcloud

import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import quote, unquote
import xml.etree.ElementTree as ET


class NextcloudClient:
    """Praat met Nextcloud via WebDAV."""

    def __init__(self, server_url, username, password, folder):
        """Sla inloggegevens op."""
        self.server_url = server_url
        self.username = username
        self.password = password
        self.folder = folder

    def _auth(self):
        """Maak inlogcode aan."""
        return HTTPBasicAuth(self.username, self.password)

    def _build_url(self, filename=""):
        """Maak URL voor Nextcloud."""
        if filename:
            encoded = quote(filename, safe='')
            return f"{self.server_url}/remote.php/dav/files/{self.username}/{self.folder}/{encoded}"
        return f"{self.server_url}/remote.php/dav/files/{self.username}/{self.folder}/"

    def list_files(self):
        """Haal lijst van bestanden op."""
        try:
            url = self._build_url()
            response = requests.request("PROPFIND", url, headers={"Depth": "1"}, auth=self._auth(), timeout=30)

            if response.status_code != 207:
                print(f"ERROR: Nextcloud PROPFIND returned status {response.status_code}")
                return []

            # Parse XML response
            root = ET.fromstring(response.text)
            files = []
            folder_path = f"/remote.php/dav/files/{self.username}/{self.folder}/"

            for elem in root.findall(".//{DAV:}response"):
                href = elem.find(".//{DAV:}href")
                if href is None:
                    continue

                decoded = unquote(href.text)
                if decoded.endswith('/'):
                    continue  # Skip mappen
                if folder_path in decoded:
                    files.append(decoded.split('/')[-1])

            return files
        except requests.exceptions.Timeout:
            print("ERROR: Nextcloud request timeout")
            return []
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Nextcloud request failed: {e}")
            return []
        except Exception as e:
            print(f"ERROR: Unexpected error in list_files: {e}")
            return []

    def upload(self, filename, file_bytes):
        """Upload bestand naar Nextcloud."""
        url = self._build_url(filename)
        response = requests.put(url, data=file_bytes, auth=self._auth(), timeout=30)
        return response.status_code in (201, 204)

    def download(self, filename):
        """Download bestand van Nextcloud."""
        url = self._build_url(filename)
        response = requests.get(url, auth=self._auth(), timeout=30)
        return response.content if response.status_code == 200 else None
