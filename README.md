# WHITEFOX

WHITEFOX is a command-line reconnaissance tool for domains you own or are explicitly authorized to assess. The GitHub repository remains named `Kairox`.

## Install on Kali Linux

Run these commands as your normal Kali user, not from a root shell:

```bash
git clone https://github.com/Kevin00mitnik/Kairox.git
cd Kairox
chmod +x install.sh
./install.sh
```

The installer uses `sudo` only for system packages. It creates the Python virtual environment, installs the Go-based tools into your user's `~/go/bin`, installs `testssl.sh` from Kali's package repository, and verifies the required commands. If Go reports damaged cached downloads, the installer retries that tool with a fresh temporary module cache and prints an error if the retry fails. You can safely rerun the installer after fixing a reported network or package-manager problem.

Start WHITEFOX with:

```bash
source venv/bin/activate
python kairox.py
```

If the Go commands are not found in the current terminal after setup, open a new terminal or run:

```bash
export PATH="$HOME/go/bin:$PATH"
```

WHITEFOX discovers subdomains with Subfinder, probes live hosts with httpx, checks ports with nmap, finds archived URLs with gau, and checks TLS protocols and common vulnerabilities with testssl.sh. The TLS check targets HTTPS on port 443.

Do not run the application or installer as root. It installs command-line tools for the current user, and the default scans do not need root privileges.

## Troubleshooting

- **Installer says it was run as root:** type `exit` until `whoami` prints `kali`, return to the cloned project directory, and run `./install.sh` again.
- **A tool is missing:** run `./install.sh` as your normal user and check the first error printed by the installer. Ensure your Kali package mirror and internet connection are working.
- **A Go build reports truncated files or `expected 'package', found 'EOF'`:** the installer automatically retries that tool with a fresh temporary module cache. If it still fails, check the displayed Go error and rerun after fixing the underlying network or Go issue.
- **The scan reports a command, timeout, or process error:** WHITEFOX prints the failing command and actionable next steps; confirm dependencies and connectivity, then retry.

Not every failure can be repaired automatically: unavailable mirrors, blocked networks, API rate limits, and upstream tool changes require resolving the underlying issue.
