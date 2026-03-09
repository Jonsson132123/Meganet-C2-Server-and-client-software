# Meganet C2

A simple Command & Control (C2) framework with a reverse shell client, built in Python. I developed this to get a better understanding of malware, explore how remote access software is created, improve my coding knowledge and challenge myself.

> **Educational use only. Run in an isolated lab environment. Never deploy against systems you do not own. Never use with bad intent.**

---

## What It Is

This project consists of two components:

- **`server.py`** — The C2 server (operator console). Listens for incoming connections, manages multiple sessions, and lets the operator interact with connected clients.
- **`reverse_shell.py`** — The client connects back to the server, executes commands, and returns output.

---

## Features

- Remote code execution — execute commands from the c2 on the client
- Multi-client support — handles multiple simultaneous connections with threading
- Live path prompt — the server displays the client's current working directory
- OS detection — automatically handles encoding differences between Windows (`cp850`) and Linux (`utf-8`)
- Separate stdout/stderr — error output is displayed distinctly from normal output
- Session management — `list`, `use`, `exit`, `kill`

---

## Architecture

```
[Client machine]                    [Attacker machine]
reverse_shell.py  ---TCP--->  server.py (meganet)
```

On startup the client sends its hostname and OS to the server. The server registers the client as a session and the operator can interact with it using the menu.

---

## Protocol

All data is sent using a **length-prefix protocol** built with Python's `struct` module:

```
[ 4 bytes: message length (big-endian uint32) ][ N bytes: message data ]
```

This ensures the receiver knows exactly how many bytes to read, preventing partial reads and buffer issues — a common problem with raw TCP streams.

Special control messages are sent as plain strings:
- `__exit__` — suspend session, return to menu (client stays connected)
- `__kill__` — terminate the client process and remove the session

---

## Usage

**Start the server first:**
```bash
python server.py
```

**Then start the client** (on the same machine or another machine in the lab):
```bash
python reverse_shell.py
```

**Server commands:**

| Command | Description |
|---------|-------------|
| `list` | Show all active sessions (ID, IP, hostname, OS) |
| `use <id>` | Open a shell session with a client |
| `help` | Show available commands |
| `clear` | Clear the screen |
| `exit` | Exit the server |

**Session commands (inside a session):**

| Command | Description |
|---------|-------------|
| `exit` | Return to the main menu (session stays alive) |
| `kill` | Terminate the client and remove the session |
| Any shell command | Executed on the client machine |

---

## Example

```
[*] New client connected: 192.168.1.105

mn > list

ID   IP               HOSTNAME        OS

0    192.168.1.105    DESKTOP-AB123   Windows

mn > use 0

C:\Users\albin\Desktop> whoami
desktop-ab123\albin

C:\Users\albin\Desktop> exit

mn >
```

---

## Concepts Learned

**Reverse shell vs bind shell**
A bind shell listens on the target and waits for the attacker to connect. A reverse shell connects outbound from the target to the attacker. Reverse shells are far more common in practice because outbound TCP is almost never blocked by firewalls.

**Length-prefix framing**
TCP is a stream protocol — it has no built-in concept of message boundaries. Sending `recv(1024)` does not guarantee you get exactly one command. By prepending a 4-byte length header to every message, both sides always know how many bytes belong to each message.

**`struct.pack("!I", n)`**
Packs an integer as a 4-byte big-endian unsigned int. The `!` means network byte order (big-endian), which is the standard for binary protocols sent over a network.

**Threading for concurrent sessions**
The server runs a background listener thread (`daemon=True`) that accepts new connections without blocking the operator's input loop. Each connected client is stored in a list and accessed by index.

**Cross-platform encoding**
Windows cmd uses the `cp850` codepage for output, while Linux uses `utf-8`. Without detecting the OS and decoding accordingly, output with special characters would be garbled or crash the server.

**Subprocess and shell execution**
The client uses `subprocess.run(cmd, shell=True, capture_output=True)` to execute commands. `capture_output=True` captures both stdout and stderr separately, which are then sent back to the server independently.

---

## What I Would Improve

- Error handling for invalid `use` input (e.g. `use abc`, `use 99`)
- Reconnect logic in the client — automatically retry if the connection drops
- Timestamp on sessions in the `list` view
- File transfer (`upload`/`download` commands)
- Encrypted communication (e.g. wrapping the socket with TLS)
