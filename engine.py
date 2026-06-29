import os
import json
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Literal

# 1. ARCHITECTURAL SCHEMA BOUNDARIES
class ScheduleItem(BaseModel):
    time_slot: str = Field(description="e.g., '09:00 - 10:30 AM'")
    activity_title: str = Field(description="High-leverage performance task description")
    classification: Literal["focus", "meeting", "break"] = Field(description="Operational classification tag")
    badge_text: str = Field(description="Uppercase label string like 'FOCUS' or 'BREAK'")
    vulnerability_warning: str = Field(description="Explicit disruption risk warning matching this slot")

class DashboardPayload(BaseModel):
    focus_score: int = Field(description="Productivity score from 0 to 100 based on structure design")
    focus_time: str = Field(description="Summed deep-work block hours, e.g., '4h 15m'")
    tasks_completed: str = Field(description="Completion metrics format fraction, e.g., '0/6'")
    adversarial_brief: str = Field(description="Brutally honest critique pinpointing execution traps in user inputs")
    schedule: List[ScheduleItem]

class SkillScore(BaseModel):
    skill: str
    score: int

class SkillTrackerResponse(BaseModel):
    skills: List[SkillScore]
    insight: str

# 2. SEED ENGINE INFERENCE
def generate_initial_schedule(user_raw_goals: str) -> DashboardPayload:
    """Invokes Gemini 2.5 Pro utilizing native structural constraint processing."""
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

    system_prompt = (
        "You are Apex, an elite AI efficiency engineer and performance mentor. "
        "Analyze the user's disorganized daily goals, design an optimal high-performance schedule layer, "
        "and calculate real-time baseline metrics. You must strictly output JSON matching the required schema structure."
    )

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"User Raw Input Tasks:\n{user_raw_goals}",
        config={
            'system_instruction': system_prompt,
            'response_mime_type': 'application/json',
            'response_schema': DashboardPayload,
            'temperature': 0.1
        }
    )
    return response.parsed

# 3. REAL-TIME REPAIR LOOP MECHANISM
def repair_schedule(current_schedule_dict: dict, disruption_event: str) -> DashboardPayload:
    """Intercepts active state, models real-world friction, and mutates variables without breaking the schema."""
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

    repair_prompt = (
        f"CRITICAL SYSTEM DISRUPTION: The user's day has fractured due to this issue: '{disruption_event}'.\n"
        f"ACTIVE TIMELINE METRICS DATA STATE: {str(current_schedule_dict)}\n"
        "Re-evaluate the open schedule hours. Compress blocks, shift time slots downward, and recalculate "
        "the Focus Score penalty based on this real-world interference. Protect high-value Focus slots first."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=repair_prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": DashboardPayload,
            "temperature": 0.1
        }
    )

    return response.parsed

def generate_ai_coach(
    momentum_score: int,
    completed_tasks: int,
    total_tasks: int,
    upcoming_tasks: list
) -> str:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

    # 🧠 Calculate the true mental cost of the remaining day
    total_cognitive_load = sum(task.get("cognitive_load", 5) for task in upcoming_tasks if isinstance(task, dict))
    total_dopamine_drain = sum(task.get("dopamine_drain", 5) for task in upcoming_tasks if isinstance(task, dict))

    coach_prompt = f"""
    You are an elite productivity coach for a high-performance engineer.

    Current Metrics:
    - Momentum Score: {momentum_score}
    - Tasks Completed: {completed_tasks}/{total_tasks}

    Upcoming Burden:
    - The remaining tasks have a total Cognitive Load of {total_cognitive_load} and a Dopamine Drain of {total_dopamine_drain}.
    - Upcoming Tasks context: {upcoming_tasks}

    Analyze the user's performance and remaining mental energy requirements.

    Return:
    - One specific, hard-hitting observation about their current trajectory.
    - One tactical recommendation (e.g., "Step away for 10 mins before tackling the system design" or "Your momentum is peaking, crush the debugging session now").

    Maximum 50 words. Be direct, punchy, and concise.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=coach_prompt,
        )
        return response.text
    except Exception as e:
        print(f"Coach Engine Error: {e}")
        return "System traffic high. Keep pushing forward and focus on the immediate next block."

def generate_future_self(
    momentum_score: int,
    completed_tasks: int,
    total_tasks: int,
    tasks_list: list  # <--- Added this to give the AI context!
) -> str:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

    # Extract just the task titles so the AI knows WHAT the user is actually building
    task_context = [task.get("title", "Unknown Task") for task in tasks_list if isinstance(task, dict)]
    print(f"\n=== DEBUG: TASKS PASSED TO FUTURE SELF ===\n{task_context}\n==========================================\n")
    future_prompt = f"""
    You are a predictive AI simulator tracking an engineer's project trajectory.

    Current State:
    - Momentum Score: {momentum_score}/100
    - Tasks Completed: {completed_tasks}/{total_tasks}
    - Specific Projects/Tasks in Pipeline: {task_context}

    CRITICAL JUDGING REQUIREMENT: You MUST explicitly reference the actual tasks or project names from the pipeline list above in your prediction. Do not give generic advice. Tell the user exactly what will happen to these specific systems or topics (e.g., if they have 'DBMS practice', mention their database proficiency or schema design) in 30 days if this 50% momentum trend continues.

    Return:
    - One highly specific, blunt 30-day outcome.
    - One tactical architectural recommendation.

    Maximum 60 words. Be sharp, context-driven, and direct.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=future_prompt
        )
        return response.text
    except Exception:
        return (
            "Future projection unavailable. "
            "Increase daily focus completion to improve long-term outcomes."
        )

def generate_opportunity_radar(
    momentum_score: int,
    blocks: list
) -> dict:
    remaining_tasks = [
        b for b in blocks
        if b.get("state") != "completed"
    ]

    if not remaining_tasks:
        return {
            "action": "All tasks completed",
            "reason": "No remaining actions require attention.",
            "badge": "Completed"
        }

    scored_tasks = []
    for task in remaining_tasks:
        score = 0
        if task.get("block_type") == "focus":
            score += 50
        if task.get("high_intensity"):
            score += 20
        score += 10
        scored_tasks.append((score, task))

    scored_tasks.sort(reverse=True, key=lambda x: x[0])
    best_task = scored_tasks[0][1]

    badge = "High Leverage"
    if momentum_score < 40:
        badge = "Momentum Recovery"
    elif best_task.get("block_type") == "focus":
        badge = "Critical Path"

    return {
        "action": best_task.get("title", "Unknown Task"),
        "reason": (
            "This task provides the highest immediate productivity gain "
            "based on your remaining schedule."
        ),
        "badge": badge
    }

def generate_skill_tracker(
    momentum_score: int,
    streak: int,
    blocks: list
) -> dict:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

    completed = sum(1 for b in blocks if b.get("state") == "completed")
    total = len(blocks)
    focus_blocks = sum(1 for b in blocks if b.get("block_type") == "focus" and b.get("state") == "completed")

    prompt = f"""
Analyze the user's productivity state.
Momentum Score: {momentum_score}%
Current Streak: {streak} days
Tasks Completed: {completed}/{total}
Focus Blocks Completed: {focus_blocks}

Generate a skill tracker assessment estimating realistic scores (0-100) for:
1. Problem Solving
2. Time Management
3. Consistency
4. Deep Work

Provide a single, punchy, 1-sentence AI coaching insight (max 15 words) evaluating their current vector trajectory.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": SkillTrackerResponse,
                "temperature": 0.2
            }
        )

        if response.parsed:
            # Handle Pydantic cross-compatibility safely
            return response.parsed.model_dump() if hasattr(response.parsed, 'model_dump') else response.parsed.dict()
        else:
            return json.loads(response.text)

    except Exception:
        return {
            "skills": [
                {"skill": "Problem Solving", "score": 10},
                {"skill": "Time Management", "score": 10},
                {"skill": "Consistency", "score": 10},
                {"skill": "Deep Work", "score": 10}
            ],
            "insight": "Complete more focus sessions to calibrate your skill profile."
        }
def generate_eod_insight(momentum_score: int, completed_tasks: int, total_tasks: int) -> str:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

    prompt = f"""
    Analyze the user's day:
    Momentum Score: {momentum_score}%
    Tasks: {completed_tasks}/{total_tasks}

    Return exactly ONE sentence (maximum 15 words) interpreting their daily performance.
    Examples: "Morning focus offset afternoon interruptions." or "Consistent deep work created strong end-of-day momentum."
    No fluff, no coaching, no paragraphs.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"temperature": 0.3}
        )
        return response.text.strip()
    except Exception:
        return "Consistent effort created a stable baseline for tomorrow."
def get_cognitive_load_analysis(task_title: str, task_context: str) -> dict:
    """Asks Gemini to weigh the task's true cost."""
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    prompt = f"""
    Analyze the following task: "{task_title}" with context: "{task_context}"
    Return ONLY a JSON object: {{"cognitive_load": int(1-10), "dopamine_drain": int(1-10)}}
    - Use high cognitive load for complex system design or deep coding.
    - Use high dopamine drain for tedious, low-reward administrative work.
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception:
        return {"cognitive_load": 5, "dopamine_drain": 5}
# Add these imports to the top of engine.py if they aren't there:
# from google.genai import types
# import json

def get_cognitive_load_analysis(client, task_title, task_context):
    """Asks Gemini to weigh the task's true cost."""
    prompt = f"""
    Analyze the following task: "{task_title}" with context: "{task_context}"
    Return ONLY a JSON object: {{"cognitive_load": int(1-10), "dopamine_drain": int(1-10)}}
    - Use high cognitive load for complex system design or deep coding.
    - Use high dopamine drain for tedious, low-reward administrative work.
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    return json.loads(response.text)
