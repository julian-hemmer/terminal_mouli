import data_finder
import token_updater
import curses
import mouli_displayer
import traceback

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