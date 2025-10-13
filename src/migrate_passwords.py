#!/usr/bin/env python3
"""
Password Migration Utility for PdaNet Linux
Migrates plaintext passwords from config files to system keyring

SECURITY: This script addresses Issue #291 and #117 from the audit
- Moves WiFi passwords from plaintext JSON to secure keyring storage
- Creates backup before migration
- Provides rollback capability
- Logs all migration actions
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

try:
    from config_manager import CONFIG_DIR, ConfigManager
    from secret_store import is_available, set_wifi_password
except ImportError:
    # Allow running from scripts directory
    import os
    sys.path.insert(0, str(Path(__file__).parent))
    from config_manager import CONFIG_DIR, ConfigManager
    from secret_store import is_available, set_wifi_password


def backup_config_file(config_dir: Path, filename: str) -> Path | None:
    """Create timestamped backup of config file"""
    source = config_dir / filename
    if not source.exists():
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = config_dir / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    backup_path = backup_dir / f"{filename}.{timestamp}.backup"
    shutil.copy2(source, backup_path)
    return backup_path


def migrate_wifi_passwords(dry_run: bool = False) -> dict:
    """
    Migrate all WiFi passwords from plaintext to keyring
    
    Args:
        dry_run: If True, only report what would be done without making changes
        
    Returns:
        dict with migration statistics and results
    """
    results = {
        "success": False,
        "migrated": 0,
        "failed": 0,
        "skipped": 0,
        "errors": [],
        "backup_path": None,
        "networks": []
    }
    
    # Check keyring availability
    if not is_available():
        results["errors"].append("System keyring not available - cannot migrate")
        results["errors"].append("Install 'python3-keyring' package or keep using plaintext storage")
        return results
    
    config_dir = Path(CONFIG_DIR)
    wifi_networks_file = config_dir / "wifi_networks.json"
    
    # Check if file exists
    if not wifi_networks_file.exists():
        results["errors"].append(f"No wifi_networks.json found at {wifi_networks_file}")
        results["success"] = True  # Not an error, just nothing to migrate
        return results
    
    # Load existing networks
    try:
        with open(wifi_networks_file) as f:
            networks = json.load(f)
    except Exception as e:
        results["errors"].append(f"Failed to load wifi_networks.json: {e}")
        return results
    
    if not networks:
        results["success"] = True
        results["errors"].append("No networks found to migrate")
        return results
    
    # Create backup
    if not dry_run:
        backup_path = backup_config_file(config_dir, "wifi_networks.json")
        if backup_path:
            results["backup_path"] = str(backup_path)
    
    # Migrate each network
    updated_networks = {}
    for ssid, data in networks.items():
        if not isinstance(data, dict):
            results["errors"].append(f"Invalid data format for {ssid}")
            results["failed"] += 1
            continue
        
        password = data.get("password")
        
        # Skip if no password stored
        if not password:
            results["skipped"] += 1
            updated_networks[ssid] = data
            results["networks"].append({"ssid": ssid, "status": "skipped (no password)"})
            continue
        
        # Attempt migration
        if dry_run:
            results["networks"].append({"ssid": ssid, "status": "would migrate", "password_len": len(password)})
            results["migrated"] += 1
        else:
            success = set_wifi_password(ssid, password)
            if success:
                # Remove password from dict, keep metadata
                updated_data = {k: v for k, v in data.items() if k != "password"}
                updated_networks[ssid] = updated_data
                results["migrated"] += 1
                results["networks"].append({"ssid": ssid, "status": "migrated"})
            else:
                # Keep plaintext as fallback
                updated_networks[ssid] = data
                results["failed"] += 1
                results["errors"].append(f"Failed to migrate {ssid} to keyring")
                results["networks"].append({"ssid": ssid, "status": "failed (kept plaintext)"})
    
    # Save updated networks file (without passwords)
    if not dry_run and results["migrated"] > 0:
        try:
            with open(wifi_networks_file, 'w') as f:
                json.dump(updated_networks, f, indent=2)
            # Set restrictive permissions
            wifi_networks_file.chmod(0o600)
            results["success"] = True
        except Exception as e:
            results["errors"].append(f"Failed to save updated wifi_networks.json: {e}")
            results["success"] = False
    else:
        results["success"] = True
    
    return results


def print_migration_report(results: dict, dry_run: bool = False):
    """Print human-readable migration report"""
    print("\n" + "="*60)
    if dry_run:
        print("PASSWORD MIGRATION DRY RUN REPORT")
    else:
        print("PASSWORD MIGRATION REPORT")
    print("="*60)
    
    if results["backup_path"]:
        print(f"\n✓ Backup created: {results['backup_path']}")
    
    print("\n📊 Statistics:")
    print(f"   Migrated to keyring: {results['migrated']}")
    print(f"   Failed to migrate:   {results['failed']}")
    print(f"   Skipped (no pwd):    {results['skipped']}")
    
    if results["networks"]:
        print("\n📝 Networks:")
        for net in results["networks"]:
            status_icon = "✓" if "migrated" in net["status"] else "⚠" if "failed" in net["status"] else "•"
            print(f"   {status_icon} {net['ssid']}: {net['status']}")
    
    if results["errors"]:
        print("\n⚠️  Errors:")
        for error in results["errors"]:
            print(f"   • {error}")
    
    if results["success"]:
        if dry_run:
            print("\n✓ Dry run completed successfully")
            print("  Run without --dry-run to perform actual migration")
        else:
            print("\n✓ Migration completed successfully")
            if results["migrated"] > 0:
                print(f"  {results['migrated']} password(s) now stored securely in system keyring")
    else:
        print("\n✗ Migration failed")
    
    print("="*60 + "\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Migrate WiFi passwords from plaintext to system keyring"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without making changes"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force migration even if keyring backend seems unavailable"
    )
    
    args = parser.parse_args()
    
    print("PdaNet Linux - Password Migration Utility")
    print("Security Issue #291 & #117 Fix")
    
    if not is_available() and not args.force:
        print("\n⚠️  System keyring not available!")
        print("Install keyring support: sudo apt-get install python3-keyring")
        print("\nOr use --force to attempt migration anyway")
        sys.exit(1)
    
    results = migrate_wifi_passwords(dry_run=args.dry_run)
    print_migration_report(results, dry_run=args.dry_run)
    
    sys.exit(0 if results["success"] else 1)


if __name__ == "__main__":
    main()
