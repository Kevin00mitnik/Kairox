import os
import shutil
from pathlib import Path

from rich.console import Console

console = Console()


def check_tools():
    go_bin = Path.home() / "go" / "bin"
    os.environ["PATH"] = os.pathsep.join(
        [str(go_bin), os.environ.get("PATH", "")]
    )

    tools = ["subfinder", "httpx", "gau", "nmap", "testssl"]
    console.print("\n[cyan]Checking dependencies...[/cyan]\n")

    missing = []
    for tool in tools:
        location = shutil.which(tool)
        if location:
            console.print(f"[green]{tool} found[/green]")
        else:
            console.print(f"[red]{tool} missing[/red]")
            missing.append(tool)

    if missing:
        console.print(
            "\n[red]Missing tools: "
            + ", ".join(missing)
            + "[/red]"
        )
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            console.print(
                "[yellow]You are running as root. Exit the root shell and run "
                "./install.sh as your normal Kali user.[/yellow]"
            )
        else:
            console.print(
                "[yellow]From the Kairox project directory, run "
                "./install.sh as your normal user, then reopen your terminal.[/yellow]"
            )
        raise SystemExit(1)
