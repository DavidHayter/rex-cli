"""Generate & explain cron expressions."""

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()
app = typer.Typer(no_args_is_help=True)

FIELD_NAMES = ["Minute", "Hour", "Day (Month)", "Month", "Day (Week)"]
FIELD_RANGES = ["0-59", "0-23", "1-31", "1-12", "0-7 (0,7=Sun)"]

PRESETS = {
    "every-minute": ("* * * * *", "Every minute"),
    "every-5min": ("*/5 * * * *", "Every 5 minutes"),
    "every-15min": ("*/15 * * * *", "Every 15 minutes"),
    "every-30min": ("*/30 * * * *", "Every 30 minutes"),
    "hourly": ("0 * * * *", "Every hour at minute 0"),
    "every-2h": ("0 */2 * * *", "Every 2 hours"),
    "every-6h": ("0 */6 * * *", "Every 6 hours"),
    "daily": ("0 0 * * *", "Every day at midnight"),
    "daily-9am": ("0 9 * * *", "Every day at 9:00 AM"),
    "daily-6pm": ("0 18 * * *", "Every day at 6:00 PM"),
    "weekly": ("0 0 * * 0", "Every Sunday at midnight"),
    "weekdays": ("0 9 * * 1-5", "Weekdays at 9:00 AM"),
    "weekends": ("0 10 * * 6,0", "Weekends at 10:00 AM"),
    "monthly": ("0 0 1 * *", "First day of month at midnight"),
    "quarterly": ("0 0 1 1,4,7,10 *", "First day of each quarter"),
    "yearly": ("0 0 1 1 *", "January 1st at midnight"),
    "reboot": ("@reboot", "On system reboot"),
    "midnight": ("0 0 * * *", "At midnight daily"),
    "business-hours": ("*/15 9-17 * * 1-5", "Every 15min during business hours"),
    "backup-nightly": ("0 2 * * *", "Daily at 2:00 AM (backup window)"),
    "cleanup-weekly": ("0 3 * * 0", "Sunday at 3:00 AM (cleanup window)"),
    "health-check": ("*/5 * * * *", "Every 5 minutes (health check)"),
    "log-rotation": ("0 0 * * *", "Daily at midnight (log rotation)"),
    "cert-renewal": ("0 0 1,15 * *", "1st and 15th of month (cert check)"),
}


@app.command("explain")
def explain(
    expression: str = typer.Argument(..., help="Cron expression to explain (quote it)"),
):
    """Explain a cron expression in human-readable format."""
    if expression.startswith("@"):
        special = {
            "@reboot": "Run once at system startup",
            "@yearly": "Run once a year (0 0 1 1 *)",
            "@annually": "Run once a year (0 0 1 1 *)",
            "@monthly": "Run once a month (0 0 1 * *)",
            "@weekly": "Run once a week (0 0 * * 0)",
            "@daily": "Run once a day (0 0 * * *)",
            "@midnight": "Run once a day (0 0 * * *)",
            "@hourly": "Run once an hour (0 * * * *)",
        }
        desc = special.get(expression, "Unknown special expression")
        console.print(Panel(f"[bold]{expression}[/bold]\n\n{desc}", title="⏰ Cron Expression", border_style="green", box=box.ROUNDED))
        return

    parts = expression.split()
    if len(parts) != 5:
        console.print(f"[red]✗ Invalid cron expression. Expected 5 fields, got {len(parts)}.[/red]")
        raise typer.Exit(1)

    table = Table(title=f"⏰ Cron: {expression}", box=box.ROUNDED, border_style="green")
    table.add_column("Field", style="bold cyan")
    table.add_column("Value", style="white")
    table.add_column("Range", style="dim")
    table.add_column("Meaning", style="green")

    for field_name, field_range, value in zip(FIELD_NAMES, FIELD_RANGES, parts):
        meaning = _explain_field(value, field_name)
        table.add_row(field_name, value, field_range, meaning)

    console.print(table)

    # Human readable summary
    summary = _build_summary(parts)
    console.print(f"\n[bold green]📖 Summary:[/bold green] {summary}")


def _explain_field(value: str, field_name: str) -> str:
    """Explain a single cron field."""
    if value == "*":
        return f"Every {field_name.lower()}"
    elif value.startswith("*/"):
        return f"Every {value[2:]} {field_name.lower()}(s)"
    elif "," in value:
        return f"At {field_name.lower()} {value}"
    elif "-" in value:
        parts = value.split("-")
        return f"From {parts[0]} to {parts[1]}"
    else:
        return f"At {field_name.lower()} {value}"


def _build_summary(parts: list) -> str:
    """Build a human-readable summary."""
    minute, hour, dom, month, dow = parts
    pieces = []

    if minute == "*" and hour == "*":
        pieces.append("Every minute")
    elif minute.startswith("*/"):
        pieces.append(f"Every {minute[2:]} minutes")
    elif hour == "*":
        pieces.append(f"At minute {minute} of every hour")
    elif minute == "0":
        pieces.append(f"At {hour}:00")
    else:
        pieces.append(f"At {hour}:{minute.zfill(2)}")

    if dom != "*":
        pieces.append(f"on day {dom} of the month")
    if month != "*":
        pieces.append(f"in month(s) {month}")
    if dow != "*":
        day_map = {"0": "Sunday", "1": "Monday", "2": "Tuesday", "3": "Wednesday",
                   "4": "Thursday", "5": "Friday", "6": "Saturday", "7": "Sunday"}
        if "-" in dow:
            start, end = dow.split("-")
            pieces.append(f"on {day_map.get(start, start)} through {day_map.get(end, end)}")
        elif "," in dow:
            days = [day_map.get(d, d) for d in dow.split(",")]
            pieces.append(f"on {', '.join(days)}")
        else:
            pieces.append(f"on {day_map.get(dow, dow)}")

    return " ".join(pieces)


@app.command("presets")
def presets():
    """Show common cron expression presets."""
    table = Table(title="⏰ Cron Presets", box=box.ROUNDED, border_style="green")
    table.add_column("Name", style="bold cyan", min_width=18)
    table.add_column("Expression", style="white", min_width=22)
    table.add_column("Description", style="dim")

    for name, (expr, desc) in PRESETS.items():
        table.add_row(name, expr, desc)

    console.print(table)
    console.print("\n[dim]Use: [bold]rex cron generate <preset-name>[/bold] to copy a preset.[/dim]")


@app.command("generate")
def generate(
    preset: Optional[str] = typer.Argument(None, help="Preset name (run 'rex cron presets' to see all)"),
    minute: Optional[str] = typer.Option(None, "--minute", "-m"),
    hour: Optional[str] = typer.Option(None, "--hour", "-H"),
    day: Optional[str] = typer.Option(None, "--day", "-d"),
    month: Optional[str] = typer.Option(None, "--month", "-M"),
    weekday: Optional[str] = typer.Option(None, "--weekday", "-w"),
):
    """Generate a cron expression from preset or custom fields."""
    if preset:
        if preset in PRESETS:
            expr, desc = PRESETS[preset]
            console.print(Panel(
                f"[bold white]{expr}[/bold white]\n\n[dim]{desc}[/dim]",
                title=f"⏰ Preset: {preset}",
                border_style="green",
                box=box.ROUNDED,
            ))
        else:
            console.print(f"[red]✗ Unknown preset: {preset}. Run 'rex cron presets' for available presets.[/red]")
            raise typer.Exit(1)
    else:
        m = minute or "*"
        h = hour or "*"
        d = day or "*"
        mo = month or "*"
        wd = weekday or "*"
        expr = f"{m} {h} {d} {mo} {wd}"
        console.print(Panel(
            f"[bold white]{expr}[/bold white]",
            title="⏰ Generated Cron Expression",
            border_style="green",
            box=box.ROUNDED,
        ))
