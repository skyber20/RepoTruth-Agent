from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from repotruth import __version__
from repotruth.workflow import run_audit


app = typer.Typer(help="RepoTruth Agent: проверка claims по evidence в GitHub-репозитории.")
console = Console()


@app.callback()
def callback(
    version: bool = typer.Option(False, "--version", help="Показать версию."),
):
    """Общие настройки CLI."""

    if version:
        console.print(f"RepoTruth Agent {__version__}")
        raise typer.Exit()


@app.command()
def audit(
    repo: str = typer.Option(..., "--repo", help="GitHub URL репозитория."),
    claims: Path = typer.Option(..., "--claims", exists=True, readable=True, help="Markdown-файл с claims."),
    out: Path = typer.Option(Path("reports/demo"), "--out", help="Папка для report.md и report.json."),
    no_llm: bool = typer.Option(False, "--no-llm", "--offline", help="Отладка без LLM. Для сдачи не использовать."),
):
    """Запускает аудит репозитория."""

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold]{task.description}[/bold]"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Старт аудита...", total=None)

            def show_step(message):
                progress.update(task, description=message)

            report, markdown_path, json_path = run_audit(repo, claims, out, no_llm=no_llm, event=show_step)
    except Exception as error:
        console.print(f"[red]Ошибка:[/red] {error}")
        raise typer.Exit(1) from error

    show_summary(report)
    console.print()
    console.print(f"[green]Markdown:[/green] {markdown_path}")
    console.print(f"[green]JSON:[/green] {json_path}")
    console.print(f"[green]Log:[/green] {Path(out) / 'run.log'}")


def show_summary(report):
    """Печатает короткую таблицу."""

    table = Table(title="RepoTruth Summary")
    table.add_column("Claim", style="bold")
    table.add_column("Verdict")
    table.add_column("Verdict confidence")
    table.add_column("Top evidence")

    for audit in report.audits:
        table.add_row(
            audit.claim.text,
            color_verdict(audit.verdict.verdict),
            f"{audit.verdict.confidence:.2f}",
            ", ".join(audit.verdict.evidence_used[:3]) or "-",
        )

    console.print(table)
    console.print(
        f"Score: [bold]{report.confirmed_count}/{report.total_count}[/bold] confirmed, "
        f"[bold]{report.supported_count}/{report.total_count}[/bold] supported"
    )


def color_verdict(verdict):
    """Красит verdict."""

    if verdict == "confirmed":
        return "[green]confirmed[/green]"
    if verdict == "partial":
        return "[yellow]partial[/yellow]"
    return "[red]missing[/red]"


def main():
    """Точка входа."""

    app()
