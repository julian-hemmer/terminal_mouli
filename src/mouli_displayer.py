import curses
import data_finder
import math
import time
import datetime
import threading
import tzlocal

current_data      = None
last_data_update  = 0
data_update_delay = 30
current_data_url  = ""

last_screen_update  = 0
screen_update_delay = 1 / 60

has_network_error = False

target_start = 0

update_data_thread = None

project_aliases = {
    "Bootstrap - ": "Bs-"
}

def cprint(stdscr: curses.window, text, y = None, x = None, modifier = 0, overflow_rule = "none"):
    current_y, current_x = stdscr.getyx()
    max_y, max_x = stdscr.getmaxyx()
    was_any_none = False

    if y == None or x == None:
        y = 0
        x = 0
        was_any_none = True
    
    overflow_rule = overflow_rule.lower() if overflow_rule != None else ""
    if overflow_rule != "none":
        if overflow_rule == "cut":
            text = text[:min(max_x - current_x - 1, len(text))]
        elif overflow_rule == "hide":
            if current_x + len(text) > max_x:
                curses.setsyx(current_y, max_x)
                return

    if max_x - current_x > len(text) and current_y == max_y:
        text = text[:min(max(max_x - current_x, 0), len(text))]

    if x < 0 or y < 0 or y >= max_y:
        return

    if was_any_none:
        stdscr.addstr(f"{text}", modifier)
    else:
        stdscr.addstr(y, x, text, modifier)

def loading(stdscr: curses.window, data):
    max_y, max_x = stdscr.getmaxyx()
    max_point_count = 3
    point_count = math.floor(data["frames_counter"] / 60) % max_point_count + 1

    x = math.floor(max_x / 2 - len("│ Loading... │") / 2)
    y = math.floor(max_y / 3 + 1)

    gray = curses.color_pair(244)
    bold_gray = gray | curses.A_BOLD

    cprint(stdscr, f"┌{"─" * (len("│ Loading... │") - 2)}┐", y, x, modifier = bold_gray, overflow_rule = "cut")

    cprint(stdscr, f"│ ", y + 1, x, bold_gray, overflow_rule = "cut")
    cprint(stdscr, f"Loading", modifier = gray, overflow_rule = "cut")
    cprint(stdscr, f"{"." * point_count}", modifier = gray, overflow_rule = "cut")
    cprint(stdscr, f"{" " * (max_point_count - point_count)}", modifier = gray, overflow_rule = "cut")
    cprint(stdscr, f" │", modifier = bold_gray, overflow_rule = "cut")

    cprint(stdscr, f"└{"─" * (len("│ Loading... │") - 2)}┘", y + 2, x, modifier = bold_gray, overflow_rule = "cut")


def network_error(stdscr: curses.window, data):
    max_y, max_x = stdscr.getmaxyx()
    colors = [i for i in range(196, 201 + 1, 1)]
    current_color_index = math.floor(data["frames_counter"] / 20) % (len(colors) * 2 - 2)
    if current_color_index > len(colors) - 1:
        current_color_index = (len(colors) * 2 - 2) - current_color_index

    x = math.floor(max_x / 2 - len("│ Network Error │") / 2)
    y = math.floor(max_y / 3 + 1)

    color = curses.color_pair(colors[current_color_index])
    bold_color = color | curses.A_BOLD

    cprint(stdscr, f"┌{"─" * (len("│ Network Error │") - 2)}┐", y, x, modifier = bold_color, overflow_rule = "hide")

    cprint(stdscr, f"│ ", y + 1, x, bold_color, overflow_rule = "hide")
    cprint(stdscr, f"Network Error", modifier = color, overflow_rule = "hide")
    cprint(stdscr, f" │", modifier = bold_color, overflow_rule = "hide")

    cprint(stdscr, f"└{"─" * (len("│ Network Error │") - 2)}┘", y + 2, x, modifier = bold_color, overflow_rule = "hide")

def update_data(url, data, force, stdscr: curses.window):
    global current_data, last_data_update, current_data_url, update_data_thread, has_network_error

    while True:
        try:
            current_data = data_finder.ecofetch_data(data["token"], f"{data_finder.base_url}/{url}", force)
            has_network_error = False
            current_data["data"].reverse()
            last_data_update = time.time()
            current_data_url = url
            break
        except:
            has_network_error = True
    update_data_thread = None

def get_data(url, data, stdscr: curses.window, force = False):
    global current_data, last_data_update, current_data_url, update_data_thread, has_network_error

    if time.time() - last_data_update > data_update_delay or force or current_data_url != url:
        if has_network_error:
            network_error(stdscr, data)
        else:
            loading(stdscr, data)
        if update_data_thread != None:
            return
        update_data_thread = threading.Thread(args = (url, data, force, stdscr), target = update_data, daemon = False)
        update_data_thread.start()
    return current_data

def load():
    global target_start
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

    target_start = max(math.ceil(curses.LINES / 6) + 1, 8)
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
    data["frames_counter"] = data.get("frames_counter", 0) + 1
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
            data["start_line"] -= 1
        if typed_char == curses.KEY_UP:
            data["start_line"] += 1
        typed_char = stdscr.getch()

def get_project_ratio(project):
    passed = 0.0    
    total = 0.0

    for result in project["results"]["skills"]:
        total  += int(project["results"]["skills"][result]["count"])
        passed += int(project["results"]["skills"][result]["passed"])
    if total <= 0:
        return -1.0
    return (passed / total)

def parse_procect_aliases(name):
    global project_aliases

    for alias in project_aliases:
        name = name.replace(alias, project_aliases[alias])
    return name

def get_color_from_ratio(ratio):
    if ratio > 0.7: 
        return curses.color_pair(2)
    elif ratio > 0.3: 
        return curses.color_pair(3)
    return curses.color_pair(1)

def render_project_bar(stdscr: curses.window, y, x, project_data, modifier, length = -1, use_alias = True):
    if length == -1:
        length = int(curses.COLS / 4)
    length = length - 2 - 2 - 2 # -2 for the space and -2 for the '[', ']' and -2 for space (|' '{name}' '|)
    name = project_data["project"]["name"]
    if use_alias:
        name = parse_procect_aliases(name)
    name = name[:(max(length - 4 - 2, 0))].strip() # -4 At least 4 bar ('|'), -2 for space
    name_length = len(name)
    ratio = get_project_ratio(project_data)
    color = get_color_from_ratio(ratio)

    name = (math.ceil((length - name_length) / 2) * "|") + f" {name} " + (math.floor((length - name_length) / 2) * "|")

    cprint(stdscr, "[ ", y, x, curses.color_pair(3) | curses.A_BOLD, overflow_rule = "cut")
    cprint(stdscr, f"{name[:int(len(name) * ratio)]}", modifier = color | modifier, overflow_rule = "cut")
    cprint(stdscr, f"{name[int(len(name) * ratio):]}", modifier = curses.color_pair(244) | modifier, overflow_rule = "cut")
    cprint(stdscr, " ]", modifier = curses.color_pair(3) | curses.A_BOLD, overflow_rule = "cut")

def render_separation(stdscr: curses.window, data, list_offset_top, list_offset_down):
    max_y, max_x = stdscr.getmaxyx()
    padding = 3
    x = int(curses.COLS / 4) + padding
    middle_bar_pos = target_start - 1

    middle_bar_pos -= 1 # offset the bar by one
    for y in range(0, max_y):
        cprint(stdscr, "|###", y, x, curses.color_pair(244))
        if y > middle_bar_pos and y - middle_bar_pos < 4:
            current_y, current_x = stdscr.getyx()
            length = ((curses.COLS - 1) - current_x)
            if y - middle_bar_pos == 2:
                cprint(stdscr, f"{">" * (length - 1)}", modifier = curses.color_pair(1), overflow_rule = "cut")
                cprint(stdscr, f"|", modifier = curses.color_pair(244), overflow_rule = "cut")
            elif y - middle_bar_pos == 1:
                cprint(stdscr, f"⮤{"_" * (length - 2)}", modifier = curses.color_pair(244), overflow_rule = "cut")
            elif y - middle_bar_pos == 3:
                cprint(stdscr, f"⮦{"‾"* (length - 2)}", modifier = curses.color_pair(244), overflow_rule = "cut")
        else:
            cprint(stdscr, "|", modifier = curses.color_pair(244))

    cprint(stdscr, "", target_start, int(curses.COLS / 4) + 4, curses.color_pair(1))
    arrow_length = 4
    arrow_spacement = 10
    arrow_speed = 7
    for i in range(0, curses.COLS - (int(curses.COLS / 4) + 4) - 2):
        color = 244
        if (math.ceil(data["frames_counter"] / (60 / arrow_speed)) - i) % (arrow_spacement + arrow_length) < arrow_length:
            color = 1
        cprint(stdscr, ">", modifier = curses.color_pair(color))


def get_elapsed_time_formatted(timestamp):
    
    timestamp = datetime.datetime.strptime(timestamp, 
        "%Y-%m-%dT%H:%M:%SZ").astimezone(tzlocal.get_localzone()).timestamp()
    current_time = time.time()
    elapsed_time = current_time - timestamp

    if elapsed_time < 60:
        return f"{elapsed_time:.0f} Sec"
    elif elapsed_time < 3600:
        return f"{(elapsed_time / 60):.0f} Min"
    elif elapsed_time < 86400:
        return f"{(elapsed_time / 3600):.0f} H, {((elapsed_time % 3600) / 60):.0f} m"
    return f"{(elapsed_time / 86400):.0f} Day"

def get_extitem_value(project_info, target):
    for ext_item in project_info["results"]["externalItems"]:
        if ext_item["type"] == target:
            return ext_item["value"]
    return 0

def render_target_info(stdscr: curses.window, target_data):
    start_x = int(curses.COLS / 4) + 8
    width = curses.COLS - start_x

    project_ratio = get_project_ratio(target_data)
    ratio_color = get_color_from_ratio(project_ratio)
    bold_ratio_color = ratio_color | curses.A_BOLD
    bold_gold = curses.color_pair(3) | curses.A_BOLD
    bold_gray = curses.color_pair(244) | curses.A_BOLD
    bold_magenta = curses.color_pair(147) | curses.A_BOLD
    bold_dark_green = curses.color_pair(22) | curses.A_BOLD
    cyan = curses.color_pair(6)
    red = curses.color_pair(1)
    bold_red = red | curses.A_BOLD

    cprint(stdscr, format_string(f"{get_elapsed_time_formatted(target_data["date"])} ⌛", width - 10, "right"), 1, start_x + 5, modifier = curses.color_pair(217))

    prerequisites = target_data["results"]["prerequisites"]
    if prerequisites == 2.0:
        cprint(stdscr, f"🔵 Prerequisites Met", 1, start_x + 4, modifier = cyan)
    elif prerequisites == 1.5:
        cprint(stdscr, f"🔴 Crashed", 1, start_x + 4, modifier = bold_red)
    elif prerequisites == 1.0:
        cprint(stdscr, f"🔴 No Test Passed", 1, start_x + 4, modifier = red)
    elif prerequisites == 0.5:
        cprint(stdscr, f"🔴 Delivery Error", 1, start_x + 4, modifier = red)
    elif prerequisites == 0.0:
        cprint(stdscr, f"🔴 Banned Function", 1, start_x + 4, modifier = red)

    #second_line_len = len(f"[ {target_data["project"]["module"]["code"]} ]") + len(" [ 100.00% ]")
    second_line_len = len(f"[ {target_data["project"]["module"]["code"]} ]")

    cprint(stdscr, f" [ ", 2, (start_x - 1) + math.ceil(width / 2 - second_line_len), modifier = bold_gold, overflow_rule = "cut")
    cprint(stdscr, f"{target_data["project"]["module"]["code"]}", modifier = bold_dark_green, overflow_rule = "cut")
    cprint(stdscr, f" ]", modifier = bold_gold, overflow_rule = "cut")

    cprint(stdscr, f" [ ", modifier = bold_gold, overflow_rule = "cut")
    cprint(stdscr, f"{(project_ratio * 100):.2f}%", modifier = bold_ratio_color, overflow_rule = "cut")
    cprint(stdscr, f" ] ", modifier = bold_gold, overflow_rule = "cut")

    cprint(stdscr, f" [ ", 1, (start_x - 1) + math.ceil(width / 2 - len(f"[ {target_data["project"]["name"]} ]") / 2), modifier = bold_gold, overflow_rule = "cut")
    cprint(stdscr, f"{target_data["project"]["name"]}", modifier = bold_magenta, overflow_rule = "cut")
    cprint(stdscr, f" ]", modifier = bold_gold, overflow_rule = "cut")

    completion_len = max(math.floor((width - 10) * project_ratio), 0)

    cprint(stdscr, "╷", 3, start_x + 4, modifier = bold_gray)
    cprint(stdscr, "▁" * completion_len, modifier = ratio_color)
    cprint(stdscr, " " * ((width - 10) - completion_len))
    cprint(stdscr, "╷", modifier = bold_gray)

    cprint(stdscr, "└", 4, start_x + 4, modifier = bold_gray)
    cprint(stdscr, "─" * (width - 10), modifier = bold_gray)
    cprint(stdscr, "┘", modifier = bold_gray)

    cprint(stdscr, "│", 5, start_x + 4, modifier = bold_gray)
    cov_line = get_extitem_value(target_data, "coverage.lines")
    cov_branches = get_extitem_value(target_data, "coverage.branches")
    cprint(stdscr, f" {cov_line:.1f}", modifier = get_color_from_ratio(cov_line / 100))
    cprint(stdscr, f" │ ", modifier = bold_gray)
    cprint(stdscr, f"{cov_branches:.1f}", modifier = get_color_from_ratio(cov_line / 100))
    cprint(stdscr, f" │ ", modifier = bold_gray)

def format_string(string, length, alignement = "left"):
    alignement = alignement.lower()
    remaining_len = length - len(string)

    if alignement == "right":
        return (" " * remaining_len) + string
    elif alignement == "centered":
        return (" " * math.ceil(remaining_len / 2)) + string + (" " * math.floor(remaining_len / 2))
    else:
        return string + (" " * remaining_len)

def draw_info_box(stdscr: curses.window, list_offset_top, list_offset_down):
    start_box_up = target_start - list_offset_top - 2
    start_box_down = target_start + list_offset_down + 2

    width = int(curses.COLS / 4) - 2
    x = 1

    gray = curses.color_pair(244)
    bold_gray = gray | curses.A_BOLD

    cprint(stdscr, f"{"- ↑"}", start_box_up + 1, x + math.ceil((width - len("- ↑ UP ↑ -")) / 2), bold_gray)
    cprint(stdscr, f"{" UP "}", modifier = gray)
    cprint(stdscr, f"{"↑ -"}", modifier = bold_gray)

    ######################

    cprint(stdscr, f"{"- ↓"}", start_box_down - 1, x + math.ceil((width - len("- ↓ DOWN ↓ -")) / 2), bold_gray)
    cprint(stdscr, f"{" DOWN "}", modifier = gray)
    cprint(stdscr, f"{"↓ -"}", modifier = bold_gray)

def main_panel(data, stdscr: curses.window):
    global data_update_delay, last_data_update
    mouli_data = get_data("2024", data, stdscr)

    if data.get("start_line", None) == None:
        data["start_line"] = target_start

    main_panel_keyhandler(data, stdscr)

    if mouli_data == None:
        return

    list_offset_top = 3
    list_offset_down = 3

    current_line = -1
    index = (data.get("start_line", target_start)) + 1
    amount_of_project = len(mouli_data["data"])

    render_separation(stdscr, data, list_offset_top, list_offset_down)

    index *= -1
    target_index = (data["start_line"] - target_start) * -1

    draw_info_box(stdscr, list_offset_top, list_offset_down)

    while True:
        current_line += 1
        index += 1
        if current_line >= curses.LINES or index > target_index + list_offset_down:
            break
        if index < target_index - list_offset_top:
            continue
        project = mouli_data["data"][index % amount_of_project]
        if index == target_index:
            render_project_bar(stdscr, current_line, 2, project, curses.A_BOLD)
            render_target_info(stdscr, project)
        else:
            render_project_bar(stdscr, current_line, 0, project, 0)

    cprint(stdscr, ">", target_start, 0, modifier = curses.color_pair(1))
    