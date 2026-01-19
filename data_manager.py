import pandas as pd
import requests
import io
import os
from termcolor import colored

# CONFIGURATION
# Station 9820 (Lough Ouler/Wicklow Area)
# Note: If 9820 is not a 'Daily' reporting station, the API might fail. 
# The code handles this by using the backup.
STATION_ID = "9820" 
MET_EIREANN_URL = f"https://cli.fusio.net/cli/climate_data/webdata/dly{STATION_ID}.csv"
BACKUP_FILE = "backup_weather.csv"
MICROBIT_FILE = "microbit_log.csv"

def get_weather_data():
    """
    Attempts to download live rain/temp data from Met Eireann (Station 9820).
    Falls back to local backup if offline or station unavailable.
    """
    print(colored(f">> CONNECTING TO STATION {STATION_ID} (LOUGH OULER)...", "cyan"))
    
    try:
        # 1. Try Live Download
        response = requests.get(MET_EIREANN_URL, timeout=8)
        response.raise_for_status()
        
        # Met Eireann CSVs have ~15 lines of header text. We skip them.
        raw_data = io.StringIO(response.text)
        df = pd.read_csv(raw_data, skipinitialspace=True, skiprows=15)
        
        print(colored(">> [SUCCESS] LIVE DATA RECEIVED.", "green"))
        return df

    except Exception as e:
        print(colored(f">> [WARNING] CONNECTION FAILED: {e}", "yellow"))
        print(colored(">> [SYSTEM] ENGAGING FAILSAFE: LOADING LOCAL BACKUP...", "red"))
        
        if os.path.exists(BACKUP_FILE):
            # Load the backup file
            df = pd.read_csv(BACKUP_FILE, skipinitialspace=True, skiprows=15)
            return df
        else:
            print(colored(">> [ERROR] NO BACKUP FILE FOUND.", "red", attrs=['bold']))
            return pd.DataFrame() # Return empty if nothing works

def get_microbit_data():
    """
    Reads the specific CSV format dumped by your Micro:bit.
    Format: Time, Light (0-255), Temp
    """
    print(colored(">> READING MICROBIT FIELD DATA...", "cyan"))
    
    if os.path.exists(MICROBIT_FILE):
        try:
            # Load CSV. We explicitly name columns in case the file has no headers
            # Assuming file content is: 10, 180, 24 (Time, Light, Temp)
            df = pd.read_csv(MICROBIT_FILE, names=['Time', 'Light', 'Temp'], header=0)
            print(colored(f">> [SUCCESS] LOADED {len(df)} READINGS.", "green"))
            return df
        except Exception as e:
            print(colored(f">> [ERROR] CORRUPT DATA FILE: {e}", "red"))
            return pd.DataFrame()
    else:
        print(colored(">> [ERROR] 'microbit_log.csv' NOT FOUND.", "red"))
        return pd.DataFrame()
