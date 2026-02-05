#!/usr/bin/env python3
"""
VLC Oppdaterings-Sjekker - Hovedprogram
Sjekker om VLC Media Player har nye oppdateringer
"""

import argparse
import sys
from vlc_checker import VLCChecker
from database import VLCDatabase

VERSION = "1.0.0"
DEFAULT_VLC_VERSION = "3.0.20"  # Default versjon hvis VLC ikke er installert

def get_installed_vlc_version() -> str:
    """
    Prøver å finne installert VLC-versjon fra systemet
    Returnerer standardversjon hvis den ikke finnes
    """
    import subprocess
    import os
    
    # Windows
    vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
    if not os.path.exists(vlc_path):
        vlc_path = r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
    
    if os.path.exists(vlc_path):
        try:
            result = subprocess.run(
                [vlc_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Parseoutput for versjonsnummer
            for line in result.stdout.split('\n'):
                import re
                match = re.search(r'(\d+\.\d+\.\d+)', line)
                if match:
                    return match.group(1)
        except Exception as e:
            print(f"Advarsel: Kunne ikke lese VLC-versjon ({e})")
    
    print(f"VLC ikke funnet. Bruker standardversjon: {DEFAULT_VLC_VERSION}")
    return DEFAULT_VLC_VERSION

def main():
    parser = argparse.ArgumentParser(
        description="VLC Media Player Oppdaterings-Sjekker"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Sjekk omgående for oppdateringer"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}"
    )
    parser.add_argument(
        "--current",
        type=str,
        default=None,
        help="Spesifiser nåværende VLC-versjon (ellers autodetekt)"
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="Vis oppdaterings-historikk"
    )
    parser.add_argument(
        "--list-versions",
        action="store_true",
        help="List alle registrerte VLC-versjoner"
    )
    
    args = parser.parse_args()
    
    # Initialiserer checker og database
    checker = VLCChecker()
    db = VLCDatabase()
    
    # Henter nåværende versjon
    if args.current:
        current_version = args.current
    else:
        current_version = get_installed_vlc_version()
    
    if args.history:
        print("\n=== Oppdaterings-Historikk ===\n")
        history = db.get_update_history(limit=20)
        if history:
            for i, entry in enumerate(history, 1):
                status = "✓ Oppdatering tilgjengelig" if entry['has_update'] else "✗ Siste versjon"
                print(f"{i}. [{entry['checked_at']}]")
                print(f"   Nåværende: {entry['current']} -> Siste: {entry['latest']}")
                print(f"   {status}\n")
        else:
            print("Ingen historikk funnet.")
    
    elif args.list_versions:
        print("\n=== Registrerte VLC-Versjoner ===\n")
        versions = db.get_all_versions()
        if versions:
            for v in versions:
                print(f"Versjon: {v['version']}")
                if v['release_date']:
                    print(f"  Release: {v['release_date']}")
                if v['download_url']:
                    print(f"  URL: {v['download_url']}")
                print(f"  Sjekket: {v['checked_at']}\n")
        else:
            print("Ingen versjoner registrert.")
    
    else:
        # Standard operasjon - sjekk for oppdateringer
        print(f"\nVLC Oppdaterings-Sjekker v{VERSION}")
        print(f"Nåværende versjon: {current_version}")
        print("-" * 40)
        
        latest_version = checker.get_latest_version()
        
        if latest_version:
            db.add_version(latest_version)
            has_update, new_version = checker.check_for_updates(current_version, latest_version)
            db.record_check(current_version, latest_version)
            
            if has_update:
                print(f"\n✓ OPPDATERING TILGJENGELIG!")
                print(f"  Ny versjon: {new_version}")
                print(f"\n  Last ned fra: https://www.videolan.org/vlc/")
            else:
                print(f"\n✗ Du bruker allerede siste versjon ({latest_version})")
        else:
            print("\n✗ Kunne ikke kontakte VideoLan for å sjekke oppdateringer.")
            print("  Prøv igjen senere.")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
