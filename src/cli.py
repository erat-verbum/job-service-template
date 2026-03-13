import asyncio
import signal
import sys
from typing import Any, Callable, Optional

import typer
from rich.console import Console

from .job_runner import JobRunner
from .models import JobStatus

app = typer.Typer(
    name="job-service",
    help="CLI for running jobs without Docker",
)
console = Console()


class CliJobRunner(JobRunner):
    """Job runner with CLI progress output."""

    def __init__(
        self,
        job_ref: Optional[dict[str, Any]],
        get_status: Callable[[], str],
    ):
        super().__init__(job_ref, get_status)
        self._last_progress = -1

    async def run(self) -> dict[str, Any]:
        """Run the placeholder job with progress output."""
        for i in range(1, 11):
            if self._get_status() == "cancelled":
                console.print("[yellow]Job cancelled[/yellow]")
                return {"cancelled": True}

            await asyncio.sleep(0.1)
            if self._job_ref:
                self._job_ref["progress"] = i * 10
                self._job_ref["result"] = {"step": i, "message": f"Processing step {i}"}

                if i != self._last_progress:
                    console.print(f"[cyan]Progress:[/cyan] {i * 10}% - Step {i}")
                    self._last_progress = i

        return {"completed": True, "total_steps": 10}


def run_cli_job(
    job_id: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Run a job synchronously for the CLI."""
    job_ref: dict[str, Any] = {
        "id": job_id,
        "status": JobStatus.RUNNING,
        "progress": 0,
        "input_params": params,
    }

    cancelled = False

    def get_status() -> str:
        return job_ref["status"]

    async def run_with_progress():
        nonlocal cancelled
        runner = CliJobRunner(job_ref, get_status)
        try:
            result = await runner.run()
            if job_ref["status"] == JobStatus.RUNNING:
                job_ref["status"] = JobStatus.COMPLETED
                job_ref["result"] = result
        except Exception as e:
            job_ref["status"] = JobStatus.FAILED
            job_ref["error"] = str(e)

    def signal_handler(sig, frame):
        nonlocal cancelled
        cancelled = True
        job_ref["status"] = JobStatus.CANCELLED
        console.print("\n[yellow]Received interrupt, cancelling job...[/yellow]")
        sys.exit(130)

    original_handler = signal.signal(signal.SIGINT, signal_handler)

    try:
        asyncio.run(run_with_progress())
    finally:
        signal.signal(signal.SIGINT, original_handler)

    return job_ref


@app.command()
def run(
    job_id: Optional[str] = typer.Option(
        None,
        "--job-id",
        "-j",
        help="Job identifier (auto-generated if not provided)",
    ),
    params: list[str] = typer.Option(
        [],
        "--param",
        "-p",
        help="Job parameters as key=value pairs",
    ),
) -> None:
    """
    Run a job from the command line.

    Example:

        job-service run -p key1=value1 -p key2=value2
    """
    import uuid

    from .models import JobStatus

    if job_id is None:
        job_id = str(uuid.uuid4())

    param_dict: dict[str, Any] = {}
    for param in params:
        if "=" not in param:
            console.print(
                f"[red]Error:[/red] Invalid parameter '{param}'. Use key=value format."
            )
            raise typer.Exit(code=1)
        key, value = param.split("=", 1)
        param_dict[key] = value

    console.print(f"[bold]Starting job:[/bold] {job_id}")

    job_result = run_cli_job(job_id, param_dict)

    if job_result["status"] == JobStatus.COMPLETED:
        console.print("[green]Job completed successfully![/green]")
        console.print(f"Result: {job_result.get('result')}")
    elif job_result["status"] == JobStatus.CANCELLED:
        console.print("[yellow]Job was cancelled[/yellow]")
        raise typer.Exit(code=130)
    else:
        console.print(f"[red]Job failed:[/red] {job_result.get('error')}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
