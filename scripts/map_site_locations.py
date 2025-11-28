#!/usr/bin/env python3
"""Map site locations from EUC_ESOL.xlsx to PYTHON EMEA Locations.xls using YAML mappings"""
import pandas as pd
import yaml
from pathlib import Path
from difflib import SequenceMatcher
import sys

def similarity(a, b):
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def load_yaml_mappings(yaml_file):
    """Load site mappings from YAML file."""
    with open(yaml_file, 'r') as f:
        yaml_data = yaml.safe_load(f)
    
    # Create mapping dictionaries
    # Map from Site Location (ESOL site) to full mapping info
    site_to_mapping = {}
    for entry in yaml_data:
        site_location = entry.get('Site Location', '').strip()
        if site_location:
            site_to_mapping[site_location] = {
                'Site Location': site_location,
                'Site Name': entry.get('Site Name', ''),
                'Location': entry.get('Location', ''),
                'Country': entry.get('Country', ''),
                'SDM': entry.get('SDM', '')
            }
    
    return site_to_mapping, yaml_data

def main():
    # File paths - find project root (go up from scripts/ to project root)
    project_root = Path(__file__).resolve().parent.parent
    yaml_file = project_root / 'config' / 'esol_sites_mapped.yaml'
    euc_file = project_root / 'data' / 'raw' / 'EUC_ESOL.xlsx'
    locations_file = project_root / 'data' / 'raw' / 'PYTHON EMEA Locations.xls'
    
    # Load YAML mappings
    print("Loading YAML mappings...")
    try:
        site_mappings, yaml_data = load_yaml_mappings(yaml_file)
        print(f"[OK] Loaded {len(site_mappings)} site mappings from YAML")
    except Exception as e:
        print(f"[ERROR] Error loading YAML file: {e}")
        return
    
    # Load EUC_ESOL data
    print("Loading EUC_ESOL.xlsx...")
    try:
        euc_df = pd.read_excel(euc_file)
        print(f"[OK] Loaded {len(euc_df)} rows")
        print(f"Columns: {list(euc_df.columns)}")
    except Exception as e:
        print(f"[ERROR] Error loading EUC_ESOL.xlsx: {e}")
        return
    
    # Find site location column
    site_col = None
    for col in euc_df.columns:
        if 'site' in col.lower() and 'location' in col.lower():
            site_col = col
            break
    
    if not site_col:
        print("[ERROR] Could not find 'Site Location' column in EUC_ESOL.xlsx")
        print(f"Available columns: {list(euc_df.columns)}")
        return
    
    print(f"[OK] Found site column: '{site_col}'")
    
    # Get unique sites from EUC data
    euc_sites = euc_df[site_col].dropna().unique()
    euc_sites = [str(s).strip() for s in euc_sites if str(s).strip()]
    print(f"\n[OK] Found {len(euc_sites)} unique sites in EUC_ESOL.xlsx")
    
    # Load EMEA Locations file for reference/validation
    print(f"\nLoading PYTHON EMEA Locations.xls (for reference)...")
    locations_df = None
    location_sites = []
    try:
        # Try reading with different engines for .xls files
        try:
            locations_df = pd.read_excel(locations_file, engine='xlrd')
        except:
            locations_df = pd.read_excel(locations_file, engine='openpyxl')
        
        print(f"[OK] Loaded {len(locations_df)} rows")
        
        # Try to identify site column in locations file
        location_site_col = None
        for col in locations_df.columns:
            col_lower = str(col).lower()
            if 'site name' in col_lower:
                location_site_col = col
                break
        
        if location_site_col:
            location_sites = locations_df[location_site_col].dropna().unique()
            location_sites = [str(s).strip() for s in location_sites if str(s).strip()]
            print(f"[OK] Found {len(location_sites)} unique sites in PYTHON EMEA Locations.xls")
    except Exception as e:
        print(f"[WARNING] Could not load PYTHON EMEA Locations.xls: {e}")
        print("Continuing with YAML mappings only...")
    
    # Map sites using YAML
    print(f"\n{'='*80}")
    print("MAPPING ANALYSIS (using YAML mappings)")
    print(f"{'='*80}\n")
    
    mapped_sites = []
    unmapped_sites = []
    
    for euc_site in sorted(euc_sites):
        if euc_site in site_mappings:
            mapping = site_mappings[euc_site]
            mapped_sites.append({
                'EUC_Site': euc_site,
                'Location_Site': mapping['Site Name'],
                'Location': mapping['Location'],
                'Country': mapping['Country'],
                'SDM': mapping['SDM'],
                'Match_Type': 'yaml_mapped'
            })
        else:
            # Try fuzzy matching for unmapped sites (fallback)
            best_match = None
            best_score = 0
            best_match_full = None
            
            # Try matching against YAML Site Names
            for mapped_site, mapping in site_mappings.items():
                site_name = mapping.get('Site Name', '')
                location = mapping.get('Location', '')
                
                # Extract city from Site Name (format: "City - Country")
                if ' - ' in site_name:
                    city = site_name.split(' - ')[0].strip()
                else:
                    city = site_name
                
                # Try matching against city or location
                score1 = similarity(euc_site, city)
                score2 = similarity(euc_site, location)
                score = max(score1, score2)
                
                if score > best_score:
                    best_score = score
                    best_match = city if score1 > score2 else location
                    best_match_full = site_name
            
            if best_score >= 0.8:  # 80% similarity threshold
                unmapped_sites.append({
                    'EUC_Site': euc_site,
                    'Best_Match': best_match_full or best_match,
                    'Similarity': best_score,
                    'Match_Type': 'fuzzy_match'
                })
            else:
                unmapped_sites.append({
                    'EUC_Site': euc_site,
                    'Best_Match': 'N/A',
                    'Similarity': best_score,
                    'Match_Type': 'no_match'
                })
    
    # Print mapped sites (from YAML)
    print(f"YAML MAPPED SITES ({len(mapped_sites)}):")
    print("-" * 80)
    for site in mapped_sites:
        print(f"[YAML] {site['EUC_Site']:40s} -> {site['Location_Site']:40s}")
        print(f"       Location: {site['Location']}, Country: {site['Country']}, SDM: {site['SDM']}")
    
    # Print unmapped sites
    if unmapped_sites:
        fuzzy_matches = [s for s in unmapped_sites if s['Match_Type'] == 'fuzzy_match']
        no_matches = [s for s in unmapped_sites if s['Match_Type'] == 'no_match']
        
        if fuzzy_matches:
            print(f"\nFUZZY MATCHES (not in YAML, >=80% similarity) ({len(fuzzy_matches)}):")
            print("-" * 80)
            for site in fuzzy_matches:
                print(f"[FUZZY] {site['EUC_Site']:40s} -> {site['Best_Match']:40s} ({site['Similarity']:.2%})")
        
        if no_matches:
            print(f"\nNO MATCHES (not in YAML) ({len(no_matches)}):")
            print("-" * 80)
            for site in no_matches:
                print(f"[UNMAPPED] {site['EUC_Site']:40s}")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total EUC Sites: {len(euc_sites)}")
    print(f"YAML Mapped Sites: {len(mapped_sites)}")
    print(f"Unmapped Sites: {len(unmapped_sites)}")
    if unmapped_sites:
        fuzzy_count = sum(1 for s in unmapped_sites if s['Match_Type'] == 'fuzzy_match')
        no_match_count = sum(1 for s in unmapped_sites if s['Match_Type'] == 'no_match')
        print(f"  - Fuzzy matches (>=80%): {fuzzy_count}")
        print(f"  - No matches: {no_match_count}")
    print(f"YAML Mapping Rate: {len(mapped_sites)/len(euc_sites)*100:.1f}%")
    
    # Export mapping to CSV
    mapping_df = pd.DataFrame(mapped_sites)
    
    if len(unmapped_sites) > 0:
        unmapped_df = pd.DataFrame(unmapped_sites)
        # Combine both dataframes
        mapping_df = pd.concat([mapping_df, unmapped_df], ignore_index=True)
    
    output_file = project_root / 'data' / 'processed' / 'site_location_mapping.csv'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    mapping_df.to_csv(output_file, index=False)
    print(f"\n[OK] Mapping exported to: {output_file}")

if __name__ == "__main__":
    main()

