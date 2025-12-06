# nextcloud_client.py
# praat met nextcloud

import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import quote, unquote
import xml.etree.ElementTree as ET
from datetime import datetime
import os


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

    def get_storage_quota(self):
        """Haal opslag quota informatie op (gebruikt, totaal, beschikbaar)."""
        try:
            # Haal quota op van de user root directory
            url = f"{self.server_url}/remote.php/dav/files/{self.username}/"
            response = requests.request("PROPFIND", url, headers={"Depth": "0"}, auth=self._auth(), timeout=30)
            
            if response.status_code != 207:
                print(f"ERROR: Nextcloud quota PROPFIND returned status {response.status_code}")
                return None
            
            # Parse XML response voor quota
            root = ET.fromstring(response.text)
            quota_used = None
            quota_available = None
            
            # Zoek naar quota-used en quota-available in de response
            # Nextcloud gebruikt verschillende namespace formats
            for prop in root.findall(".//{DAV:}propstat"):
                prop_elem = prop.find("{DAV:}prop")
                if prop_elem is None:
                    continue
                
                # Probeer verschillende namespace formats
                quota_used_elem = (
                    prop_elem.find(".//{http://owncloud.org/ns}quota-used-bytes") or
                    prop_elem.find(".//{http://nextcloud.org/ns}quota-used-bytes") or
                    prop_elem.find(".//quota-used-bytes")
                )
                quota_available_elem = (
                    prop_elem.find(".//{http://owncloud.org/ns}quota-available-bytes") or
                    prop_elem.find(".//{http://nextcloud.org/ns}quota-available-bytes") or
                    prop_elem.find(".//quota-available-bytes")
                )
                
                if quota_used_elem is not None and quota_used_elem.text:
                    try:
                        quota_used = int(quota_used_elem.text)
                    except (ValueError, TypeError):
                        pass
                if quota_available_elem is not None and quota_available_elem.text:
                    try:
                        quota_available = int(quota_available_elem.text)
                    except (ValueError, TypeError):
                        pass
            
            if quota_used is None or quota_available is None:
                # Fallback: probeer OCS API
                return self._get_quota_via_ocs()
            
            quota_total = quota_used + quota_available if quota_available >= 0 else None
            
            return {
                "used": quota_used,
                "available": quota_available if quota_available >= 0 else None,
                "total": quota_total
            }
        except Exception as e:
            print(f"ERROR: Fout bij ophalen quota: {e}")
            return None

    def _get_quota_via_ocs(self):
        """Haal quota op via Nextcloud OCS API."""
        try:
            url = f"{self.server_url}/ocs/v1.php/cloud/users/{self.username}"
            headers = {"OCS-APIRequest": "true"}
            response = requests.get(url, headers=headers, auth=self._auth(), timeout=30)
            
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                quota_elem = root.find(".//quota")
                if quota_elem is not None:
                    quota_total = int(quota_elem.text) if quota_elem.text and quota_elem.text != "default" else None
                    used_elem = root.find(".//quota/used")
                    quota_used = int(used_elem.text) if used_elem is not None and used_elem.text else None
                    
                    if quota_total and quota_used is not None:
                        quota_available = quota_total - quota_used if quota_total > 0 else None
                        return {
                            "used": quota_used,
                            "available": quota_available,
                            "total": quota_total
                        }
        except Exception as e:
            print(f"ERROR: OCS API quota ophalen mislukt: {e}")
        return None

    def get_files_with_details(self):
        """Haal bestanden op met details (naam, grootte, datum)."""
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
                if folder_path not in decoded:
                    continue
                
                filename = decoded.split('/')[-1]
                
                # Haal bestandsgrootte op
                size = 0
                getcontentlength = elem.find(".//{DAV:}getcontentlength")
                if getcontentlength is not None and getcontentlength.text:
                    size = int(getcontentlength.text)
                
                # Haal modificatiedatum op
                date_str = None
                getlastmodified = elem.find(".//{DAV:}getlastmodified")
                if getlastmodified is not None and getlastmodified.text:
                    try:
                        # Parse RFC 1123 date format
                        date_str = getlastmodified.text
                    except:
                        pass
                
                files.append({
                    "name": filename,
                    "size": size,
                    "date": date_str
                })
            
            return files
        except Exception as e:
            print(f"ERROR: Fout bij ophalen bestandsdetails: {e}")
            return []

    def get_file_icon(self, filename):
        """Bepaal icoon op basis van bestandsextensie."""
        ext = os.path.splitext(filename)[1].lower()
        icon_map = {
            '.pdf': '📄', '.doc': '📄', '.docx': '📄', '.txt': '📄', '.rtf': '📄',
            '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️', '.bmp': '🖼️', '.svg': '🖼️',
            '.mp4': '🎥', '.avi': '🎥', '.mov': '🎥', '.mkv': '🎥', '.wmv': '🎥',
            '.mp3': '🎵', '.wav': '🎵', '.flac': '🎵', '.aac': '🎵', '.ogg': '🎵',
            '.zip': '📦', '.rar': '📦', '.7z': '📦', '.tar': '📦', '.gz': '📦',
            '.xls': '📊', '.xlsx': '📊', '.csv': '📊',
            '.ppt': '📊', '.pptx': '📊'
        }
        return icon_map.get(ext, '📄')
