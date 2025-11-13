# iLEAPP Automated Analysis Instructions for macOS

## Overview
This guide will help you run iLEAPP forensic analysis on your iOS backup using the automated script.

## Prerequisites
- Python 3.10 to 3.12 installed on your Mac
- iOS backup located at: `/Users/macbook/Desktop/library/Application Support/MobileSync/Backup/00008110-0001306901C0A01E`
- iLEAPP installed at: `/Applications/GitHub/iLEAPP/Forensics/iLEAPP`

## Quick Start

### Step 1: Copy the Script to Your Mac
Copy the `run_ileapp_analysis.sh` script from this repository to your Mac. You can save it anywhere, for example:
```bash
/Users/macbook/Desktop/run_ileapp_analysis.sh
```

### Step 2: Make the Script Executable
Open Terminal and run:
```bash
chmod +x /Users/macbook/Desktop/run_ileapp_analysis.sh
```

### Step 3: Run the Analysis
Execute the script:
```bash
/Users/macbook/Desktop/run_ileapp_analysis.sh
```

## What the Script Does

The automated script will:
1. ✅ Verify that all required paths exist
2. ✅ Check for Python 3 installation
3. ✅ Install/verify required dependencies
4. ✅ Run iLEAPP analysis on your iOS backup
5. ✅ Create timestamped output folder in `/Users/macbook/MVT-IOS/`
6. ✅ Automatically open the HTML report in your browser

## Output Location

Results will be saved to:
```
/Users/macbook/MVT-IOS/iLEAPP_Results_YYYYMMDD_HHMMSS/
```

The main report file will be:
```
/Users/macbook/MVT-IOS/iLEAPP_Results_YYYYMMDD_HHMMSS/index.html
```

## Customizing the Script

If your paths are different, edit the script and update these variables:

```bash
# iLEAPP installation directory
ILEAPP_DIR="/Applications/GitHub/iLEAPP/Forensics/iLEAPP"

# iOS backup path
BACKUP_PATH="/Users/macbook/Desktop/library/Application Support/MobileSync/Backup/00008110-0001306901C0A01E"

# Output directory
MVT_DIR="/Users/macbook/MVT-IOS"
```

## Troubleshooting

### Python Not Found
If you get "python3 not found", install Python 3:
```bash
brew install python@3.12
```

### Dependencies Installation Fails
Manually install dependencies:
```bash
cd /Applications/GitHub/iLEAPP/Forensics/iLEAPP
python3 -m pip install -r requirements.txt
```

### Backup Path Error
Verify your backup exists:
```bash
ls -la "/Users/macbook/Desktop/library/Application Support/MobileSync/Backup/00008110-0001306901C0A01E"
```

### Permission Denied
Make sure the script is executable:
```bash
chmod +x run_ileapp_analysis.sh
```

## Manual Command (Alternative)

If you prefer to run iLEAPP manually without the script:

```bash
cd /Applications/GitHub/iLEAPP/Forensics/iLEAPP
python3 ileapp.py -t fs \
    -i "/Users/macbook/Desktop/library/Application Support/MobileSync/Backup/00008110-0001306901C0A01E" \
    -o "/Users/macbook/MVT-IOS/iLEAPP_Results"
```

## Additional Options

For more iLEAPP options, run:
```bash
cd /Applications/GitHub/iLEAPP/Forensics/iLEAPP
python3 ileapp.py --help
```

## Analysis Time

Depending on the size of your iOS backup, the analysis may take:
- Small backups (< 5GB): 2-5 minutes
- Medium backups (5-20GB): 5-15 minutes
- Large backups (> 20GB): 15-30+ minutes

## Results

The analysis will generate:
- HTML report with interactive interface
- TSV (tab-separated) files for each artifact
- Timeline data
- KML files for location data (if available)
- LAVA format output

## Support

For issues with iLEAPP itself, visit:
- GitHub: https://github.com/abrignoni/iLEAPP
- Blog: https://abrignoni.blogspot.com/
