import curses
import data_finder
import math
import time

current_data      = None
last_data_update  = 0
data_update_delay = 30
current_data_url  = ""

last_screen_update  = 0
screen_update_delay = 1 / 60

def loading(stdscr: curses.window):
    stdscr.addstr(0, 0, f"Loading...", curses.color_pair(244))

def get_data(url, data, stdscr: curses.window, force = False):
    global current_data, last_data_update, current_data_url

    if time.time() - last_data_update > data_update_delay or force or current_data_url != url:
        loading(stdscr)
        stdscr.refresh()
        current_data = data_finder.ecofetch_data(data["token"], f"{data_finder.base_url}/{url}", force)
        current_data["data"].reverse()
        stdscr.clear()
        last_data_update = time.time()
        current_data_url = url

    return current_data

def load():
    stdscr = curses.initscr()

    stdscr.keypad(True)
    stdscr.nodelay(True)
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)

    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i, i, -1)

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
    curses.update_lines_cols()

def main_panel_keyhandler(data, stdscr: curses.window):
    typed_char = stdscr.getch()
    while typed_char != -1:
        if typed_char == ord('q'):
            data["running"] = False

        if typed_char == curses.KEY_DOWN:
            data["start_line"] = data.get("start_line", int(curses.LINES / 2)) - 1
        if typed_char == curses.KEY_UP:
            data["start_line"] = data.get("start_line", int(curses.LINES / 2)) + 1
        typed_char = stdscr.getch()

def render_project(stdscr: curses.window, y, x, project_data):
    length = int(curses.COLS / 4)
    
    stdscr.addstr(y, x, f"[", curses.color_pair(3))
    stdscr.addstr(f"{"|" * (length - 2)}", curses.color_pair(244))
    stdscr.addstr("]", curses.color_pair(3))

def render_separation(stdscr: curses.window):
    padding = 3
    x = int(curses.COLS / 4) + padding

    for y in range(0, curses.LINES):
        stdscr.addstr(y, x, "|###|", curses.color_pair(244))

def main_panel(data, stdscr: curses.window):
    global data_update_delay, last_data_update
    data["frames_counter"] = data.get("frames_counter", 0) + 1
    mouli_data = get_data("2024", data, stdscr)

    main_panel_keyhandler(data, stdscr)

    current_line = -1
    index = (data.get("start_line", int(curses.LINES / 2))) + 1
    amount_of_project = len(mouli_data["data"])

    stdscr.addstr(int(curses.LINES / 2), int(curses.COLS / 4), "-->", curses.color_pair(1))

    render_separation(stdscr)

    index *= -1
    while True:
        current_line += 1
        index += 1
        if current_line < 0:
            continue
        project = mouli_data["data"][index % amount_of_project]
        project_info = project["project"]
        if current_line >= curses.LINES:
            break
        render_project(stdscr, current_line, 0, project_info)
        stdscr.addstr(current_line, 
            int(curses.COLS / 2 - len(project_info["name"]) / 2), f"{project_info["name"]}",
            curses.color_pair(2))
        
    target_index = (data.get("start_line", int(curses.LINES / 2)) - int(curses.LINES / 2)) * -1
    stdscr.addstr(1, 1, 
                  f"|{data["frames_counter"]}|" +
                  f"{data.get("start_line", int(curses.LINES / 2)) - 1}|" +
                  f"{mouli_data["data"][target_index % amount_of_project]["project"]["name"]}|" +
                  f"{int(time.time())}|" + 
                  f"{last_data_update}|" +
                  f"{data_update_delay}|", 
                  curses.color_pair(3))

    