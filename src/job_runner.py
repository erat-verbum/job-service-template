import asyncio
from typing import Any, Callable, Optional


class JobRunner:
    """Manages job execution with progress updates and cancellation support."""

    def __init__(
        self, job_ref: Optional[dict[str, Any]], get_status: Callable[[], str]
    ):
        self._job_ref = job_ref
        self._get_status = get_status

    async def run(self) -> dict[str, Any]:
        """Run the placeholder job. Override this for custom jobs."""
        for i in range(1, 11):
            if self._get_status() == "cancelled":
                return {"cancelled": True}

            await asyncio.sleep(0.1)
            if self._job_ref:
                self._job_ref["progress"] = i * 10
                self._job_ref["result"] = {"step": i, "message": f"Processing step {i}"}

        return {"completed": True, "total_steps": 10}


async def run_job(
    job_ref: Optional[dict[str, Any]],
    get_status: Callable[[], str],
) -> dict[str, Any]:
    """Entry point for running a job."""
    runner = JobRunner(job_ref, get_status)
    return await runner.run()
