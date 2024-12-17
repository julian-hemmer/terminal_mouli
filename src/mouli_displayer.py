import curses
import data_finder
import main
import time

current_data = None
last_data_update  = 0
data_update_delay = 30

last_screen_update  = 0
screen_update_delay = 1 / 60


def get_data(url, data, force = False):
    global current_data

    if time.time() - last_data_update > data_update_delay or force:
        current_data = data_finder.ecofetch_data(data["token"], f"{data_finder.base_url}/{url}", force)

    return current_data

def load():
    stdscr = curses.initscr()

    stdscr.keypad(True)
    stdscr.nodelay(True)
    curses.noecho()
    curses.cbreak()

    return stdscr

def unload(stdscr: curses.window):
    curses.nocbreak()
    stdscr.keypad(False)
    stdscr.nodelay(False)
    curses.echo()
    curses.endwin()

def renderer(data, stdscr: curses.window):
    global last_screen_update, screen_update_delay
    current_time = time.time()
    if current_time - last_screen_update < screen_update_delay:
        return
    last_screen_update = current_time

    stdscr.clear()
    main_panel(data, stdscr)
    stdscr.refresh()

counter = 1

def main_panel(data, stdscr: curses.window):
    global counter
    mouli_data = get_data("2024", data)

    if stdscr.getch() == ord('q'):
        data["running"] = False

    stdscr.addstr(1, 1, f"|{counter}|{ord('q')}|{stdscr.getch()}|{data["running"]}|")
    counter += 1
    
    