import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict

class VLCDatabase:
    """Håndterer SQLite-database for VLC-oppdaterings-sjekk"""
    
    def __init__(self, db_path: str = "vlc_updates.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialiserer databasen med nødvendige tabeller"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Opprett tabell for versjons-sjekker
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vlc_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL UNIQUE,
                release_date TEXT,
                download_url TEXT,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Opprett tabell for oppdaterings-historikk
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS update_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                current_version TEXT,
                latest_version TEXT,
                has_update BOOLEAN,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notified BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_version(self, version: str, release_date: Optional[str] = None, 
                   download_url: Optional[str] = None) -> bool:
        """Legger til en ny VLC-versjon i databasen"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO vlc_versions (version, release_date, download_url)
                VALUES (?, ?, ?)
            ''', (version, release_date, download_url))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Versjonen finnes allerede
            return False
    
    def get_latest_version(self) -> Optional[str]:
        """Henter den seneste registrerte VLC-versjonen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT version FROM vlc_versions 
            ORDER BY checked_at DESC LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def record_check(self, current_version: str, latest_version: str) -> bool:
        """Registrerer en oppdaterings-sjekk"""
        has_update = current_version != latest_version
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO update_checks (current_version, latest_version, has_update)
                VALUES (?, ?, ?)
            ''', (current_version, latest_version, has_update))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Feil ved registrering av sjekk: {e}")
            return False
    
    def get_update_history(self, limit: int = 10) -> List[Dict]:
        """Henter oppdaterings-historikk"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT current_version, latest_version, has_update, checked_at
            FROM update_checks 
            ORDER BY checked_at DESC LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'current': r[0],
                'latest': r[1],
                'has_update': bool(r[2]),
                'checked_at': r[3]
            }
            for r in results
        ]
    
    def get_all_versions(self) -> List[Dict]:
        """Henter alle registrerte VLC-versjoner"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT version, release_date, download_url, checked_at
            FROM vlc_versions
            ORDER BY checked_at DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'version': r[0],
                'release_date': r[1],
                'download_url': r[2],
                'checked_at': r[3]
            }
            for r in results
        ]
