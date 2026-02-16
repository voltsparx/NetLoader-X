import os
import time
from core.config import GlobalConfig
from core.engine import Engine
from core.profiles import HTTPSteady, HTTPBurst, SlowClient
from core.simulations import SimSlowloris, SimHTTPFlood, SimICMP
from ui.banner import show_banner
from ui.menu import main_menu
from ui.dashboard import live_dashboard

PROFILES = {
    "1": HTTPSteady(),
    "2": HTTPBurst(),
    "3": SlowClient(),
    "4": SimSlowloris(),
    "5": SimHTTPFlood(),
    "6": SimICMP(),
}

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def main():
    clear()
    show_banner()
    choice = main_menu()

    workload = PROFILES.get(choice)
    if not workload:
        print("Invalid choice")
        return

    threads = 50
    duration = 60

    engine = Engine()
    engine.configure("small-web", 
                    "HTTP" if isinstance(workload, HTTPSteady) else "BURST" if isinstance(workload, HTTPBurst) else "SLOW",
                    threads, duration)

    confirm = input("[?] Start simulation? (yes/no): ").lower()
    if confirm != "yes":
        return

    clear()
    engine.run()
    live_dashboard(engine)

if __name__ == "__main__":
    main()