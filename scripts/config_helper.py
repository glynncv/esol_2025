#!/usr/bin/env python3
"""
OKR Configuration Helper
Helps users understand and modify OKR configuration settings
"""

import sys
from pathlib import Path
import yaml

# Add the scripts directory to the path
sys.path.append(str(Path(__file__).parent))

from separated_esol_analyzer import ConfigManager

def display_current_config():
    """Display current configuration settings"""
    try:
        # Find project root (go up from scripts/ to project root)
        project_root = Path(__file__).resolve().parent.parent
        config_path = str(project_root / 'config')
        config_manager = ConfigManager(config_path=config_path)
        
        print("📋 CURRENT OKR CONFIGURATION")
        print("="*50)
        
        # OKR Weights
        okr_config = config_manager.get_okr_criteria()
        print("\n🎯 OKR WEIGHTS:")
        weights = okr_config['okr_weights']
        for kr, weight in weights.items():
            print(f"  {kr}: {weight}%")
        
        total_weight = sum(weights.values())
        status = "✅ Valid" if total_weight == 100 else f"⚠️  Warning: Total = {total_weight}%"
        print(f"  Total: {total_weight}% ({status})")
        
        # Targets
        print("\n🎯 TARGETS:")
        targets = okr_config['targets']
        for target, value in targets.items():
            print(f"  {target}: {value}")
        
        # Status Thresholds
        print("\n📊 STATUS THRESHOLDS:")
        thresholds = okr_config['status_thresholds']
        for threshold, value in thresholds.items():
            print(f"  {threshold}: {value}%")
        
        # ESOL Categories
        print("\n🔧 ESOL CATEGORIES:")
        esol_config = config_manager.get_esol_criteria()
        categories = esol_config['esol_categories']
        for category, details in categories.items():
            print(f"  {category}:")
            print(f"    Action: {details['action_value']}")
            print(f"    Target Date: {details['target_date']}")
            print(f"    Description: {details['description']}")
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")

def validate_config():
    """Validate configuration settings"""
    try:
        # Find project root (go up from scripts/ to project root)
        project_root = Path(__file__).resolve().parent.parent
        config_path = str(project_root / 'config')
        config_manager = ConfigManager(config_path=config_path)
        print("✅ Configuration validation passed!")
        
        # Check weights
        okr_config = config_manager.get_okr_criteria()
        weights = okr_config['okr_weights']
        total_weight = sum(weights.values())
        
        if total_weight != 100:
            print(f"⚠️  Warning: OKR weights sum to {total_weight}%, not 100%")
        else:
            print("✅ OKR weights sum to 100%")
            
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")

def show_config_help():
    """Show help for configuration"""
    print("""
📚 CONFIGURATION HELP
====================

The OKR system uses two main configuration files:

1. config/okr_criteria.yaml
   - OKR weights (must sum to 100%)
   - Status thresholds (on_track, caution levels)
   - Targets for each Key Result
   - Milestone dates

2. config/esol_criteria.yaml  
   - ESOL category definitions
   - Data column mappings
   - Kiosk detection patterns
   - Windows 11 compatibility rules

🔧 MODIFYING CONFIGURATION:

To change OKR weights:
1. Edit config/okr_criteria.yaml
2. Modify the okr_weights section
3. Ensure weights sum to 100%

To change targets:
1. Edit the targets section in okr_criteria.yaml
2. Update percentage or count targets as needed

To change status thresholds:
1. Modify status_thresholds in okr_criteria.yaml
2. Set on_track_min_progress and caution_min_progress

⚠️ IMPORTANT:
- Always backup configuration files before editing
- Use this tool to validate after changes
- OKR weights must sum to exactly 100%
- All dates should be in YYYY-MM-DD format

💡 TIP:
Run this script after making changes to validate your configuration.
""")

def backup_config():
    """Create backup of current configuration"""
    try:
        from datetime import datetime
        import shutil
        
        # Find project root (go up from scripts/ to project root)
        project_root = Path(__file__).resolve().parent.parent
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        config_dir = project_root / 'config'
        backup_dir = project_root / 'config' / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        # Backup YAML files
        for yaml_file in config_dir.glob('*.yaml'):
            backup_name = f"{yaml_file.stem}_{timestamp}.yaml"
            backup_path = backup_dir / backup_name
            shutil.copy2(yaml_file, backup_path)
            print(f"✅ Backed up {yaml_file.name} to {backup_path}")
            
        print(f"\n📦 Configuration backup completed: {timestamp}")
        
    except Exception as e:
        print(f"❌ Error creating backup: {e}")

def main():
    """Main configuration helper"""
    print("🔧 OKR CONFIGURATION HELPER")
    print("="*50)
    print("1. Display Current Configuration")
    print("2. Validate Configuration")
    print("3. Backup Configuration")
    print("4. Help")
    print("5. Exit")
    print("="*50)
    
    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                print("\n" + "="*50)
                display_current_config()
                
            elif choice == '2':
                print("\n🔍 Validating Configuration...")
                validate_config()
                
            elif choice == '3':
                print("\n📦 Creating Configuration Backup...")
                backup_config()
                
            elif choice == '4':
                show_config_help()
                
            elif choice == '5':
                print("\n👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter a number from 1-5.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
