# Site Location Mapping Script Documentation

## Overview

`map_site_locations.py` is a Python script that maps ESOL site locations from the EUC_ESOL.xlsx file to Phinia location names using a YAML configuration file as the primary mapping source. The script provides a bridge between ESOL site identifiers and standardized Phinia location names.

## Purpose

The script serves to:
- Map ESOL site locations to Phinia location names
- Validate site mappings against the YAML configuration
- Identify unmapped sites that may need manual attention
- Export mapping results to CSV for further analysis

## Input Files

### Required Files

1. **`config/esol_sites_mapped.yaml`** (Required)
   - Primary mapping source
   - Contains mappings between ESOL site locations and Phinia locations
   - Format: Each entry includes:
     - `Site Location`: ESOL site identifier (from EUC_ESOL.xlsx)
     - `Site Name`: Full site name (format: "City - Country")
     - `Location`: Phinia location/city name
     - `Country`: Country name
     - `SDM`: Site Delivery Manager

2. **`data/raw/EUC_ESOL.xlsx`** (Required)
   - Source file containing ESOL device data
   - Must contain a "Site Location" column
   - Contains device inventory information

### Optional Files

3. **`data/raw/PYTHON EMEA Locations.xls`** (Optional)
   - Reference file for Phinia locations
   - Used for validation purposes only
   - Script continues even if this file is missing

## Output Files

- **`data/processed/site_location_mapping.csv`**
  - Contains all mapping results
  - Includes both YAML-mapped sites and unmapped sites
  - Columns:
    - `EUC_Site`: Site location from EUC_ESOL.xlsx
    - `Location_Site`: Full site name from YAML (if mapped)
    - `Location`: Phinia location name (if mapped)
    - `Country`: Country name (if mapped)
    - `SDM`: Site Delivery Manager (if mapped)
    - `Match_Type`: Type of match (`yaml_mapped`, `fuzzy_match`, or `no_match`)
    - `Best_Match`: Best match found (for unmapped sites)
    - `Similarity`: Similarity score (for fuzzy matches)

## How It Works

### 1. Load YAML Mappings
- Reads `config/esol_sites_mapped.yaml`
- Creates a dictionary mapping ESOL site locations to full mapping information
- Validates YAML structure

### 2. Load EUC Data
- Reads `data/raw/EUC_ESOL.xlsx`
- Automatically detects the "Site Location" column
- Extracts unique site locations

### 3. Load Reference Data (Optional)
- Attempts to load `data/raw/PYTHON EMEA Locations.xls`
- Used for reference/validation only
- Script continues if file is missing

### 4. Mapping Process

#### Primary Mapping (YAML-based)
- For each site in EUC_ESOL.xlsx:
  - Checks if site exists in YAML mappings
  - If found: Uses YAML mapping directly (exact match)
  - Includes: Site Name, Location, Country, SDM

#### Fallback Mapping (Fuzzy Matching)
- For sites not in YAML:
  - Uses fuzzy string matching against YAML Site Names
  - Calculates similarity scores (0.0 to 1.0)
  - Only matches if similarity >= 80% (0.8)
  - Marks as `fuzzy_match` or `no_match`

### 5. Output Generation
- Prints detailed mapping results to console
- Categorizes sites:
  - **YAML Mapped**: Sites found in YAML (exact matches)
  - **Fuzzy Matches**: Sites not in YAML but >=80% similar
  - **No Matches**: Sites with no good matches
- Exports results to CSV

## Usage

### Basic Usage

The script can be run from any directory. It automatically resolves paths relative to the project root.

**From project root:**
```bash
python scripts/map_site_locations.py
```

**From scripts directory:**
```bash
python map_site_locations.py
```

### Expected Output

```
Loading YAML mappings...
[OK] Loaded 19 site mappings from YAML
Loading EUC_ESOL.xlsx...
[OK] Loaded 3984 rows
[OK] Found site column: 'Site Location'
[OK] Found 24 unique sites in EUC_ESOL.xlsx

Loading PYTHON EMEA Locations.xls (for reference)...
[WARNING] Could not load PYTHON EMEA Locations.xls: ...
Continuing with YAML mappings only...

================================================================================
MAPPING ANALYSIS (using YAML mappings)
================================================================================

YAML MAPPED SITES (19):
--------------------------------------------------------------------------------
[YAML] Belval -> Belval - Luxembourg
       Location: Belval, Country: Luxembourg, SDM: Gauthier, Guillaume
...

NO MATCHES (not in YAML) (5):
--------------------------------------------------------------------------------
[UNMAPPED] Amsterdam
[UNMAPPED] Flechtorf
...

================================================================================
SUMMARY
================================================================================
Total EUC Sites: 24
YAML Mapped Sites: 19
Unmapped Sites: 5
  - Fuzzy matches (>=80%): 0
  - No matches: 5
YAML Mapping Rate: 79.2%

[OK] Mapping exported to: C:\Users\cglynn\myPython\esol_2025_testing\data\processed\site_location_mapping.csv
(Note: Path will vary based on your project location)
```

## Key Functions

### `load_yaml_mappings(yaml_file)`
- Loads and parses YAML configuration file
- Returns dictionary mapping site locations to full mapping info
- Handles YAML parsing errors

### `similarity(a, b)`
- Calculates string similarity ratio (0.0 to 1.0)
- Uses `difflib.SequenceMatcher`
- Case-insensitive comparison
- Used for fuzzy matching fallback

### `main()`
- Main execution function
- Orchestrates the entire mapping process
- Handles file loading, mapping, and output generation

## Match Types

1. **`yaml_mapped`**: Site found in YAML file (exact match)
   - Most reliable mapping
   - Includes full location details

2. **`fuzzy_match`**: Site not in YAML but >=80% similar to a YAML entry
   - Fallback matching
   - Should be reviewed manually

3. **`no_match`**: Site not in YAML and no good fuzzy match found
   - Requires manual mapping
   - Should be added to YAML file

## Error Handling

- **YAML file missing**: Script exits with error message
- **EUC_ESOL.xlsx missing**: Script exits with error message
- **PYTHON EMEA Locations.xls missing**: Script continues with warning
- **Missing Site Location column**: Script exits with available columns listed
- **Invalid YAML format**: Script exits with parsing error

## Dependencies

- `pandas`: Excel file reading and data manipulation
- `yaml`: YAML file parsing
- `pathlib`: File path handling
- `difflib`: String similarity calculation

## Best Practices

1. **Keep YAML file updated**: Add new sites to YAML for accurate mappings
2. **Review unmapped sites**: Check unmapped sites and add to YAML if needed
3. **Validate fuzzy matches**: Review fuzzy matches before using them
4. **Check output CSV**: Verify mapping results in the exported CSV file

## Troubleshooting

### Issue: "Could not find 'Site Location' column"
**Solution**: Check that EUC_ESOL.xlsx has a column containing "site" and "location" (case-insensitive)

### Issue: "Error loading YAML file"
**Solution**: Verify YAML file syntax is correct and file exists at `config/esol_sites_mapped.yaml`

### Issue: Many unmapped sites
**Solution**: Add missing sites to the YAML file with proper mapping information

### Issue: Low mapping rate
**Solution**: 
- Review unmapped sites
- Add missing mappings to YAML file
- Check for typos or naming inconsistencies

## Example YAML Entry

```yaml
- Site Location: Belval
  Site Name: Belval - Luxembourg
  Location: Belval
  Country: Luxembourg
  SDM: Gauthier, Guillaume
```

## Notes

- The script prioritizes YAML mappings over fuzzy matching
- Fuzzy matching is only used as a fallback for sites not in YAML
- The PYTHON EMEA Locations.xls file is optional and used for reference only
- All output is written to `data/processed/` directory

