import requests
from bs4 import BeautifulSoup
import re
from typing import Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VLCChecker:
    """Sjekker for VLC Media Player-oppdateringer"""
    
    VLC_DOWNLOAD_URL = "https://www.videolan.org/vlc/download-windows.html"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_latest_version(self) -> Optional[str]:
        """Henter den seneste VLC-versjonen fra VideoLan"""
        try:
            logger.info(f"Henter VLC-informasjon fra {self.VLC_DOWNLOAD_URL}")
            response = self.session.get(self.VLC_DOWNLOAD_URL, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Søk etter versjonsinformasjon i siden
            version_match = re.search(r'version\s*[\'":]?\s*([0-9]+\.[0-9]+\.[0-9]+)', 
                                     response.text, re.IGNORECASE)
            
            if version_match:
                version = version_match.group(1)
                logger.info(f"Fant VLC versjon: {version}")
                return version
            
            # Alternativ: søk etter versjonsnummer i h1/h2-tagger
            for heading in soup.find_all(['h1', 'h2']):
                text = heading.get_text()
                version_match = re.search(r'(\d+\.\d+\.\d+)', text)
                if version_match:
                    version = version_match.group(1)
                    logger.info(f"Fant VLC versjon i heading: {version}")
                    return version
            
            logger.warning("kunne ikke finne versjonsnummer på siden")
            return None
            
        except requests.RequestException as e:
            logger.error(f"Feil ved henting av VLC-info: {e}")
            return None
    
    def check_for_updates(self, current_version: str, latest_version: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Sjekker om det finnes oppdateringer for VLC
        
        Returns:
            (har_oppdatering: bool, ny_versjon: str|None)
        """
        if latest_version is None:
            latest_version = self.get_latest_version()
        
        if latest_version is None:
            logger.warning("Kunne ikke bestemme siste versjon")
            return False, None
        
        if self._compare_versions(current_version, latest_version) < 0:
            logger.info(f"Oppdatering tilgjengelig: {current_version} -> {latest_version}")
            return True, latest_version
        else:
            logger.info(f"Du bruker allerede siste versjon: {current_version}")
            return False, None
    
    @staticmethod
    def _compare_versions(v1: str, v2: str) -> int:
        """
        Sammenligner to versjonsnummer
        Returns: -1 hvis v1 < v2, 0 hvis v1 == v2, 1 hvis v1 > v2
        """
        try:
            v1_parts = [int(x) for x in v1.split('.')]
            v2_parts = [int(x) for x in v2.split('.')]
            
            # Pad med nuller hvis ulike lengder
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            for a, b in zip(v1_parts, v2_parts):
                if a < b:
                    return -1
                elif a > b:
                    return 1
            return 0
        except (ValueError, AttributeError):
            logger.warning(f"Kunne ikke sammenligne versjoner: {v1} vs {v2}")
            return 0
