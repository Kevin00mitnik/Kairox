#!/usr/bin/env bash

set -Eeuo pipefail

trap 'status=$?; printf "\n[!] Setup failed at line %s (exit %s): %s\n" "$LINENO" "$status" "$BASH_COMMAND" >&2; exit "$status"' ERR

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ $EUID -eq 0 ]]; then
    printf '[!] Do not run this installer as root or with sudo.\n' >&2
    printf '    Run it as your normal Kali user: cd ~/Downloads/Kairox && ./install.sh\n' >&2
    printf '    The installer will request sudo only for system packages.\n' >&2
    exit 1
fi

if ! command -v apt-get >/dev/null 2>&1; then
    printf '[!] This installer currently supports Kali/Debian systems with apt-get.\n' >&2
    exit 1
fi

if ! command -v sudo >/dev/null 2>&1; then
    printf '[!] sudo is required to install system packages. Install sudo or ask your administrator.\n' >&2
    exit 1
fi

printf '[+] Installing system dependencies...\n'
sudo apt-get update
sudo apt-get install -y git curl wget python3 python3-pip python3-venv nmap golang-go testssl.sh

if ! command -v python3 >/dev/null 2>&1 || ! command -v go >/dev/null 2>&1; then
    printf '[!] Python 3 and Go must be available after installing system dependencies.\n' >&2
    exit 1
fi

VENV_DIR="$SCRIPT_DIR/venv"
if [[ -d "$VENV_DIR" && ! -w "$VENV_DIR" ]]; then
    printf "[+] Repairing ownership of this project's existing virtual environment...\n"
    sudo chown -R "$(id -u):$(id -g)" "$VENV_DIR"
fi

printf '[+] Setting up the Python virtual environment...\n'
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install -r "$SCRIPT_DIR/requirements.txt"

GOBIN="$HOME/go/bin"
mkdir -p "$GOBIN"
export GOBIN
export PATH="$GOBIN:$(go env GOROOT)/bin:$PATH"

add_go_path_to_profile() {
    local profile="$1"
    local path_line='export PATH="$HOME/go/bin:$PATH"'

    if [[ -f "$profile" ]] && grep -Fqx "$path_line" "$profile"; then
        return
    fi

    printf '\n# Kairox Go tools\n%s\n' "$path_line" >> "$profile"
}

add_go_path_to_profile "$HOME/.profile"
[[ ! -f "$HOME/.bashrc" ]] || add_go_path_to_profile "$HOME/.bashrc"
[[ ! -f "$HOME/.zshrc" ]] || add_go_path_to_profile "$HOME/.zshrc"

install_go_tool() {
    local name="$1"
    local package="$2"
    local first_log
    local retry_log
    local retry_cache
    local status

    if command -v "$name" >/dev/null 2>&1 && [[ "$(command -v "$name")" == "$GOBIN/"* ]]; then
        printf '[+] %s is already installed.\n' "$name"
        return
    fi

    printf '[+] Installing %s with Go (this can take several minutes)...\n' "$name"
    first_log="$(mktemp "${TMPDIR:-/tmp}/kairox-go-install.XXXXXX")"
    if go install -v "$package" 2>&1 | tee "$first_log"; then
        rm -f -- "$first_log"
        return
    else
        status=$?
    fi

    if ! grep -Eq "expected 'package', found 'EOF'|checksum mismatch|zip: not a valid zip file" "$first_log"; then
        rm -f -- "$first_log"
        printf '[!] Could not install %s. Check your internet connection and Go output above, then rerun ./install.sh.\n' "$name" >&2
        return "$status"
    fi

    printf '[!] Go reported a damaged module download. Retrying %s with a fresh temporary module cache...\n' "$name" >&2
    retry_cache="$(mktemp -d "${TMPDIR:-/tmp}/kairox-gomodcache.XXXXXX")"
    retry_log="$(mktemp "${TMPDIR:-/tmp}/kairox-go-retry.XXXXXX")"
    if GOMODCACHE="$retry_cache" go install -v "$package" 2>&1 | tee "$retry_log"; then
        rm -f -- "$first_log" "$retry_log"
        rm -rf -- "$retry_cache"
        printf '[+] %s installed using a fresh Go module cache.\n' "$name"
        return
    else
        status=$?
    fi

    rm -f -- "$first_log" "$retry_log"
    rm -rf -- "$retry_cache"
    printf '[!] Could not install %s. Check your internet connection and Go output above, then rerun ./install.sh.\n' "$name" >&2
    return "$status"
}

printf '[+] Installing command-line tools for your user...\n'
install_go_tool subfinder github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
install_go_tool httpx github.com/projectdiscovery/httpx/cmd/httpx@latest
install_go_tool gau github.com/lc/gau/v2/cmd/gau@latest

printf '\n[+] Verifying required tools...\n'
missing=()
for tool in subfinder httpx gau nmap testssl; do
    if command -v "$tool" >/dev/null 2>&1; then
        printf '[+] %s: %s\n' "$tool" "$(command -v "$tool")"
    else
        printf '[!] %s is still missing.\n' "$tool" >&2
        missing+=("$tool")
    fi
done

if ((${#missing[@]})); then
    printf '\n[!] Setup is incomplete. Missing: %s\n' "${missing[*]}" >&2
    printf '    Review the error above, fix the reported problem, and rerun ./install.sh.\n' >&2
    exit 1
fi

printf '\n[+] Setup completed successfully.\n'
printf '[+] Start KAIROX with: %s\n' "$VENV_DIR/bin/python kairox.py"
printf '[+] Open a new terminal or run: export PATH="$HOME/go/bin:$PATH"\n'
