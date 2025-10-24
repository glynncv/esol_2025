
#!/usr/bin/env python3
"""
Simple OKR Status Dashboard
Provides an easy-to-use interface for the separated ESOL analyzer
"""

import sys
from pathlib import Path
from datetime import datetime

# Add the scripts directory to the path
sys.path.append(str(Path(__file__).parent))

from separated_esol_analyzer import OKRAnalysisOrchestrator
from data_utils import get_data_file_path

def print_menu():
    """Display the main menu"""
    print("\n" + "="*50)
    print("🎯 OKR ANALYSIS DASHBOARD")
    print("="*50)
    print("1. 📊 Quick Status Check (Daily)")
    print("2. 📋 Executive Summary")  
    print("3. 📈 Full OKR Tracker")
    print("4. 🏢 Site Analysis (ESOL)")
    print("5. 🖥️ Windows 11 Site Analysis")
    print("6. 💾 Save Executive Report")
    print("7. ❓ Help")
    print("8. 🚪 Exit")
    print("="*50)

def quick_status():
    """Run quick status check"""
    try:
        orchestrator = OKRAnalysisOrchestrator()
        data_file = get_data_file_path()
        metrics = orchestrator.get_metrics_json(data_file)
        
        print(f"""
🎯 OKR QUICK STATUS CHECK
{'='*50}
Overall Score: {metrics['overall_score']:.1f}%
Status: {['🔴 AT RISK', '🟡 CAUTION', '🟢 ON TRACK'][metrics['overall_status_level']]}

Key Metrics:
• ESOL 2024: {metrics['esol_2024_count']} devices ({metrics['esol_2024_percentage']:.1f}%)
• ESOL 2025: {metrics['esol_2025_count']} devices ({metrics['esol_2025_percentage']:.1f}%)
• Win11 Compatibility: {metrics['compatibility_percentage']:.1f}%
• Enterprise Kiosks: {metrics['enterprise_kiosk_count']} need re-provisioning

Priority Actions:
1. 🔴 Immediate: Procure {metrics['esol_2024_count']} ESOL 2024 devices
2. 🟡 Q3 Planning: {metrics['kr2_milestone_target_devices']} ESOL 2025 devices  
3. 🟢 Re-provision: {metrics['enterprise_kiosk_count']} Enterprise kiosk devices

Total Investment: {metrics['total_devices'] - metrics['compatible_device_count']} devices requiring replacement
""")
    except Exception as e:
        print(f"❌ Error: {e}")

def executive_summary():
    """Display executive summary"""
    try:
        orchestrator = OKRAnalysisOrchestrator()
        data_file = get_data_file_path()
        summary = orchestrator.generate_executive_summary(data_file)
        print(summary)
    except Exception as e:
        print(f"❌ Error: {e}")

def full_tracker():
    """Display full OKR tracker"""
    try:
        orchestrator = OKRAnalysisOrchestrator()
        data_file = get_data_file_path()
        tracker = orchestrator.generate_full_report(data_file)
        print(tracker)
    except Exception as e:
        print(f"❌ Error: {e}")

def site_analysis():
    """Display ESOL site analysis"""
    try:
        orchestrator = OKRAnalysisOrchestrator()
        data_file = get_data_file_path()
        analysis = orchestrator.generate_site_analysis(data_file, 10)
        print(analysis)
    except Exception as e:
        print(f"❌ Error: {e}")

def win11_site_analysis():
    """Display Windows 11 site analysis"""
    try:
        import subprocess
        import sys
        
        # Run the Windows 11 site analysis
        result = subprocess.run([
            sys.executable, 'scripts/win11_count.py', '--site-table'
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            print("🖥️ Windows 11 Site Analysis")
            print("=" * 50)
            print(result.stdout)
        else:
            print(f"❌ Error running Windows 11 analysis: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def save_executive_report():
    """Save executive report to file"""
    try:
        orchestrator = OKRAnalysisOrchestrator()
        data_file = get_data_file_path()
        summary = orchestrator.generate_executive_summary(data_file)
        
        # Create reports directory if it doesn't exist
        reports_dir = Path('data/reports')
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = reports_dir / f'Executive_Summary_{timestamp}.md'
        
        # Save the report
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"✅ Executive summary saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def show_help():
    """Display help information"""
    print("""
📚 HELP - OKR Analysis Dashboard
================================

This dashboard provides easy access to ESOL OKR analysis tools:

1. QUICK STATUS CHECK
   - Daily overview of OKR progress
   - Key metrics and priority actions
   - Best for: Daily stand-ups, quick reviews

2. EXECUTIVE SUMMARY  
   - Management-focused report
   - High-level status and critical actions
   - Best for: Weekly reports, executive briefings

3. FULL OKR TRACKER
   - Comprehensive detailed analysis
   - Complete progress tracking and risk assessment
   - Best for: Monthly reviews, deep analysis

4. SITE ANALYSIS (ESOL)
   - Site-by-site breakdown of ESOL devices
   - Priority ranking by device count
   - Best for: Planning site visits, resource allocation

5. WINDOWS 11 SITE ANALYSIS
   - Site-by-site Windows 11 deployment status
   - Shows eligible, upgraded, and pending devices
   - Best for: Windows 11 upgrade planning and tracking

6. SAVE EXECUTIVE REPORT
   - Saves executive summary to timestamped file
   - Files saved to data/reports/ directory
   - Best for: Record keeping, sharing reports

💡 Tips:
- Run Quick Status daily for best results
- Use Executive Summary for weekly management updates
- Save reports regularly for tracking progress over time
- Site Analysis helps prioritize remediation efforts

🔧 Technical Notes:
- Data source: Auto-detected from data/raw/ or EUC_DATA_FILE environment variable
- Configuration: config/ directory (YAML files)
- Reports saved to: data/reports/
- Shared utilities: scripts/data_utils.py for consistent file handling
""")

def main():
    """Main application loop"""
    print("🚀 Starting OKR Analysis Dashboard...")
    
    while True:
        print_menu()
        
        try:
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                print("\n📊 Running Quick Status Check...")
                quick_status()
                
            elif choice == '2':
                print("\n📋 Running Executive Summary...")
                executive_summary()
                
            elif choice == '3':
                print("\n📈 Running Full OKR Tracker...")
                full_tracker()
                
            elif choice == '4':
                print("\n🏢 Running ESOL Site Analysis...")
                site_analysis()
                
            elif choice == '5':
                print("\n🖥️ Running Windows 11 Site Analysis...")
                win11_site_analysis()
                
            elif choice == '6':
                print("\n💾 Saving Executive Report...")
                save_executive_report()
                
            elif choice == '7':
                show_help()
                
            elif choice == '8':
                print("\n👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter a number from 1-8.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
