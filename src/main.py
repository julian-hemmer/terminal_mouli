import data_finder
import token_updater
import curses
import mouli_displayer
import traceback

def get_percent(mouli):
    passed = 0.0    
    total = 0.0

    for result in mouli["results"]["skills"]:
        total  += int(mouli["results"]["skills"][result]["count"])
        passed += int(mouli["results"]["skills"][result]["passed"])
    if total <= 0:
        return -1.0
    return (passed / total) * 100.0

def parse_data(mouli):
    return f"{mouli["project"]["name"]}:{get_percent(mouli)}\n"

def main():
    data = {}
    data["token"] = token_updater.load_token()
    data["running"] = True

    stdscr = mouli_displayer.load()
    try:
        while data["running"]:
            mouli_displayer.renderer(data, stdscr)
    except Exception as e:
        mouli_displayer.unload(stdscr)
        traceback.print_exc()
        print(e)
    else:
        mouli_displayer.unload(stdscr)

if __name__ == "__main__":
    main()