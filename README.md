# 🟣 Command Conqueror CTF — Linux Handbook CLI CTF

<center>

![Pixel Art](https://media.tenor.com/95NWCn_bppQAAAAj/pengu-pudgy.gif)

<center>

```text
  ______                                                                   __         ______                                                                                  
 /      \                                                                 /  |       /      \                                                                                 
/$$$$$$  |  ______   _____  ____   _____  ____    ______   _______    ____$$ |      /$$$$$$  |  ______   _______    ______   __    __   ______    ______    ______    ______  
$$ |  $$/  /      \ /     \/    \ /     \/    \  /      \ /       \  /    $$ |      $$ |  $$/  /      \ /       \  /      \ /  |  /  | /      \  /      \  /      \  /      \ 
$$ |      /$$$$$$  |$$$$$$ $$$$  |$$$$$$ $$$$  | $$$$$$  |$$$$$$$  |/$$$$$$$ |      $$ |      /$$$$$$  |$$$$$$$  |/$$$$$$  |$$ |  $$ |/$$$$$$  |/$$$$$$  |/$$$$$$  |/$$$$$$  |
$$ |   __ $$ |  $$ |$$ | $$ | $$ |$$ | $$ | $$ | /    $$ |$$ |  $$ |$$ |  $$ |      $$ |   __ $$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |$$    $$ |$$ |  $$/ $$ |  $$ |$$ |  $$/ 
$$ \__/  |$$ \__$$ |$$ | $$ | $$ |$$ | $$ | $$ |/$$$$$$$ |$$ |  $$ |$$ \__$$ |      $$ \__/  |$$ \__$$ |$$ |  $$ |$$ \__$$ |$$ \__$$ |$$$$$$$$/ $$ |      $$ \__$$ |$$ |      
$$    $$/ $$    $$/ $$ | $$ | $$ |$$ | $$ | $$ |$$    $$ |$$ |  $$ |$$    $$ |      $$    $$/ $$    $$/ $$ |  $$ |$$    $$ |$$    $$/ $$       |$$ |      $$    $$/ $$ |      
 $$$$$$/   $$$$$$/  $$/  $$/  $$/ $$/  $$/  $$/  $$$$$$$/ $$/   $$/  $$$$$$$/        $$$$$$/   $$$$$$/  $$/   $$/  $$$$$$$ | $$$$$$/   $$$$$$$/ $$/        $$$$$$/  $$/       
                                                                                                                        $$ |                                                  
                                                                                                                        $$ |                                                  
                                                                                                                        $$/                                                                  

         A sleek terminal-first Capture The Flag experience
```

💜 Welcome to **Command Conqueror CTF** — a compact, terminal-native CTF platform with isolated Docker challenge environments and a lightweight Go backend, powered by Linux Handbook.

---

## What this project is
- Terminal-first CTF: play entirely in your shell — no browser required.
- Each challenge runs in its own Docker container for safety and reproducibility.
- Backend (Go) validates flags, tracks scores and progression; CLI client (Python) orchestrates gameplay.

---

## Key Features
- 🐍 CLI client: interactive session, shell attach, flag submission
- 🐳 Dockerized challenges: one container per level for isolation
- 🏆 Live leaderboard: view top players from the terminal
- 🔄 Persistent progress: user state stored in MongoDB
- ⚡ Fast backend: written in Go for concurrency and performance

---

## Quick local run (client-only)
Requirements: Python 3.7+, Docker running, network access.

```bash
git clone https://github.com/linuxhandbook/command-conqueror-CTF-frontend.git
cd command-conqueror-CTF-frontend
sudo python3 play.py
```

The client will guide you through initial setup (pulling challenge images) and then open an interactive play session.

---

## In-game commands
While in a level prompt (e.g. `ctf-1>`):

- `submit flag{...}` — submit a flag
- `play` — open an interactive bash shell inside the challenge container
- `leaderboard` — show top 10 players (nice purple-styled table)
- `restart` — reset your progress to level 1 (if enabled)
- `delete` — delete your user account (removes local saved username)
- `exit` — leave current level session

---

## Tech Stack
- Backend: Go 1.20+ (single binary)
- Client: Python 3 (CLI)
- Database: MongoDB (Atlas or local)
- Containers: Docker for challenge isolation

---

## Challenges (summary)
| # | Difficulty | Points |
|---:|:----------:|:------:|
| 1  | ⭐ Beginner | 100 |
| 2  | ⭐ Beginner | 150 |
| 3  | ⭐⭐ Easy    | 200 |
| 4  | ⭐⭐ Easy    | 250 |
| 5  | ⭐⭐⭐ Medium | 300 |
| 6  | ⭐⭐⭐ Medium | 350 |
| 7  | ⭐⭐⭐⭐ Hard  | 400 |
| 8  | ⭐⭐⭐⭐ Hard  | 450 |
| 9  | ⭐⭐⭐⭐⭐ Expert | 500 |
| 10 | ⭐⭐⭐⭐⭐ Expert | 1000 |

Total points: **4350**

---

## Env vars (backend)
- `MONGODB_URI` — MongoDB connection string (required)
- `PORT` — optional, default 10000

> ⚠️ Never commit secrets to the repository. Use environment variables or secret stores.

---


## Contributing
- Fork the repo, create a branch, open a PR.
- Keep secrets out of commits. Run linters and basic tests before PR.

---

## License
MIT — free for educational and non-commercial use.

---

Happy hacking — keep it purple, keep it safe. 💜
