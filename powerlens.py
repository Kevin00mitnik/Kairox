import os
import sys
import asyncio

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.rule import Rule

from utils.checker import check_tools
from utils.runner import CommandError
from utils.validation import normalize_domain
from core.engine import run_engine

console = Console()

TOOL_NAME = "Power Lens"
AUTHOR = "Mohammed Arif Pallath (whitefox.infosec)"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    console.print(Panel.fit(
        f"[bold #00d4ff]{TOOL_NAME}[/bold #00d4ff]\n"
        f"[white]Author: {AUTHOR}[/white]",
        border_style="#00d4ff"
    ))

def disclaimer():
    console.print(Panel.fit(
        "[bold red]LEGAL DISCLAIMER[/bold red]\n\n"
        "Use only for authorized security testing.\n"
        "Unauthorized use is illegal.",
        border_style="red"
    ))

def confirm():
    while True:
        c = Prompt.ask("[yellow]Proceed? (yes/no)[/yellow]").lower()
        if c in ["yes", "y"]:
            return
        elif c in ["no", "n"]:
            sys.exit()
        else:
            console.print("[red]Invalid input[/red]")

def get_target():
    while True:
        target = Prompt.ask("[cyan]Enter target domain[/cyan]")
        try:
            return normalize_domain(target)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")

def show(data, live, ports, urls, tls, errors):
    console.print(Rule("[bold cyan]Results[/bold cyan]"))

    def render(title, items, color):
        table = Table(title=title, style=color)
        table.add_column("Value")
        for i in items[:20]:
            table.add_row(str(i))
        console.print(table)

    render("High Value", data["high"], "red")
    render("Medium Value", data["medium"], "yellow")
    render("Live Hosts", [f"{l['url']} [{l['status']}]" for l in live], "cyan")
    render("Open Ports", ports, "green")
    render("Sensitive URLs", urls, "magenta")
    render("TLS / SSL Results", tls, "blue")
    render("Checks with errors", errors, "red")

    console.print(Rule("[green]Completed[/green]"))

def main():
    clear()
    banner()
    disclaimer()
    confirm()

    check_tools()

    target = get_target()
    console.print(f"[green]Target: {target}[/green]\n")
    console.print(
        "[cyan]Running live-host, port, archived-URL, and TLS checks. "
        "This can take a few minutes...[/cyan]"
    )

    try:
        data, live, ports, urls, tls, errors = asyncio.run(run_engine(target))
    except (CommandError, RuntimeError, OSError) as exc:
        console.print(f"\n[red]{TOOL_NAME} could not complete the scan:[/red] {exc}")
        raise SystemExit(1) from exc
    except KeyboardInterrupt:
        console.print("\n[yellow]Scan cancelled.[/yellow]")
        raise SystemExit(130) from None

    show(data, live, ports, urls, tls, errors)

if __name__ == "__main__":
    main()