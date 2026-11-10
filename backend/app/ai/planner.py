"""AI planner — builds ActionPlan from user command + context."""
import json
import logging
from typing import Any, Dict, Optional

from app.ai.provider import AIProvider
from app.schemas.ai_schemas import ActionPlan, AIResponse, ToolCall

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are LifeOS AI, an intelligent personal productivity assistant.
Your job is to understand the user's natural-language command and create an action plan.

You have access to the following tools:
- create_task(title, description, priority, status, due_date, tags, project_id, is_ai_generated)
- update_task(task_id, title, description, priority, status, due_date)
- delete_task(task_id)
- list_tasks(status, priority, project_id, limit, sort_by)
- mark_overdue_tasks()
- create_project(name, description, status, color, deadline)
- list_projects(status)
- create_calendar_event(title, description, start_time, end_time, all_day, event_type, task_id)
- list_calendar_events(start, end)
- generate_report(report_type, include_tasks, include_projects, include_time_analysis)
- create_automation(name, description, trigger_type, trigger_config, actions, is_active)

Respond with a JSON object in this exact format:
{
  "intent": "short_intent_identifier",
  "description": "Human-readable description of what you will do",
  "tool_calls": [
    {
      "tool_name": "tool_name_here",
      "arguments": { ... }
    }
  ],
  "estimated_duration_ms": 500,
  "user_message": "Friendly message to show the user"
}

Always include a user_message. Use clear, helpful language.
"""


async def create_plan(
    command: str,
    context: Dict[str, Any],
    provider: AIProvider,
) -> tuple[ActionPlan, str]:
    """
    Send the user command + context to the AI provider and parse the response
    into an ActionPlan with a list of ToolCall steps.

    Returns:
        (ActionPlan, user_message: str)
    """
    context_summary = json.dumps(context, indent=2, default=str)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"User Context:\n{context_summary}\n\n"
                f"User Command: {command}"
            ),
        },
    ]

    try:
        response: AIResponse = await provider.complete(messages)

        # If the mock/real provider already returned a plan, use it
        if response.plan:
            return response.plan, response.content

        # Otherwise try to parse JSON from the content
        content = response.content.strip()
        # Strip markdown code fences if present
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])

        data = json.loads(content)
        tool_calls = [
            ToolCall(
                tool_name=tc["tool_name"],
                arguments=tc.get("arguments", {}),
            )
            for tc in data.get("tool_calls", [])
        ]
        plan = ActionPlan(
            intent=data.get("intent", "unknown"),
            description=data.get("description", ""),
            tool_calls=tool_calls,
            estimated_duration_ms=data.get("estimated_duration_ms", 0),
        )
        user_message = data.get("user_message", response.content)
        return plan, user_message

    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("Could not parse AI response as plan: %s", exc)
        # Return a minimal no-op plan with the raw response as the message
        plan = ActionPlan(
            intent="chat",
            description="General chat response — no tool calls",
            tool_calls=[],
            estimated_duration_ms=0,
        )
        return plan, response.content
