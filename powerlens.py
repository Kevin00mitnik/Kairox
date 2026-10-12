import os
import sys
import asyncio
from collections.abc import Sequence

from rich import box
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.rule import Rule
from rich.text import Text

from utils.checker import check_tools
from utils.runner import CommandError
from utils.validation import normalize_domain
from core.engine import run_engine

console = Console()

TOOL_NAME = "Power Lens"
AUTHOR = "Mohammed Arif Pallath (whitefox.infosec)"
ACCENT = "#35D0BA"
MAX_DISPLAY_ROWS = 20

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    brand = Table.grid(padding=(0, 2))
    brand.add_column()
    brand.add_row(Text("POWER LENS", style=f"bold {ACCENT}"))
    brand.add_row(Text("DOMAIN INTELLIGENCE  /  AUTHORIZED SECURITY TESTING", style="dim"))
    brand.add_row(Text(f"Created by {AUTHOR}", style="white"))
    console.print(
        Panel(
            brand,
            border_style=ACCENT,
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )

def disclaimer():
    console.print(
        Panel(
            Text(
                "Use only on systems you own or are explicitly authorized to assess. "
                "Unauthorized testing may be illegal.",
                style="white",
            ),
            title="[bold yellow]AUTHORIZED USE ONLY[/bold yellow]",
            title_align="left",
            border_style="yellow",
            box=box.ROUNDED,
            padding=(0, 1),
        )
    )

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

def _metric(label, value, color):
    return Panel(
        Align.center(Text(str(value), style=f"bold {color}")),
        title=Text(label, style="dim"),
        title_align="left",
        border_style=color,
        box=box.ROUNDED,
        padding=(0, 1),
        expand=True,
    )


def _section(title, items, color, columns=("Value",)):
    table = Table(
        box=box.SIMPLE_HEAD,
        expand=True,
        show_header=bool(items),
        header_style="bold dim",
        padding=(0, 1),
    )
    for column in columns:
        table.add_column(column, overflow="fold")

    visible = items[:MAX_DISPLAY_ROWS]
    if visible:
        for item in visible:
            values = item if isinstance(item, Sequence) and not isinstance(item, str) else (item,)
            table.add_row(*(Text(str(value), overflow="fold") for value in values))
    else:
        table.add_row(
            Text("No findings identified.", style="dim italic"),
            *(Text("") for _ in columns[1:]),
        )

    content = Table.grid(expand=True)
    content.add_column()
    content.add_row(table)
    if len(items) > MAX_DISPLAY_ROWS:
        content.add_row(
            Text(
                f"Showing {MAX_DISPLAY_ROWS} of {len(items)} entries",
                style="dim",
            )
        )

    return Panel(
        content,
        title=f"[bold]{title}[/bold]  [dim]{len(items)}[/dim]",
        title_align="left",
        border_style=color,
        box=box.ROUNDED,
        padding=(0, 1),
    )


def show(target, data, live, ports, urls, tls, errors):
    console.print(Rule(f"[bold {ACCENT}]SCAN OVERVIEW[/bold {ACCENT}]"))
    console.print(
        Panel(
            Text(target, style=f"bold {ACCENT}"),
            title="[dim]AUTHORIZED TARGET[/dim]",
            title_align="left",
            border_style="dim",
            box=box.ROUNDED,
            padding=(0, 1),
        )
    )

    high = data.get("high", [])
    medium = data.get("medium", [])
    low = data.get("low", [])
    metrics = (
        ("Subdomains", len(high) + len(medium) + len(low), ACCENT),
        ("High value", len(high), "red"),
        ("Medium value", len(medium), "yellow"),
        ("Live hosts", len(live), "cyan"),
        ("Open ports", len(ports), "green"),
        ("Archived URLs", len(urls), "magenta"),
    )
    summary = Table.grid(expand=True, padding=(0, 1))
    summary.add_column(ratio=1)
    summary.add_column(ratio=1)
    summary.add_column(ratio=1)
    for index in range(0, len(metrics), 3):
        summary.add_row(*(_metric(*metric) for metric in metrics[index:index + 3]))
    console.print(summary)

    console.print(Rule("[bold]FINDINGS[/bold]", style="dim"))
    console.print(
        Columns(
            [
                _section("High-value subdomains", high, "red"),
                _section("Medium-value subdomains", medium, "yellow"),
            ],
            equal=True,
            expand=True,
            padding=(0, 1),
        )
    )
    console.print(
        Columns(
            [
                _section(
                    "Live hosts",
                    [(host["url"], host["status"]) for host in live],
                    "cyan",
                    columns=("URL", "Status"),
                ),
                _section("Open ports", ports, "green"),
            ],
            equal=True,
            expand=True,
            padding=(0, 1),
        )
    )
    console.print(_section("Sensitive archived URLs", urls, "magenta"))
    console.print(_section("TLS / SSL assessment", tls, "blue"))
    if errors:
        console.print(_section("Checks requiring attention", errors, "yellow"))
        console.print(
            Panel(
                Text("Scan completed with checks requiring attention.", style="bold yellow"),
                border_style="yellow",
                box=box.ROUNDED,
                padding=(0, 1),
            )
        )
    else:
        console.print(
            Panel(
                Text("All checks completed without reported errors.", style="bold green"),
                border_style="green",
                box=box.ROUNDED,
                padding=(0, 1),
            )
        )

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

    show(target, data, live, ports, urls, tls, errors)

if __name__ == "__main__":
    main()