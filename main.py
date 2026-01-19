import sys
import time
from termcolor import colored
import data_manager
import simulation

def print_header():
    print(colored(r"""
   (                 ,&&&.
    )                .,&&&&.
   (  (              &&&&&&&&
    )  )             &&&&&&&&&       FOREST SENTINEL
  ( ( (              '&&&/&&&'       COMMAND CONSOLE
   ) ) )              |  |  |          V.2026.LC
    ) (               |  |  |
    | |         .-----'  |  '-----.
   /   \       /                   \
   |   |       |   STATION: 9820   |
   |___|       |    LOUGH OULER    |
  [_____]      \___________________/
    """, "green"))

def main_menu():
    while True:
        print("\n" + "="*40)
        print(colored("       MAIN CONTROL MENU", "white", attrs=['bold']))
        print("="*40)
        print(colored("[1]", "cyan"), "Load & View Micro:bit Field Data")
        print(colored("[2]", "cyan"), "Run Fire Risk Simulation (Weather API)")
        print(colored("[3]", "cyan"), "View 'What-If' Disaster Scenarios")
        print(colored("[4]", "cyan"), "Export Daily Safety Report")
        print(colored("[5]", "red"), "EXIT")
        
        choice = input(colored("\n>> ENTER COMMAND: ", "yellow"))
        
        if choice == '1':
            df = data_manager.get_microbit_data()
            if not df.empty:
                df = simulation.calculate_fire_risk_microbit(df)
                simulation.plot_microbit(df)
            else:
                input("Press Enter to continue...")

        elif choice == '2':
            df = data_manager.get_weather_data()
            if not df.empty:
                df = simulation.calculate_fire_risk_weather(df)
                # Show simple plot for option 2 (reuse the microbit plotter style or make new one)
                # For now, let's just show the scenario plot but focus on the green line
                simulation.plot_weather_scenarios(df) 
            else:
                input("Press Enter to continue...")

        elif choice == '3':
            df = data_manager.get_weather_data()
            if not df.empty:
                df = simulation.run_what_if_scenarios(df)
                simulation.plot_weather_scenarios(df)
            else:
                input("Press Enter to continue...")
        
        elif choice == '4':
            df = data_manager.get_weather_data()
            if not df.empty:
                df = simulation.calculate_fire_risk_weather(df)
                simulation.generate_report(df)
                print(colored(">> REPORT GENERATED SUCCESSFULLY.", "green"))
            else:
                print("No data to report on.")
        
        elif choice == '5':
            print(colored(">> SHUTTING DOWN SYSTEM...", "red"))
            time.sleep(1)
            sys.exit()
        
        else:
            print("Invalid Command.")

if __name__ == "__main__":
    print_header()
    # Artificial loading delay for effect
    print(colored(">> INITIALIZING MODULES...", "yellow"))
    time.sleep(1)
    print(colored(">> SYSTEM ONLINE.", "green"))
    main_menu()