import logging
import sys
from typing import Any

from framework.runtime.context import JobContext


class ContextLoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that injects JobContext fields into every log record.
    """

    def process(self, msg: str, kwargs: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs


def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure root logging for pipeline jobs.

    This should be called once at the beginning of each job.
    """
    logging.basicConfig(
        level=level,
        format=(
            "%(asctime)s "
            "%(levelname)s "
            "pipeline=%(pipeline_name)s "
            "job=%(job_name)s "
            "business_date=%(business_date)s "
            "run_id=%(run_id)s "
            "env=%(env)s "
            "- %(message)s"
        ),
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )


def get_logger(context: JobContext) -> logging.LoggerAdapter:
    """
    Create a context-aware logger for a pipeline job.
    """
    base_logger = logging.getLogger(f"{context.pipeline_name}.{context.job_name}")

    return ContextLoggerAdapter(
        base_logger,
        {
            "pipeline_name": context.pipeline_name,
            "job_name": context.job_name,
            "business_date": context.business_date,
            "run_id": context.run_id,
            "env": context.env,
        },
    )
