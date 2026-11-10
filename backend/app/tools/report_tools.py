"""Report tools — AI-callable analytics and reporting."""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.execution_log import ExecutionLog
from app.models.project import Project
from app.models.task import Task
from app.tools.registry import register_tool


@register_tool("generate_report")
async def generate_report(
    db: AsyncSession,
    user_id: int,
    report_type: str = "weekly",
    include_tasks: bool = True,
    include_projects: bool = True,
    include_time_analysis: bool = True,
) -> Dict[str, Any]:
    """
    Generate a productivity report with real stats from the database.
    Creates an ExecutionLog entry for audit purposes.
    """
    now = datetime.now(timezone.utc)
    if report_type == "daily":
        since = now - timedelta(days=1)
    elif report_type == "weekly":
        since = now - timedelta(days=7)
    elif report_type == "monthly":
        since = now - timedelta(days=30)
    else:
        since = now - timedelta(days=7)

    report: Dict[str, Any] = {
        "report_type": report_type,
        "generated_at": now.isoformat(),
        "period_start": since.isoformat(),
        "period_end": now.isoformat(),
    }

    if include_tasks:
        # Tasks completed in period
        completed = await db.execute(
            select(func.count()).select_from(Task).where(
                Task.user_id == user_id,
                Task.status == "completed",
                Task.updated_at >= since,
            )
        )
        # Total tasks
        total = await db.execute(
            select(func.count()).select_from(Task).where(Task.user_id == user_id)
        )
        # By priority
        for priority in ["low", "medium", "high", "critical"]:
            cnt = await db.execute(
                select(func.count()).select_from(Task).where(
                    Task.user_id == user_id, Task.priority == priority
                )
            )
            report.setdefault("tasks_by_priority", {})[priority] = cnt.scalar() or 0

        overdue = await db.execute(
            select(func.count()).select_from(Task).where(
                Task.user_id == user_id, Task.status == "overdue"
            )
        )
        total_count = total.scalar() or 0
        completed_count = completed.scalar() or 0
        report["tasks"] = {
            "completed_in_period": completed_count,
            "total": total_count,
            "overdue": overdue.scalar() or 0,
            "completion_rate": round(completed_count / total_count * 100, 1) if total_count else 0.0,
        }

    if include_projects:
        projects = await db.execute(
            select(Project).where(Project.user_id == user_id).limit(50)
        )
        all_projects = projects.scalars().all()
        report["projects"] = {
            "total": len(all_projects),
            "active": sum(1 for p in all_projects if p.status == "active"),
            "completed": sum(1 for p in all_projects if p.status == "completed"),
            "archived": sum(1 for p in all_projects if p.status == "archived"),
        }

    if include_time_analysis:
        # Recent execution logs as proxy for activity
        logs = await db.execute(
            select(ExecutionLog).where(
                ExecutionLog.user_id == user_id,
                ExecutionLog.created_at >= since,
            ).limit(100)
        )
        all_logs = logs.scalars().all()
        report["activity"] = {
            "total_actions": len(all_logs),
            "successful": sum(1 for l in all_logs if l.status == "success"),
            "failed": sum(1 for l in all_logs if l.status == "failed"),
        }

    # Create execution log entry
    log = ExecutionLog(
        user_id=user_id,
        action_type="generate_report",
        status="success",
        input_data={"report_type": report_type},
        output_data=report,
    )
    db.add(log)
    await db.flush()

    return report
