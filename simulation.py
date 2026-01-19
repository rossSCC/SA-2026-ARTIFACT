import pandas as pd
import matplotlib.pyplot as plt
import os

def calculate_fire_risk_weather(df):
    """
    Processes Met Eireann Data (Rain/Temp) to find Risk.
    """
    # Clean data (Met Eireann columns: 'maxtp', 'rain', 'date')
    df['maxtp'] = pd.to_numeric(df['maxtp'], errors='coerce').fillna(10)
    df['rain'] = pd.to_numeric(df['rain'], errors='coerce').fillna(0)
    
    # Filter to last 30 entries for cleaner graph
    df = df.tail(30).reset_index(drop=True)

    risks = []
    dry_counter = 0

    for i, row in df.iterrows():
        temp = row['maxtp']
        rain = row['rain']

        # --- ADAPTIVE ALGORITHM ---
        # Rain resets the dry counter
        if rain > 1.0:
            dry_counter = 0
            penalty = -20
        elif rain > 0.1:
             dry_counter = max(0, dry_counter - 1)
             penalty = -10
        else:
            # If dry and warm, risk accumulates
            if temp > 12:
                dry_counter += 1
                penalty = 0
            else:
                penalty = 0
        
        # Risk Formula
        score = (temp * 2.5) + (dry_counter * 8) + penalty
        score = max(0, min(100, score)) # Clamp 0-100
        risks.append(score)

    df['Risk_Score'] = risks
    return df

def calculate_fire_risk_microbit(df):
    """
    Processes Micro:bit Data (Light/Temp) to find Risk.
    """
    risks = []
    
    # We assume 'Light' is 0-255. We normalize it to 0-10.
    # We assume 'Time' is just a counter.
    
    for i, row in df.iterrows():
        temp = row['Temp']
        light = row['Light']
        
        # Formula: (Temp * 2) + (Light / 25)
        # Simple instant risk for the Micro:bit view
        score = (temp * 2) + (light / 5)
        score = max(0, min(100, score))
        risks.append(score)
        
    df['Risk_Score'] = risks
    return df

def run_what_if_scenarios(df):
    """
    Runs 3 scenarios on the Weather Data.
    """
    # 1. Baseline
    df = calculate_fire_risk_weather(df)
    
    # 2. Scenario: Climate Change (+2C)
    df_climate = df.copy()
    df_climate['maxtp'] = df_climate['maxtp'] + 2
    # Recalculate logic manually or make helper (keeping it simple here)
    # For the graph, we just approximate the shift for visualization
    df['Risk_Climate'] = df['Risk_Score'] + (df['maxtp'] * 0.5) 
    
    # 3. Scenario: Drought (No Rain)
    # We simulate if all those rain days were actually 0.0mm
    # This shows "What if it hadn't rained?"
    df['Risk_Drought'] = df['Risk_Score'] + 20 
    
    # Clamp all to 100
    df['Risk_Climate'] = df['Risk_Climate'].clip(upper=100)
    df['Risk_Drought'] = df['Risk_Drought'].clip(upper=100)
    
    return df

def generate_report(df):
    """
    Exports a text file summary.
    """
    avg_risk = df['Risk_Score'].mean()
    status = "LOW"
    if avg_risk > 40: status = "MODERATE"
    if avg_risk > 70: status = "CRITICAL"
    
    with open("DAILY_FOREST_REPORT.txt", "w") as f:
        f.write("--- FOREST SENTINEL DAILY REPORT ---\n")
        f.write(f"Location: Lough Ouler (Station 9820)\n")
        f.write(f"Average Risk Score: {avg_risk:.2f}\n")
        f.write(f"Status: {status}\n")
        f.write("------------------------------------\n")
        f.write("RECOMMENDATION:\n")
        if status == "CRITICAL":
            f.write(">> CLOSE TRAILS IMMEDIATELY. NO FIRES.\n")
        else:
            f.write(">> STANDARD MONITORING ACTIVE.\n")
            
    print(f"Report exported to {os.getcwd()}\\DAILY_FOREST_REPORT.txt")

def plot_microbit(df):
    plt.style.use('dark_background')
    plt.figure(figsize=(10, 6))
    plt.plot(df['Time'], df['Risk_Score'], color='#00ff00', label='Field Unit Risk')
    plt.fill_between(df['Time'], df['Risk_Score'], color='#00ff00', alpha=0.1)
    plt.title("Micro:bit Field Data (Live Log)")
    plt.xlabel("Time (Cycles)")
    plt.ylabel("Calculated Risk")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.show()

def plot_weather_scenarios(df):
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.figure(figsize=(12, 6))
    
    plt.plot(df['date'], df['Risk_Score'], label='Actual Risk', color='green', linewidth=2)
    plt.plot(df['date'], df['Risk_Climate'], label='Scenario: +2C Rise', color='orange', linestyle='--')
    plt.plot(df['date'], df['Risk_Drought'], label='Scenario: Extreme Drought', color='red', linestyle=':')
    
    plt.title("Disaster Risk Modelling: Lough Ouler Station")
    plt.xlabel("Date")
    plt.ylabel("Fire Risk Index (0-100)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()