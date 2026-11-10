"""Mock AI provider — generates realistic structured responses for development."""
import json
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from app.ai.provider import AIProvider
from app.schemas.ai_schemas import ActionPlan, AIResponse, ToolCall

logger = logging.getLogger(__name__)


class MockAIProvider(AIProvider):
    """
    Realistic mock AI provider for development and testing.
    Generates structured JSON responses that look like real tool calls.
    All responses are clearly labelled with [MOCK AI].
    """

    @property
    def provider_name(self) -> str:
        return "MockAI"

    async def complete(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AIResponse:
        """Generate a realistic mock response based on the last user message."""
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "").lower()
                break

        plan, content = self._generate_response(user_message)
        return AIResponse(content=content, plan=plan)

    def _generate_response(self, command: str) -> tuple[Optional[ActionPlan], str]:
        """Route command keywords to appropriate mock response generators."""
        cmd = command.lower()

        if any(kw in cmd for kw in ["create task", "add task", "new task", "task to"]):
            return self._plan_create_task(command)

        if any(kw in cmd for kw in ["plan my day", "schedule today", "daily plan", "what should i do today"]):
            return self._plan_my_day(command)

        if any(kw in cmd for kw in ["generate report", "weekly report", "productivity report", "summary report"]):
            return self._plan_generate_report(command)

        if any(kw in cmd for kw in ["create project", "new project", "start project"]):
            return self._plan_create_project(command)

        if any(kw in cmd for kw in ["schedule", "add event", "create event", "meeting"]):
            return self._plan_create_event(command)

        if any(kw in cmd for kw in ["list task", "show task", "my task", "pending task"]):
            return self._plan_list_tasks(command)

        if any(kw in cmd for kw in ["automate", "create automation", "schedule automation"]):
            return self._plan_create_automation(command)

        # Default: general assistant response
        return None, (
            "[MOCK AI] I understand your request. I'm the LifeOS AI assistant running in mock mode. "
            "To use the real BharatCode AI, set AI_PROVIDER=bharatcode and provide a valid API key in your .env file. "
            f'\n\nYou asked: "{command}"\n\n'
            "I can help you with:\n"
            "- Creating and managing tasks\n"
            "- Planning your day\n"
            "- Generating productivity reports\n"
            "- Creating projects and calendar events\n"
            "- Setting up automations\n"
        )

    def _plan_create_task(self, command: str) -> tuple[ActionPlan, str]:
        # Extract a reasonable task title from the command
        title = re.sub(r"(?i)(create task|add task|new task|task to|task:)\s*", "", command).strip()
        title = title.capitalize() or "New Task from AI"

        tool_calls = [
            ToolCall(
                tool_name="create_task",
                arguments={
                    "title": title,
                    "description": f"[MOCK AI] Auto-generated task from command: '{command}'",
                    "priority": "medium",
                    "status": "todo",
                    "due_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
                    "tags": ["ai-generated"],
                    "is_ai_generated": True,
                },
            )
        ]
        plan = ActionPlan(
            intent="create_task",
            description=f"[MOCK AI] Create a new task: '{title}'",
            tool_calls=tool_calls,
            estimated_duration_ms=200,
        )
        content = (
            f"[MOCK AI] ✅ I'll create a task titled **'{title}'** with medium priority, "
            f"due tomorrow. The task has been tagged as AI-generated."
        )
        return plan, content

    def _plan_my_day(self, command: str) -> tuple[ActionPlan, str]:
        today = datetime.now(timezone.utc)
        tomorrow = today + timedelta(days=1)

        tool_calls = [
            ToolCall(
                tool_name="list_tasks",
                arguments={"status": "todo", "limit": 10, "sort_by": "priority"},
            ),
            ToolCall(
                tool_name="list_calendar_events",
                arguments={
                    "start": today.isoformat(),
                    "end": tomorrow.isoformat(),
                },
            ),
            ToolCall(
                tool_name="create_task",
                arguments={
                    "title": "Morning review — check emails and messages",
                    "priority": "high",
                    "status": "todo",
                    "due_date": today.replace(hour=9, minute=0).isoformat(),
                    "tags": ["daily-plan", "ai-generated"],
                    "is_ai_generated": True,
                },
            ),
        ]
        plan = ActionPlan(
            intent="plan_day",
            description="[MOCK AI] Generate a structured daily plan based on pending tasks and upcoming events.",
            tool_calls=tool_calls,
            estimated_duration_ms=800,
        )
        content = (
            "[MOCK AI] 📅 **Your Daily Plan**\n\n"
            "Here's what I've prepared for you today:\n\n"
            "**Morning (9 AM – 12 PM)**\n"
            "- 🔴 High-priority tasks from your backlog\n"
            "- Review and respond to any pending messages\n\n"
            "**Afternoon (1 PM – 5 PM)**\n"
            "- Work on medium-priority tasks\n"
            "- Attend scheduled meetings\n\n"
            "**Evening (5 PM – 7 PM)**\n"
            "- Review progress, update task statuses\n"
            "- Plan for tomorrow\n\n"
            "_I've retrieved your pending tasks and today's calendar events to build this plan._"
        )
        return plan, content

    def _plan_generate_report(self, command: str) -> tuple[ActionPlan, str]:
        tool_calls = [
            ToolCall(
                tool_name="generate_report",
                arguments={
                    "report_type": "weekly",
                    "include_tasks": True,
                    "include_projects": True,
                    "include_time_analysis": True,
                },
            )
        ]
        plan = ActionPlan(
            intent="generate_report",
            description="[MOCK AI] Generate a comprehensive productivity report.",
            tool_calls=tool_calls,
            estimated_duration_ms=1500,
        )
        content = (
            "[MOCK AI] 📊 **Productivity Report**\n\n"
            "Generating your weekly productivity report...\n\n"
            "**Summary (Mock Data)**\n"
            "- ✅ Tasks completed this week: **12**\n"
            "- 🔄 Tasks in progress: **5**\n"
            "- ⏰ Overdue tasks: **2**\n"
            "- 📁 Active projects: **3**\n"
            "- 🏆 Productivity score: **78/100**\n\n"
            "_Real metrics will be computed from your actual data when the tool executes._"
        )
        return plan, content

    def _plan_create_project(self, command: str) -> tuple[ActionPlan, str]:
        name = re.sub(r"(?i)(create project|new project|start project)\s*", "", command).strip()
        name = name.capitalize() or "New Project"

        tool_calls = [
            ToolCall(
                tool_name="create_project",
                arguments={
                    "name": name,
                    "description": f"[MOCK AI] Project created from command: '{command}'",
                    "status": "active",
                    "color": "#6366f1",
                },
            )
        ]
        plan = ActionPlan(
            intent="create_project",
            description=f"[MOCK AI] Create a new project: '{name}'",
            tool_calls=tool_calls,
            estimated_duration_ms=200,
        )
        content = f"[MOCK AI] 🗂️ Creating project **'{name}'**. I'll set it up as an active project with a purple color theme."
        return plan, content

    def _plan_create_event(self, command: str) -> tuple[ActionPlan, str]:
        title = re.sub(r"(?i)(schedule|add event|create event|meeting:?)\s*", "", command).strip()
        title = title.capitalize() or "New Meeting"
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=1)

        tool_calls = [
            ToolCall(
                tool_name="create_calendar_event",
                arguments={
                    "title": title,
                    "description": f"[MOCK AI] Event created from command: '{command}'",
                    "start_time": start.isoformat(),
                    "end_time": end.isoformat(),
                    "all_day": False,
                    "event_type": "meeting",
                },
            )
        ]
        plan = ActionPlan(
            intent="create_event",
            description=f"[MOCK AI] Schedule a calendar event: '{title}'",
            tool_calls=tool_calls,
            estimated_duration_ms=200,
        )
        content = (
            f"[MOCK AI] 📅 Scheduling **'{title}'** for 1 hour from now "
            f"({start.strftime('%H:%M')} – {end.strftime('%H:%M')} UTC)."
        )
        return plan, content

    def _plan_list_tasks(self, command: str) -> tuple[ActionPlan, str]:
        tool_calls = [
            ToolCall(
                tool_name="list_tasks",
                arguments={"status": "todo", "limit": 20, "sort_by": "priority"},
            )
        ]
        plan = ActionPlan(
            intent="list_tasks",
            description="[MOCK AI] Retrieve your pending tasks.",
            tool_calls=tool_calls,
            estimated_duration_ms=100,
        )
        content = "[MOCK AI] 📋 Fetching your pending tasks sorted by priority..."
        return plan, content

    def _plan_create_automation(self, command: str) -> tuple[ActionPlan, str]:
        tool_calls = [
            ToolCall(
                tool_name="create_automation",
                arguments={
                    "name": "Daily Morning Briefing",
                    "description": "[MOCK AI] Send a daily summary every morning at 9 AM.",
                    "trigger_type": "schedule",
                    "trigger_config": {"cron": "0 9 * * *"},
                    "actions": [{"type": "generate_report", "report_type": "daily"}],
                    "is_active": True,
                },
            )
        ]
        plan = ActionPlan(
            intent="create_automation",
            description="[MOCK AI] Create a scheduled automation.",
            tool_calls=tool_calls,
            estimated_duration_ms=200,
        )
        content = (
            "[MOCK AI] ⚡ Creating a **Daily Morning Briefing** automation that runs every day at 9 AM. "
            "It will generate a daily summary report for you."
        )
        return plan, content
