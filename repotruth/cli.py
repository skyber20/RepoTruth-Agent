from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from repotruth.workflow import run_audit


app = typer.Typer(help="RepoTruth Agent", add_completion=False)
console = Console()


@app.command()
def audit(
    repo: str = typer.Option(..., "--repo", help="GitHub URL или локальная папка."),
    claims: Path = typer.Option(..., "--claims", exists=True, readable=True, help="Файл с ТЗ/claims."),
    out: Path = typer.Option(Path("reports/demo"), "--out", help="Папка для отчета."),
):
    """Сверяет claims с кодом репозитория."""

    try:
        with Progress(SpinnerColumn(), TextColumn("[bold]{task.description}[/bold]"), console=console, transient=True) as progress:
            task = progress.add_task("Стартую аудит...", total=None)

            def show_step(message):
                progress.update(task, description=message)
                progress.console.print(f"[dim]• {message}[/dim]")

            report, markdown_path, json_path = run_audit(repo, claims, out, event=show_step)
    except Exception as error:
        console.print(f"[red]Ошибка:[/red] {error}")
        raise typer.Exit(1) from error

    show_summary(report)
    console.print(f"[green]Markdown:[/green] {markdown_path}")
    console.print(f"[green]JSON:[/green] {json_path}")
    console.print(f"[green]Log:[/green] {Path(out) / 'run.log'}")


def show_summary(report):
    table = Table(title="RepoTruth Summary")
    table.add_column("Claim", style="bold")
    table.add_column("Verdict")
    table.add_column("Confidence")
    table.add_column("Tools")
    table.add_column("Почему")
    table.add_column("Evidence")

    for audit in report.audits:
        table.add_row(
            audit.claim.text,
            color(audit.verdict.verdict),
            f"{audit.verdict.confidence:.2f}",
            ", ".join(audit.tools_used) or "-",
            audit.verdict.reason,
            ", ".join(audit.verdict.evidence_used[:3]) or "-",
        )

    console.print(table)
    console.print(f"Score: [bold]{report.confirmed_count}/{report.total_count}[/bold] confirmed")


def color(verdict):
    if verdict == "confirmed":
        return "[green]confirmed[/green]"
    if verdict == "partial":
        return "[yellow]partial[/yellow]"
    return "[red]missing[/red]"


def main():
    app()
