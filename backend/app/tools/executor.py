"""Tool executor — iterates ActionPlan tool calls and executes them."""
import logging
import time
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.ai_schemas import ActionPlan, ToolCall
from app.tools.registry import registry

# Import tools to trigger @register_tool decorators
import app.tools.task_tools  # noqa: F401
import app.tools.project_tools  # noqa: F401
import app.tools.calendar_tools  # noqa: F401
import app.tools.report_tools  # noqa: F401
import app.tools.automation_tools  # noqa: F401

logger = logging.getLogger(__name__)


async def execute_plan(
    plan: ActionPlan,
    user_id: int,
    db: AsyncSession,
) -> List[ToolCall]:
    """
    Execute each tool call in the ActionPlan sequentially.
    Updates each ToolCall with its result or error.
    Returns the list of ToolCalls with results filled in.
    """
    executed: List[ToolCall] = []

    for tool_call in plan.tool_calls:
        func = registry.get(tool_call.tool_name)

        if func is None:
            tool_call.status = "failed"
            tool_call.error = f"Unknown tool: {tool_call.tool_name}"
            executed.append(tool_call)
            logger.warning("Unknown tool requested: %s", tool_call.tool_name)
            continue

        start_ms = time.monotonic() * 1000
        try:
            result = await func(
                db=db,
                user_id=user_id,
                **tool_call.arguments,
            )
            tool_call.result = result
            tool_call.status = "success"
            logger.info("Tool %s executed successfully", tool_call.tool_name)
        except Exception as exc:
            tool_call.status = "failed"
            tool_call.error = str(exc)
            logger.error("Tool %s failed: %s", tool_call.tool_name, exc)
        finally:
            elapsed = time.monotonic() * 1000 - start_ms
            logger.debug("Tool %s took %.1f ms", tool_call.tool_name, elapsed)

        executed.append(tool_call)

    return executed
