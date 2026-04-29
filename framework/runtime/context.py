# 这个文件是整个 data platform 的“运行上下文（execution context）”

# 它会被所有 pipeline 使用：
# user_events ingestion
# dau
# retention
# orders
# revenue
# orders_conversion

# 这个 Context 要解决 5 件事：
# 1. 当前运行是哪一天的数据（business_date）
# 2. 这次运行的唯一 ID（run_id）
# 3. 是哪个 pipeline / job 在跑
# 4. 当前环境（dev / prod）
# 5. 统一日志和路径使用

from dataclasses import dataclass
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class JobContext:
    """
    JobContext represents the runtime context of a single pipeline job execution.

    It is immutable and shared across the entire job lifecycle.
    """

    # core identifiers
    pipeline_name: str
    job_name: str

    # execution info
    business_date: str  # e.g. "2026-04-22"
    run_id: str  # unique ID for this run

    # environment
    env: str = "dev"

    @staticmethod
    def generate_run_id() -> str:
        """Generate a unique run id."""
        return (
            datetime.now(timezone.utc).strftime("%Y%m%d%H%M%SZ")
            + "_"
            + str(uuid.uuid4())[:8]
        )

    @classmethod
    def create(
        cls,
        pipeline_name: str,
        job_name: str,
        business_date: str,
        env: str = "dev",
    ) -> "JobContext":
        """
        Factory method to create a JobContext.

        This ensures run_id is always generated consistently.
        """
        return cls(
            pipeline_name=pipeline_name,
            job_name=job_name,
            business_date=business_date,
            run_id=cls.generate_run_id(),
            env=env,
        )

    def as_dict(self) -> dict:
        """Convert context to dictionary (useful for logging)."""
        return {
            "pipeline_name": self.pipeline_name,
            "job_name": self.job_name,
            "business_date": self.business_date,
            "run_id": self.run_id,
            "env": self.env,
        }
