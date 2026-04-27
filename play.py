#!/usr/bin/env python3

import os
import sys
import subprocess
import threading
import time
import requests
import getpass
from threading import Semaphore

# ── ANSI palette ─────────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"

BCYAN   = "\033[96m"
BMAGENTA= "\033[95m"
BGREEN  = "\033[92m"
BYELLOW = "\033[93m"
BRED    = "\033[91m"
WHITE   = "\033[97m"
CYAN    = "\033[36m"
MAGENTA = "\033[35m"
GREEN   = "\033[32m"

# ── Constants ─────────────────────────────────────────────────
total_levels   = 10
user_file_path = os.path.expanduser("~/.ctf_user")
sem            = Semaphore(2)
levels_pulled  = 0
loading_done   = False
BACKEND_URL    = "https://ctf-backend-jrxl.onrender.com"

# ── UI helpers ───────────────────────────────────────────────
def clear():
    os.system("clear")

def cx(text, width):
    """Center text in given visible width (ignores ANSI codes)."""
    import re
    visible = re.sub(r'\033\[[0-9;]*m', '', text)
    pad = max(0, width - len(visible))
    left = pad // 2
    right = pad - left
    return ' ' * left + text + ' ' * right

def box_line(content, width=58):
    """Return a ║ content ║ row where content is padded to `width` visible chars."""
    import re
    visible_len = len(re.sub(r'\033\[[0-9;]*m', '', content))
    pad = max(0, width - visible_len)
    return f"  {BCYAN}║{RESET}{content}{' ' * pad}{BCYAN}║{RESET}"

def box_top(width=58):
    return f"  {BCYAN}╔{'═' * width}╗{RESET}"

def box_sep(width=58):
    return f"  {BCYAN}╠{'═' * width}╣{RESET}"

def box_bot(width=58):
    return f"  {BCYAN}╚{'═' * width}╝{RESET}"

def print_victory(user_id):
    """Full-screen congratulations banner shown when all levels are cleared."""
    clear()
    W = 58
    print()
    for line in LOGO:
        print(line)
    print(f"  {BMAGENTA}{'─' * W}{RESET}")
    print()
    print(f"  {BGREEN}{'═' * W}{RESET}")
    print(f"  {BGREEN}{BOLD}{'':^{W}}{RESET}")
    print(f"  {BGREEN}{BOLD}{'🎉  MISSION ACCOMPLISHED  🎉':^{W}}{RESET}")
    print(f"  {BGREEN}{BOLD}{'ALL 10 LEVELS CLEARED':^{W}}{RESET}")
    print(f"  {BGREEN}{BOLD}{'':^{W}}{RESET}")
    print(f"  {BGREEN}{'═' * W}{RESET}")
    print()
    print(box_top(W))
    print(box_line(cx(f"{BYELLOW}{BOLD}  Operator: {BCYAN}{user_id}{RESET}", W), W))
    print(box_line(cx(f"{DIM}You have conquered the CTF. Well played.{RESET}", W), W))
    print(box_bot(W))
    print()

# ── Boot art ─────────────────────────────────────────────────
LOGO = [
    f"{BCYAN}   ██████╗████████╗███████╗    {RESET}",
    f"{BCYAN}  ██╔════╝╚══██╔══╝██╔════╝    {RESET}",
    f"{BCYAN}  ██║        ██║   █████╗      {RESET}",
    f"{BCYAN}  ██║        ██║   ██╔══╝      {RESET}",
    f"{BCYAN}  ╚██████╗   ██║   ██║         {RESET}",
    f"{BCYAN}   ╚═════╝   ╚═╝   ╚═╝         {RESET}",
]

def print_boot():
    clear()
    print()
    for line in LOGO:
        print(line)
    W = 58
    print(f"  {BMAGENTA}{'─' * W}{RESET}")
    subtitle = cx(f"{BMAGENTA}{BOLD}  CAPTURE THE FLAG  //  LINUX HANDBOOK EDITION  {RESET}", W)
    print(f"  {subtitle}")
    print(f"  {BMAGENTA}{'─' * W}{RESET}")
    print()

# ── Login ────────────────────────────────────────────────────
def login():
    print_boot()
    W = 58
    print(box_top(W))
    print(box_line(cx(f"{BMAGENTA}{BOLD} 🔐  AUTHENTICATION REQUIRED {RESET}", W), W))
    print(box_sep(W))
    print(box_line(f"  {DIM}Credentials are case-sensitive. Authorised users only.{RESET}", W))
    print(box_bot(W))
    print()

    while True:
        username = input(f"  {BMAGENTA}USER {BCYAN}▶{RESET}  ").strip()
        password = getpass.getpass(f"  {BMAGENTA}PASS {BCYAN}▶{RESET}  ")
        print()
        try:
            resp = requests.post(
                f"{BACKEND_URL}/login",
                json={"username": username, "password": password},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    print(f"  {BGREEN}✔{RESET}  {BGREEN}Access granted.{RESET}  Welcome, {BCYAN}{BOLD}{username}{RESET}\n")
                    time.sleep(0.6)
                    with open(user_file_path, "w") as f:
                        f.write(username)
                    return username
                else:
                    print(f"  {BRED}✘{RESET}  {BRED}Invalid credentials. Try again.{RESET}\n")
            else:
                print(f"  {BRED}✘{RESET}  {BRED}Backend error (HTTP {resp.status_code}).  Try again.{RESET}\n")
        except Exception as e:
            print(f"  {BRED}✘{RESET}  {BRED}Connection error: {e}{RESET}\n")

# ── System checks ────────────────────────────────────────────
def check_internet():
    try:
        subprocess.check_call(["ping", "-c", "2", "google.com"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def are_you_sudo():
    return os.geteuid() == 0

def get_os():
    if sys.platform.startswith("linux"):
        try:
            with open("/etc/os-release") as f:
                lines = f.read().lower()
                for name, label in [("ubuntu","Ubuntu"), ("debian","Debian"),
                                     ("centos","CentOS"), ("red hat","RHEL"),
                                     ("fedora","Fedora"), ("arch","Arch")]:
                    if name in lines:
                        return label
        except:
            pass
    elif sys.platform == "darwin":
        return "MacOS"
    return "Unknown"

def restart_docker():
    os_type = get_os()
    if os_type == "MacOS":
        r = subprocess.call("brew services restart docker > /dev/null 2>&1", shell=True)
    else:
        r = subprocess.call("systemctl restart docker > /dev/null 2>&1", shell=True)
    return r == 0

def check_and_get_docker():
    if subprocess.call("docker images > /dev/null 2>&1", shell=True) == 0:
        return True
    if restart_docker():
        return True
    os_type = get_os()
    if os_type in ["Ubuntu", "Debian"]:
        subprocess.call("apt update && apt install -y docker.io curl > /dev/null 2>&1", shell=True)
    elif os_type in ["CentOS", "RHEL"]:
        subprocess.call("yum install -y docker curl > /dev/null 2>&1", shell=True)
    elif os_type == "Fedora":
        subprocess.call("dnf install -y docker curl > /dev/null 2>&1", shell=True)
    else:
        return False
    return restart_docker()

# ── Progress loader ──────────────────────────────────────────
def loader_animation():
    global loading_done, levels_pulled
    blocks  = " ▏▎▍▌▋▊▉█"
    spinner = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    BAR_W   = 20
    i = 0
    while not loading_done:
        frac = levels_pulled / total_levels
        filled = int(frac * BAR_W)
        bar = f"{BGREEN}{'█' * filled}{DIM}{'░' * (BAR_W - filled)}{RESET}"
        pct = int(frac * 100)
        sp  = spinner[i % len(spinner)]
        print(f"\r  {BCYAN}[{bar}{BCYAN}]{RESET}  {BYELLOW}{pct:3d}%{RESET}  "
              f"{BMAGENTA}{sp}{RESET}  {DIM}{levels_pulled}/{total_levels}{RESET}   ",
              end="", flush=True)
        i += 1
        time.sleep(0.12)
    print(f"\r  {BCYAN}[{BGREEN}{'█' * BAR_W}{BCYAN}]{RESET}  {BGREEN}100%  ✔  All levels loaded.{RESET}            ")

def pull_level(level):
    global levels_pulled
    tag   = f"war{level}"
    image = f"ghcr.io/yash09042004/ctf_challenge:{tag}"
    for _ in range(3):
        if subprocess.call(f"docker pull {image} > /dev/null 2>&1", shell=True) == 0:
            levels_pulled += 1
            return True
        time.sleep(3)
    return False

def pull_level_thread(level):
    sem.acquire()
    pull_level(level)
    sem.release()

def pull_levels():
    global loading_done, levels_pulled
    if not restart_docker():
        return False
    loading_done  = False
    levels_pulled = 0
    lt = threading.Thread(target=loader_animation)
    lt.start()
    threads = [threading.Thread(target=pull_level_thread, args=(i,))
               for i in range(1, total_levels + 1)]
    for t in threads: t.start()
    for t in threads: t.join()
    loading_done = True
    lt.join()
    return True

# ── Setup ────────────────────────────────────────────────────
def setup():
    if not are_you_sudo():
        print(f"\n  {BRED}✘{RESET}  Please run with {BCYAN}sudo{RESET}.\n")
        return 1
    print_boot()
    print(f"  {BCYAN}▸{RESET}  Checking network...          ", end="", flush=True)
    if not check_internet():
        print(f"\n  {BRED}✘{RESET}  No internet. Check connection.\n")
        return 1
    print(f"{BGREEN}OK{RESET}")

    print(f"  {BCYAN}▸{RESET}  Verifying Docker daemon...   ", end="", flush=True)
    if not check_and_get_docker():
        print(f"\n  {BRED}✘{RESET}  Docker unavailable.\n")
        return 1
    print(f"{BGREEN}OK{RESET}\n")

    print(f"  {BCYAN}▸{RESET}  Pulling challenge images:\n")
    if not pull_levels():
        print(f"\n  {BRED}✘{RESET}  Failed to pull levels.\n")
        return 1
    print()
    return 0

def check_file():
    if os.path.isfile(user_file_path):
        with open(user_file_path, "r") as f:
            return bool(f.read().strip())
    return False

# ── Backend API ──────────────────────────────────────────────
def get_current_level(user_id):
    try:
        resp = requests.get(f"{BACKEND_URL}/getLevel", params={"userId": user_id})
        if resp.status_code == 200:
            return resp.json().get("level", 1)
    except Exception as e:
        print(f"  {BRED}▸{RESET}  Backend error: {e}")
    return -1

def submit_flag(flag, user_id):
    try:
        resp = requests.post(f"{BACKEND_URL}/checkFlag",
                             json={"flag": flag, "userId": user_id})
        if resp.status_code == 200:
            r = resp.json()
            return r["correct"], r["newLevel"]
        return False, None
    except Exception as e:
        print(f"  {BRED}▸{RESET}  Error: {e}")
        return False, None

def reset_current_level(level_name, level_num, user_id):
    """Remove and restart only the current level container."""
    subprocess.call(f"docker rm -f {level_name} > /dev/null 2>&1", shell=True)
    start_container(level_name, level_num, user_id)

# ── Leaderboard ──────────────────────────────────────────────
def show_leaderboard():
    try:
        resp = requests.get(f"{BACKEND_URL}/api/leaderboard", timeout=10)
        if resp.status_code != 200:
            print(f"\n  {BRED}✘{RESET}  Leaderboard unavailable.\n")
            return
        users = resp.json()[:10]
    except Exception as e:
        print(f"\n  {BRED}✘{RESET}  {e}\n")
        return

    W      = 54
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    colors = {1: BYELLOW, 2: BCYAN, 3: BMAGENTA}

    print()
    print(box_top(W))
    print(box_line(cx(f"{BMAGENTA}{BOLD}  🏆  LEADERBOARD — TOP 10  🏆  {RESET}", W), W))
    print(box_sep(W))
    hdr = f"  {'#':>2}   {'USERNAME':<16}  {'SCORE':>8}  {'SOLVED':>6}  "
    print(box_line(f"{DIM}{hdr}{RESET}", W))
    print(box_sep(W))
    for idx, u in enumerate(users, 1):
        medal  = medals.get(idx, "  ")
        color  = colors.get(idx, WHITE)
        uname  = u.get("username", "?")[:15].ljust(15)
        score  = str(u.get("score", 0)).rjust(8)
        solved = str(len(u.get("solvedLevels", []))).rjust(6)
        row    = f"  {medal}{idx:>2}   {uname}  {score}  {solved}  "
        print(box_line(f"{color}{row}{RESET}", W))
    print(box_bot(W))
    print()

# ── Level HUD ────────────────────────────────────────────────
def print_level_hud(level_num, user_id):
    clear()
    W = 58
    print()
    print(box_top(W))
    print(box_line(cx(f"{BMAGENTA}{BOLD}  ◈  CTF // LEVEL {level_num:02d} of {total_levels:02d}  ◈  {RESET}", W), W))
    print(box_line(cx(f"{DIM}Operator: {BCYAN}{user_id}{RESET}", W), W))
    print(box_sep(W))
    cmds = [
        (f"{BCYAN}play{RESET}",          f"{DIM}Enter level shell (type 'exit' inside to return){RESET}"),
        (f"{BCYAN}submit <FLAG>{RESET}", f"{DIM}Submit a captured flag{RESET}"),
        (f"{BCYAN}leaderboard{RESET}",   f"{DIM}View top-10 ranking{RESET}"),
        (f"{BCYAN}restart{RESET}",       f"{DIM}Re-enter this level shell{RESET}"),
        (f"{BCYAN}help{RESET}",          f"{DIM}Show this reference panel{RESET}"),
    ]
    for cmd, desc in cmds:
        # Build the visible line manually (ANSI-aware)
        line = f"  {cmd}  —  {desc}"
        print(box_line(line, W))
    print(box_bot(W))
    print()

# ── Docker helpers ───────────────────────────────────────────
def start_container(level_name, level_num, user_id):
    tag   = f"war{level_num}"
    image = f"ghcr.io/yash09042004/ctf_challenge:{tag}"
    cmd   = (f"docker run -dit --hostname {user_id} --user root "
             f"--name {level_name} {image} tail -f /dev/null > /dev/null 2>&1")
    subprocess.call(cmd, shell=True)

def container_running(level_name):
    r = subprocess.call(
        f"docker ps --format '{{{{.Names}}}}' | grep -w {level_name} > /dev/null 2>&1",
        shell=True)
    return r == 0

def open_shell(level_name, level_num, user_id):
    if not container_running(level_name):
        subprocess.call(f"docker rm -f {level_name} > /dev/null 2>&1", shell=True)
        start_container(level_name, level_num, user_id)
    os.system(f"docker exec -it {level_name} bash")
    # docker exec can leave stdin in EOF state — restore it from the terminal
    try:
        sys.stdin = open("/dev/tty")
    except OSError:
        pass

def cleanup_level(level_name, level_num):
    """Remove container AND image after a level is cleared."""
    tag   = f"war{level_num}"
    image = f"ghcr.io/linuxhandbook/command-conqueror:{tag}"
    subprocess.call(f"docker rm -f {level_name} > /dev/null 2>&1", shell=True)
    subprocess.call(f"docker rmi {image} > /dev/null 2>&1", shell=True)

# ── Interactive level shell ───────────────────────────────────
def interactive_level_shell(level_name, level_num, user_id):
    # Ensure container exists
    exists = subprocess.call(
        f"docker ps -a --format '{{{{.Names}}}}' | grep -w {level_name} > /dev/null 2>&1",
        shell=True)
    if exists != 0:
        start_container(level_name, level_num, user_id)

    # Show HUD — user types 'play' to enter shell
    print_level_hud(level_num, user_id)
    prompt = f"  {BMAGENTA}[CTF:L{level_num:02d}]{RESET}{BCYAN}▶ {RESET}"

    while True:
        try:
            raw = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not raw:
            continue

        lower = raw.lower()

        # ── play ────────────────────────────────────────────
        if lower == "play":
            print(f"\n  {DIM}Launching shell — type {BCYAN}exit{DIM} to return here.{RESET}\n")
            time.sleep(0.3)
            open_shell(level_name, level_num, user_id)
            input(f"\n {BGREEN}Don't forget to COPY the flag... {DIM}Press {BCYAN}Enter{DIM} to return to the CTF menu...{RESET}")
            print_level_hud(level_num, user_id)

        # ── submit ───────────────────────────────────────────
        elif lower.startswith("submit "):
            flag = raw[7:].strip()
            if not flag:
                print(f"\n  {BRED}▸{RESET}  Usage: {BCYAN}submit FLAG{{...}}{RESET}\n")
                continue
            print(f"\n  {DIM}Verifying flag...{RESET}", end="", flush=True)
            correct, new_level = submit_flag(flag, user_id)
            if correct:
                print(f"\r  {BGREEN}✔  Flag accepted! Level {level_num} cleared.{RESET}\n")
                time.sleep(0.5)
                print(f"  {DIM}Cleaning up environment...{RESET}")
                cleanup_level(level_name, level_num)
                time.sleep(0.3)
                if new_level is not None and new_level > total_levels:
                    print_victory(user_id)
                    input(f"  {DIM}Press {BCYAN}Enter{DIM} to exit...{RESET}")
                return new_level
            else:
                print(f"\r  {BRED}✘  Incorrect flag. Keep digging.{RESET}\n")

        # ── leaderboard ──────────────────────────────────────
        elif lower == "leaderboard":
            show_leaderboard()

        # ── restart (same level, not from level 1) ───────────
        elif lower == "restart":
            print(f"\n  {DIM}Restarting level {level_num} environment...{RESET}\n")
            time.sleep(0.3)
            reset_current_level(level_name, level_num, user_id)
            open_shell(level_name, level_num, user_id)
            input(f"\n {BGREEN}Don't forget to COPY the flag... {DIM}Press {BCYAN}Enter{DIM} to return to the CTF menu...{RESET}")
            print_level_hud(level_num, user_id)

        # ── help ─────────────────────────────────────────────
        elif lower == "help":
            print_level_hud(level_num, user_id)

        else:
            print(f"\n  {BRED}▸{RESET}  Unknown command.  "
                  f"Type {BCYAN}help{RESET} to see available commands.\n")

    return level_num   # stay on same level if shell exits unexpectedly

# ── Main ─────────────────────────────────────────────────────
def main():
    if len(sys.argv) > 1 and sys.argv[1] == "-r":
        if os.path.isfile(user_file_path):
            os.remove(user_file_path)
        print(f"  {BYELLOW}▸{RESET}  Session cleared.\n")
        return

    if not check_file():
        if setup() != 0:
            return

    user_id = login()
    clear()
    print_boot()

    print(f"  {BCYAN}▸{RESET}  Connecting to backend...     ", end="", flush=True)
    current_level = get_current_level(user_id)
    if current_level == -1:
        print(f"\n  {BRED}✘{RESET}  Backend unreachable. Try again later.\n")
        return
    print(f"{BGREEN}OK{RESET}")

    print(f"  {BCYAN}▸{RESET}  Loading operator profile...  ", end="", flush=True)
    time.sleep(0.4)
    print(f"{BGREEN}OK{RESET}\n")
    time.sleep(0.3)

    # Already completed all levels on a previous run
    if current_level > total_levels:
        print_victory(user_id)
        input(f"  {DIM}Press {BCYAN}Enter{DIM} to exit...{RESET}")
        return

    while current_level <= total_levels:
        level_name = f"ctf{current_level}"
        new_level  = interactive_level_shell(level_name, current_level, user_id)
        if new_level is None:
            break
        if new_level > current_level:
            current_level = new_level
        else:
            break

    print_boot()
    W = 58
    if current_level > total_levels:
        print(f"  {BGREEN}{'═' * W}{RESET}")
        print(f"  {BGREEN}{BOLD}{'  🎉  ALL LEVELS CLEARED — MISSION ACCOMPLISHED  🎉  ':^{W}}{RESET}")
        print(f"  {BGREEN}{'═' * W}{RESET}\n")
    else:
        print(f"  {BMAGENTA}{'─' * W}{RESET}")
        print(f"  {BMAGENTA}{'  Session ended. Good luck next time.  ':^{W}}{RESET}")
        print(f"  {BMAGENTA}{'─' * W}{RESET}\n")

if __name__ == "__main__":
    main()