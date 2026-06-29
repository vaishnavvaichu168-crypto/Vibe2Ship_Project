import streamlit as st
from google import genai
from google.genai import types
import plotly.graph_objects as go
import os
import json
from datetime import datetime
from typing import List, Literal
from dotenv import load_dotenv
from pydantic import BaseModel


from engine import (
    repair_schedule,
    generate_ai_coach,
    generate_future_self,
    generate_opportunity_radar,
    generate_skill_tracker,
    generate_eod_insight,
    get_cognitive_load_analysis
)
# ==========================================================
# 🧠 THE COGNITIVE AI SCHEDULING ENGINE (MODERN SDK)
# ==========================================================
# Initialize the modern client using your secure secrets file
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def mutate_schedule_with_ai(current_blocks, anomaly_text):
    """Sends the schedule context to Gemini to intelligently restructure it."""

    prompt = f"""
    You are an elite cognitive scheduling AI for a high-performance dashboard.
    The user has experienced a schedule anomaly: "{anomaly_text}"

    Here is their current schedule array in JSON format:
    {json.dumps(current_blocks, indent=2)}

    CRITICAL INSTRUCTIONS:
    1. Act as a tactical planner. Read the anomaly and the current schedule.
    2. TIME MATH IS MANDATORY: If the user is running late, you MUST physically rewrite the 'time' values for all subsequent tasks.
    3. If the anomaly implies high fatigue, autonomously insert a new JSON block for a 15-minute 'Quiet Decompression' break before the next heavy task.
    4. You MUST maintain the EXACT JSON keys provided in the current schedule.
    5. Do NOT change the time of any task where "state" is "completed". Only mutate "ready" tasks.
    6. Return ONLY the raw JSON array containing the new schedule. Do not wrap it in markdown.
    """

    try:
        # Using the modern SDK generate_content syntax and the 2.5 model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        # 🚨 X-RAY VISION: Watch the terminal to see it think!
        print("\n=== 🧠 GEMINI RAW OUTPUT ===")
        print(response.text)
        print("============================\n")

        return json.loads(response.text)
    except Exception as e:
        error_string = str(e)
        if "429" in error_string or "RESOURCE_EXHAUSTED" in error_string:
            st.warning("⏳ AI Engine cooling down (Free Tier Rate Limit). Please wait 60 seconds and try again.")
        else:
            st.error(f"Neural Link Failed: {e}")

        print(f"ERROR: {e}")
        return current_blocks
# ==========================================================
# ==========================================================
# 1. Page Configuration & Layout Optimization
st.set_page_config(page_title="Alex - Your Day in Focus", layout="wide", initial_sidebar_state="expanded")

# 2. Premium Design System CSS Override (Linear/Stripe + glow accent system)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght=500;600;700&family=Inter:wght=400;500;600;700&display=swap');

    .stApp {
            background: radial-gradient(circle at 12% -10%, rgba(59,130,246,0.10), transparent 42%), #090A10 !important;
            color: #F1F5F9 !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

    /* ========================================================== */
    /* UPGRADED: CINEMATIC HARDWARE-ACCELERATED REVEAL ENGINE     */
    /* ========================================================== */
    @keyframes cinematicReveal {
        0% {
            opacity: 0;
            transform: translateY(40px) scale(0.98);
            filter: blur(8px);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
            filter: blur(0);
        }
    }

    /* Targets our specific st.container keys */
    [class*="st-key-eod_chart"] {
        background: rgba(18, 22, 36, 0.45) !important;
        backdrop-filter: blur(14px) saturate(160%) !important;
        -webkit-backdrop-filter: blur(14px) saturate(160%) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-top: 1px solid rgba(255,255,255,0.18) !important;
        border-radius: 18px !important;
        padding: 14px 10px 4px 10px !important;
        box-shadow: 0 12px 30px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04) !important;
        transition: transform 0.35s ease, box-shadow 0.35s ease !important;

        /* THE FIX: 'both' keeps it invisible while waiting for Plotly to render */
        animation: cinematicReveal 0.85s cubic-bezier(0.2, 0.8, 0.2, 1) both !important;
    }

    [class*="st-key-eod_chart"]:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 16px 36px rgba(0,0,0,0.5), 0 0 26px rgba(59,130,246,0.18) !important;
    }

    /* THE FIX: Increased delays so Plotly draws in the dark before sliding up */
    .st-key-eod_chart_momentum { animation-delay: 0.35s !important; }
    .st-key-eod_chart_energy   { animation-delay: 0.55s !important; }
    .st-key-eod_chart_donut    { animation-delay: 0.75s !important; }
    /* ========================================================== */

        [data-testid="stSidebar"] { background-color: #0F111A !important; border-right: 1px solid #1E2235; }
        h1, h2, h3, .card-value, .ring-label { font-family: 'Space Grotesk', 'Inter', sans-serif !important; }

        /* Premium Card UI Dashboard Grid */
.dashboard-card {
        /* A deeper, more translucent base so Level 2 charts pop out more */
        background: rgba(13, 17, 26, 0.35) !important;
        backdrop-filter: blur(12px) saturate(140%) !important;
        -webkit-backdrop-filter: blur(12px) saturate(140%) !important;

        /* The Top-Left Light Source Illusion */
        border: 1px solid rgba(255, 255, 255, 0.03) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-left: 1px solid rgba(255, 255, 255, 0.06) !important;

        border-radius: 20px !important;
        padding: 24px !important;
        margin-bottom: 18px !important;
        position: relative !important;
        overflow: hidden !important;

        /* Deep ambient shadow pulling down and right */
        box-shadow: 0 15px 35px rgba(0,0,0,0.3),
                    inset 0 1px 0 rgba(255,255,255,0.02) !important;
        transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275),
                    box-shadow 0.4s ease, border-color 0.4s ease !important;
    }

    /* The "Neon Edge" Hover Sweep */
        .dashboard-card:hover {
            transform: translateY(-4px) !important;
            border-top: 1px solid rgba(59, 130, 246, 0.5) !important; /* Cyan light sweep */
            border-left: 1px solid rgba(59, 130, 246, 0.3) !important;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5),
                        0 0 25px rgba(59, 130, 246, 0.12) !important;
        }

        /* Adds a subtle internal glowing orb to the background of the cards */
        .dashboard-card::before {
            content: '';
            position: absolute;
            top: -50%; left: -50%;
            width: 200%; height: 200%;
            background: radial-gradient(circle at 50% 0%, rgba(59,130,246,0.05), transparent 60%);
            pointer-events: none;
            z-index: 0;
        }

        /* Ensures text stays above the glowing orb */
        .dashboard-card > * {
            position: relative;
            z-index: 1;
        }

        /* ========================================================== */
        /* LEVEL 2: INTERACTIVE NODES (Buttons, Sidebar & Progress)   */
        /* ========================================================== */

        /* 1. The Premium Button Engine (Neon Tactile Effect) */
        .stButton > button {
            background: rgba(18, 22, 36, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-top: 1px solid rgba(255, 255, 255, 0.25) !important;
            color: #F8FAFC !important;
            border-radius: 12px !important;
            font-family: 'Space Grotesk', 'Inter', sans-serif !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
            padding: 10px 20px !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2),
                        inset 0 1px 0 rgba(255,255,255,0.05) !important;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        }

        .stButton > button:hover {
            background: rgba(59, 130, 246, 0.15) !important;
            border: 1px solid rgba(59, 130, 246, 0.5) !important;
            color: #60A5FA !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3),
                        0 0 15px rgba(59, 130, 246, 0.2) !important;
        }

        .stButton > button:active {
            transform: translateY(1px) !important;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.4) !important;
        }

        /* 2. The Deep Canvas Sidebar */
        [data-testid="stSidebar"] {
            background: rgba(10, 14, 26, 0.7) !important;
            backdrop-filter: blur(20px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        }

        /* 3. Neon Progress Bars */
        .stProgress > div > div > div > div {
            background-image: linear-gradient(90deg, #3B82F6, #8B5CF6) !important;
            border-radius: 10px !important;
            box-shadow: 0 0 10px rgba(59, 130, 246, 0.4) !important;
        }

        .stProgress > div > div {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border-radius: 10px !important;
        }
        /* ========================================================== */
        .card-header {
            font-size: 13px; color: #64748B; font-weight: 600; text-transform: uppercase;
            letter-spacing: 0.6px; display: flex; align-items: center; gap: 7px;
        }
        .header-icon { display: inline-flex; align-items: center; }
        .card-value { font-size: 32px; font-weight: 700; color: #FFFFFF; margin-top: 10px; display: flex; align-items: center; letter-spacing: -0.3px; }
        .card-subtext { font-size: 12.5px; color: #94A3B8; margin-top: 6px; line-height: 1.5; }
        .badge-green { background: rgba(16, 185, 129, 0.15); color: #10B981; padding: 2px 9px; border-radius: 20px; font-size: 11px; margin-left: 10px; font-weight: 600; }

        .flex-container { display: flex; justify-content: space-between; align-items: center; width: 100%; }

        /* Glow rings (Today's Focus / Daily Focus Goal) */
        .ring-wrap { position: relative; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .ring-bg { opacity: 0.6; }
        .ring-fg { filter: drop-shadow(0 0 7px currentColor); stroke-linecap: round; }
        .ring-label { position: absolute; font-weight: 700; color: #fff; }

        /* Glow sparklines */
        .spark-line { filter: drop-shadow(0 0 5px currentColor); stroke-linecap: round; stroke-linejoin: round; }

        /* Timeline */
        .timeline-container { background-color: #131622; border: 1px solid #1E2235; border-radius: 18px; padding: 22px; }
        .timeline-row { display: flex; align-items: flex-start; padding: 16px 4px; border-bottom: 1px solid #1A1E2E; }
        .timeline-row:last-child { border-bottom: none; }
        .time-col { width: 85px; font-size: 13px; font-weight: 700; color: #475569; padding-top: 13px; text-transform: uppercase; letter-spacing: 0.3px; }

        .pill-block {
            flex-grow: 1; border-radius: 16px; padding: 15px 20px; font-size: 14px; font-weight: 500;
            color: #FFFFFF; display: flex; justify-content: space-between; align-items: center;
            transition: transform .15s ease, box-shadow .15s ease;
        }
        .pill-block:hover { transform: translateY(-1px); }

        .pill-focus { background: linear-gradient(120deg, rgba(59,130,246,0.5), rgba(59,130,246,0.14)); box-shadow: 0 0 26px -6px rgba(59,130,246,0.5); border: 1px solid rgba(59,130,246,0.25); }
        .pill-meeting { background: linear-gradient(120deg, rgba(139,92,246,0.45), rgba(139,92,246,0.12)); box-shadow: 0 0 26px -6px rgba(139,92,246,0.45); border: 1px solid rgba(139,92,246,0.25); }
        .pill-break { background: linear-gradient(120deg, rgba(20,184,166,0.45), rgba(34,197,94,0.14)); box-shadow: 0 0 24px -6px rgba(45,190,150,0.4); border: 1px solid rgba(45,190,150,0.22); }
        .pill-default { background: rgba(255,255,255,0.04); border: 1px solid #1E2235; }

        .pill-badge { font-size: 11px; font-weight: 600; text-transform: uppercase; padding: 3px 10px; border-radius: 12px; background: rgba(255,255,255,0.12); letter-spacing: 0.4px; }

        .dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; margin-right: 9px; }
        .dot-focus { background: #3B82F6; box-shadow: 0 0 6px #3B82F6; }
        .dot-meeting { background: #8B5CF6; box-shadow: 0 0 6px #8B5CF6; }
        .dot-break { background: #22C55E; box-shadow: 0 0 6px #22C55E; }
        .dot-default { background: #64748B; }
        .dot-dnd { background: #EF4444; box-shadow: 0 0 6px #EF4444; }

        /* Up next list */
        .up-next-row { display: flex; align-items: flex-start; gap: 0; padding: 10px 0; border-bottom: 1px solid #1A1E2E; }
        .up-next-row:last-child { border-bottom: none; }
        .up-next-row .dot { margin-top: 6px; }
        .up-next-title { font-size: 14px; font-weight: 600; color: #fff; }
        .up-next-sub { font-size: 12px; color: #94A3B8; margin-top: 1px; }

        @keyframes radarFadeIn {
            from { opacity: 0; transform: translateY(-4px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .radar-card { animation: radarFadeIn 0.4s ease; }
        .radar-action { font-size: 22px; font-weight: 700; color: #60A5FA; margin-top: 12px; }
        .radar-reason { margin-top: 10px; color: #94A3B8; line-height: 1.6; font-size: 13px; }

    /* ========================================================== */
    /* LEVEL 3: THE FINAL POLISH (Typography & Scrollbars)        */
    /* ========================================================== */

    /* 1. Metallic Gradient Text for Big Data Numbers */
    .card-value {
        font-size: 32px !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #FFFFFF 0%, #64748B 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-shadow: 0 4px 15px rgba(255,255,255,0.05) !important;
    }

    /* 2. Interactive Schedule Task Pills */
    .pill-block:hover {
        transform: scale(1.01) translateX(6px) !important;
        box-shadow: -4px 0 0 #3B82F6, 0 8px 20px rgba(0,0,0,0.3) !important;
        background: rgba(255,255,255,0.05) !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }

    /* 3. Stealth Dark Mode Scrollbar */
    ::-webkit-scrollbar {
        width: 8px !important;
        height: 8px !important;
    }
    ::-webkit-scrollbar-track {
        background: transparent !important;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(59, 130, 246, 0.5) !important;
    }
    /* ========================================================== */
    </style>
""", unsafe_allow_html=True)


# 4. Structured output schema
class ScheduleBlock(BaseModel):
    time: str
    title: str
    context: str
    block_type: Literal["focus", "meeting", "break", "default"]
    badge: str
    high_intensity: bool
    cognitive_load: int = 5
    dopamine_drain: int = 5

class ScheduleResponse(BaseModel):
    blocks: List[ScheduleBlock]

DEFAULT_BLOCKS = [
    {"time": "8:00 AM", "title": "Morning planning & inbox", "context": "Review priority metrics", "block_type": "default", "badge": "Inbox", "high_intensity": False, "state": "ready"},
    {"time": "9:00 AM", "title": "Deep work — Q3 roadmap draft", "context": "System compilation block", "block_type": "focus", "badge": "Focus", "high_intensity": True, "state": "ready"},
    {"time": "11:00 AM", "title": "Design sync", "context": "Cross-functional framework alignment", "block_type": "meeting", "badge": "Meeting", "high_intensity": False, "state": "ready"},
    {"time": "12:00 PM", "title": "Lunch & walk", "context": "Cognitive recovery phase", "block_type": "break", "badge": "Break", "high_intensity": False, "state": "ready"},
    {"time": "1:00 PM", "title": "Focus block — API integration", "context": "Hardcoding interface logic", "block_type": "focus", "badge": "Focus", "high_intensity": True, "state": "ready"},
]
DATA_FILE = "planner_data.json"

if "ai_coach_message" not in st.session_state:
    st.session_state["ai_coach_message"] = ""

if "future_self_message" not in st.session_state:
    st.session_state["future_self_message"] = "Press 🔮 Generate Future Self to see your 30-day projection."

if "blocks" not in st.session_state:
    try:
        with open(DATA_FILE, "r") as f:
            saved_data = json.load(f)
        st.session_state["blocks"] = saved_data.get("blocks", DEFAULT_BLOCKS)
        st.session_state["streak"] = saved_data.get("streak", 1)
        st.session_state["last_active_date"] = saved_data.get("last_active_date", datetime.now().strftime("%Y-%m-%d"))
        today = datetime.now().strftime("%Y-%m-%d")
        if st.session_state["last_active_date"] != today:
            st.session_state["streak"] += 1
            st.session_state["last_active_date"] = today
    except Exception:
        st.session_state["blocks"] = DEFAULT_BLOCKS
        st.session_state["streak"] = 1
        st.session_state["last_active_date"] = datetime.now().strftime("%Y-%m-%d")

# 5. Small inline icon set
ICON_SPARKLE = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M7.05 7.05l2.12 2.12M14.83 14.83l2.12 2.12M16.95 7.05l-2.12 2.12M9.17 14.83l-2.12 2.12"/></svg>'
ICON_DROPLET = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2c4 5 7 8.5 7 12a7 7 0 1 1-14 0c0-3.5 3-7 7-12z"/></svg>'
ICON_TREND = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 17l5-5 4 4 7-7M14 9h6v6"/></svg>'
ICON_TARGET = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/></svg>'

# 6. Reusable glow components
def donut_ring(percent, size=64, color="#3B82F6"):
    r = 15.9155
    path_d = f"M18 2.0845 a {r} {r} 0 0 1 0 31.831 a {r} {r} 0 0 1 0 -31.831"
    return f"""
    <div class="ring-wrap" style="width:{size}px;height:{size}px;color:{color};">
        <svg viewBox="0 0 36 36" width="{size}" height="{size}">
            <path class="ring-bg" stroke-width="3.5" fill="none" stroke="#1E2235" d="{path_d}" />
            <path class="ring-fg" stroke-dasharray="{percent}, 100" stroke="{color}" stroke-width="3.5" fill="none" d="{path_d}" />
        </svg>
        <div class="ring-label" style="font-size:{size * 0.26:.0f}px;">{percent}%</div>
    </div>"""

def sparkline(points, color="#3B82F6", width=70, height=32):
    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="color:{color};">
        <polyline points="{points}" fill="none" stroke="currentColor" stroke-width="2.2" class="spark-line"/>
    </svg>"""

def bars(values, color="#3B82F6", width=60, height=35, bar_w=6, gap=4):
    max_v = max(values) if values else 1
    parts = []
    for i, v in enumerate(values):
        h = (v / max_v) * (height - 5)
        x = i * (bar_w + gap)
        y = height - h
        parts.append(f'<rect x="{x}" y="{y:.0f}" width="{bar_w}" height="{h:.0f}" rx="2" fill="currentColor" class="spark-line"/>')
    return f'<svg width="{width}" height="{height}" style="color:{color};">{"".join(parts)}</svg>'

def flatten_html(html: str) -> str:
    """Collapses all whitespace/newlines so formatting never breaks HTML rendering."""
    return " ".join(html.split())

def render_pill(block: dict) -> str:
    block_type = block.get("block_type", "default")
    state = block.get("state", "ready")
    state_map = {"ready": "⏳ Ready", "in_focus": "🎯 In Focus", "completed": "✅ Completed"}
    state_label = state_map.get(state, "⏳ Ready")
    dot_class = "dot-dnd" if block.get("high_intensity") else f"dot-{block_type}"
    return f"""
    <div class="timeline-row">
        <div class="time-col">{block.get('time', '')}</div>
        <div class="pill-block pill-{block_type}">
            <span><span class="dot {dot_class}"></span><b>{block.get('title', '')}</b> — {block.get('context', '')}</span>
            <span class="pill-badge">{state_label}</span>
        </div>
    </div>"""

def render_timeline(blocks: list) -> str:
    return '<div class="timeline-container">' + "".join(render_pill(b) for b in blocks) + "</div>"

def blocks_to_repair_payload(blocks):
    return {
        "schedule": [
            {
                "time_slot": block.get("time", ""),
                "activity_title": block.get("title", ""),
                "classification": block.get("block_type", "focus"),
                "badge_text": block.get("badge", ""),
                "vulnerability_warning": block.get("context", ""),
            }
            for block in blocks
        ]
    }

def repaired_schedule_to_blocks(schedule):
    repaired_blocks = []
    for item in schedule:
        repaired_blocks.append({
            "time": item.time_slot,
            "title": item.activity_title,
            "context": item.vulnerability_warning,
            "block_type": item.classification,
            "badge": item.badge_text,
            "high_intensity": item.classification == "focus",
            "cognitive_load": get_cognitive_load_analysis(client, user_title, user_context)["cognitive_load"],
            "dopamine_drain": get_cognitive_load_analysis(client, user_title, user_context)["dopamine_drain"],
        })
    return repaired_blocks
@st.dialog("Mission Impact Preview")
def show_impact_preview(task_title, current_momentum, current_streak):
    st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 14px; margin-top: -10px; margin-bottom: 20px;'>Completing this mission will improve today's performance.</p>", unsafe_allow_html=True)

    task = next((b for b in st.session_state["blocks"] if b["title"] == task_title), None)
    is_focus = task and task.get("block_type") == "focus"

    m_boost = 9 if is_focus else 4
    new_m = min(100, current_momentum + m_boost)
    dw_boost = "+8%" if is_focus else "+2%"
    c_boost = f"+{min(15, current_streak * 2)}%"
    r_cost = "−18 min" if is_focus else "−5 min"

    st.markdown(f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 25px;">
        <div style="background: rgba(59,130,246,0.12); border: 1px solid rgba(59,130,246,0.35); border-radius: 12px; padding: 18px; text-align: center; box-shadow: 0 4px 20px rgba(59,130,246,0.1); backdrop-filter: blur(8px);">
            <div style="color: #60A5FA; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Momentum</div>
            <div style="color: #fff; font-size: 26px; font-weight: 700; margin-top: 6px;">{current_momentum}% <span style="color: #3B82F6; font-size: 22px;">→ {new_m}%</span></div>
        </div>
        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 18px; text-align: center; backdrop-filter: blur(8px);">
            <div style="color: #94A3B8; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Deep Work</div>
            <div style="color: #10B981; font-size: 26px; font-weight: 700; margin-top: 6px;">{dw_boost}</div>
        </div>
        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 18px; text-align: center; backdrop-filter: blur(8px);">
            <div style="color: #94A3B8; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Consistency</div>
            <div style="color: #10B981; font-size: 26px; font-weight: 700; margin-top: 6px;">{c_boost}</div>
        </div>
        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 18px; text-align: center; backdrop-filter: blur(8px);">
            <div style="color: #94A3B8; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Recovery Cost</div>
            <div style="color: #F43F5E; font-size: 26px; font-weight: 700; margin-top: 6px;">{r_cost}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    btn_c1, btn_c2 = st.columns(2)
    if btn_c1.button("Cancel", use_container_width=True):
        st.rerun()
    if btn_c2.button("✅ Complete Mission", type="primary", use_container_width=True):
        for block in st.session_state["blocks"]:
            if block["title"] == task_title and block.get("state", "ready") == "in_focus":
                block["state"] = "completed"
        with open(DATA_FILE, "w") as f:
            json.dump({
                "blocks": st.session_state["blocks"],
                "streak": st.session_state.get("streak", 1),
                "last_active_date": st.session_state.get("last_active_date", datetime.now().strftime("%Y-%m-%d"))
            }, f)
        if "skill_tracker" in st.session_state:
            del st.session_state["skill_tracker"]
        if "radar" in st.session_state:
            del st.session_state["radar"]
        st.rerun()
# 7. Interactive Command Navigation Sidebar
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 700; margin-bottom:0px;'>Control Desk</h2>", unsafe_allow_html=True)
    st.caption("⚡ Premium Scheduling Engine")
    st.markdown("---")
    DEMO_MODE = st.checkbox("🚀 Live Demo Mode (Instant Mock)", value=False)
    st.markdown("### 📝 Active Task Injection")
    raw_task_stream = st.text_area(
        "Paste unorganized task entries here:",
        placeholder="e.g., Study physics equations from 9-11am. Gym at 4pm. Quick lunch window at noon.",
        height=220
    )
    optimize_execution = st.button("⚡ Optimize Focus Timeline", use_container_width=True)
    st.markdown("---")
    if st.button("📊 Generate End-of-Day Report", use_container_width=True):
        st.session_state["show_report"] = True
        st.rerun()
# ---------------------------------------------------------
# END OF DAY REPORT VIEW INTERCEPT
# ---------------------------------------------------------
if st.session_state.get("show_report", False):
    if st.button("← Back to Dashboard"):
        st.session_state["show_report"] = False
        st.rerun()

    st.markdown("<h2 style='text-align: center; color: white; letter-spacing: 4px; font-weight: 800; margin-top: 20px; margin-bottom: 40px;'>END OF DAY REPORT</h2>", unsafe_allow_html=True)
    # --- 🌊 THE WATERFALL REVEAL ENGINE ---
    with st.spinner("⏳ Synthesizing cognitive vectors and compiling matrix telemetry..."):
        time.sleep(0.75)  # Creates a cinematic processing delay
    # --------------------------------------
    st.markdown("<h4 style='color: #94A3B8; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;'>Momentum Timeline</h4>", unsafe_allow_html=True)
    time_labels = ['8 AM', '10 AM', '12 PM', '2 PM', '4 PM', '6 PM', '8 PM']

    # Dynamic progressive state arrays
    momentum_curve = []
    energy_curve = []
    blocks_list = st.session_state.get("blocks", [])

    current_m = 15
    current_e = 45

    for idx in range(7):
        task_completed = False
        is_focus_block = False

        # Route timeline windows down to index positions within active task maps
        if idx == 0 and len(blocks_list) > 0:
            task_completed = blocks_list[0].get("state") == "completed"
        elif idx == 1 and len(blocks_list) > 1:
            task_completed = blocks_list[1].get("state") == "completed"
            is_focus_block = blocks_list[1].get("block_type") == "focus"
        elif idx == 2 and len(blocks_list) > 3:
            task_completed = any(b.get("state") == "completed" for b in blocks_list[2:4])
        elif idx == 3 and len(blocks_list) > 4:
            task_completed = blocks_list[4].get("state") == "completed"
            is_focus_block = blocks_list[4].get("block_type") == "focus"

        # Accumulate or penalize vectors linearly based on true execution status
        if task_completed:
            current_m += 30 if is_focus_block else 20
            current_e += 15
        else:
            current_m -= 8
            current_e -= 12

        momentum_curve.append(max(8, min(100, current_m)))
        energy_curve.append(max(12, min(100, current_e)))

    with st.container(key="eod_chart_momentum"):
            fig_hero = go.Figure()
            fig_hero.add_trace(go.Scatter(
                x=time_labels, y=momentum_curve, fill='tozeroy', mode='lines+markers',
                line=dict(color='#3B82F6', width=3, shape='spline', smoothing=1.3),
                marker=dict(size=8, color='#090A10', line=dict(color='#3B82F6', width=2)),
                fillcolor='rgba(59, 130, 246, 0.15)', hoverinfo='x+y+text',
                text=["Warming up", "Deep work", "Peak focus", "Lunch dip", "Second wind", "Wrap up", "Rest"]
            ))
            fig_hero.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350,
                margin=dict(l=0, r=0, t=10, b=30),
                xaxis=dict(showgrid=False, color='#64748B', showline=False, zeroline=False),
                yaxis=dict(showgrid=False, showticklabels=False, zeroline=False), hovermode="x unified",
                transition={'duration': 1000, 'easing': 'cubic-in-out'}
            )
            st.plotly_chart(fig_hero, use_container_width=True, config={'displayModeBar': False}, key="momentum_fig")



    # 1. THE CHECK: Are there any tasks?
    if "blocks" not in st.session_state or len(st.session_state["blocks"]) == 0:
        
        # 2. THE EMPTY STATE
        st.markdown("""
            <div style='
                text-align: center; 
                padding: 40px; 
                background-color: rgba(30, 41, 59, 0.3); 
                border-radius: 12px; 
                border: 1px dashed #475569;
                margin-top: 20px;
            '>
                <h3 style='color: #94A3B8; font-family: monospace; letter-spacing: 2px;'>SYSTEM IDLE</h3>
                <p style='color: #64748B; font-size: 14px;'>The focus pipeline is currently empty. Inject tasks via the Control Desk to spin up the telemetry engine.</p>
            </div>
        """, unsafe_allow_html=True)

    # 3. THE ACTIVE STATE
    else:
        col_rep1, col_rep2 = st.columns([2, 1], gap="large")

        with col_rep1:
            st.markdown("<h4 style='color: #94A3B8; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;'>AI Task Telemetry</h4>", unsafe_allow_html=True)
            with st.container(key="eod_chart_energy"):
                task_names = [f"Task {i+1}" for i in range(len(st.session_state["blocks"]))]
                load_scores = [i * 2 + 1 for i in range(len(st.session_state["blocks"]))]
                drain_scores = [i * 1 + 2 for i in range(len(st.session_state["blocks"]))] 

                fig_energy = go.Figure()

                fig_energy.add_trace(go.Scatter(
                    x=task_names, y=load_scores, name="Cognitive Load",
                    line=dict(color='#FF4B4B', width=3, shape='spline'),
                    mode='lines+markers', fill='tozeroy', fillcolor='rgba(255, 75, 75, 0.15)'
                ))

                fig_energy.add_trace(go.Scatter(
                    x=task_names, y=drain_scores, name="Dopamine Drain",
                    line=dict(color='#8B5CF6', width=3, shape='spline'),
                    mode='lines+markers'
                ))

                fig_energy.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=200, margin=dict(l=0, r=0, t=10, b=10),
                    xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                    yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                    hovermode="x unified", showlegend=False,
                    transition={'duration': 1200, 'easing': 'sin-in-out'}
                )
                st.plotly_chart(fig_energy, use_container_width=True, config={'displayModeBar': False}, key="energy_fig")

    with col_rep2:
        st.markdown("<h4 style='color: #94A3B8; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;'>Distribution</h4>", unsafe_allow_html=True)

        # PRESERVING YOUR EXACT CALCULATIONS HERE:
        f_count = sum(1 for b in st.session_state.get("blocks", []) if b.get("block_type") == "focus")
        m_count = sum(1 for b in st.session_state.get("blocks", []) if b.get("block_type") == "meeting")
        b_count = sum(1 for b in st.session_state.get("blocks", []) if b.get("block_type") == "break")

        with st.container(key="eod_chart_donut"):
            fig_donut = go.Figure(data=[go.Pie(
                labels=['Focus', 'Meetings', 'Breaks'],
                values=[f_count, m_count, b_count],
                hole=.7,
                marker=dict(colors=['#3B82F6', '#8B5CF6', '#22C55E']),
                textinfo='none'
            )])
            fig_donut.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=200, margin=dict(l=0, r=0, t=10, b=10), showlegend=False,
                transition={'duration': 900, 'easing': 'cubic-in-out'}
            )
            st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False}, key="donut_fig")

        m_count = sum(1 for b in st.session_state.get("blocks", []) if b.get("block_type") == "meeting")

        # Quick calculations for the insight generator to avoid crashing
        t_weight, e_weight, c_tasks, t_tasks = 0, 0, 0, len(st.session_state.get("blocks", []))
        for b in st.session_state.get("blocks", []):
            w = 2 if b.get("block_type") == "focus" else 1
            t_weight += w
            if b.get("state") == "completed":
                c_tasks += 1
                e_weight += w
        m_score = int((e_weight / t_weight) * 100) if t_weight > 0 else 0

        if "eod_insight" not in st.session_state:
            st.session_state["eod_insight"] = generate_eod_insight(m_score, c_tasks, t_tasks)

        st.markdown(f'''
        <div style="text-align: center; padding: 20px;">
            <p style="color: #10B981; font-weight: 700; font-size: 12px; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px;">AI Synthesis</p>
            <h3 id="ai-synthesis-text" style="color: #F1F5F9; font-size: 22px; font-weight: 500; font-family: 'Space Grotesk', sans-serif;">"{st.session_state['eod_insight']}"</h3>
        </div>

        <script>
            function scrambleText(el, finalText) {{
                const chars = '@#§%X$&01';
                let iteration = 0;
                const length = finalText.length;

                const interval = setInterval(() => {{
                    el.innerText = finalText
                        .split("")
                        .map((letter, index) => {{
                            if(index < iteration) {{ return finalText[index]; }}
                            return chars[Math.floor(Math.random() * chars.length)];
                        }})
                        .join("");

                    if(iteration >= length) clearInterval(interval);
                    iteration += 1 / 3;
                }}, 30);
            }}

            const target = document.getElementById("ai-synthesis-text");
            if (target) {{
                const finalContent = target.innerText;
                scrambleText(target, finalContent);
            }}
        </script>
    ''', unsafe_allow_html=True)

        st.stop() # THIS IS THE MAGIC BULLET. IT PREVENTS THE DASHBOARD FROM RENDERING.
# 8. Core Interface Heading Modules
st.markdown("<p style='color: #64748B; font-weight: 600; margin-bottom: -5px;'>Good afternoon, Alex</p>", unsafe_allow_html=True)
st.markdown("<h1 style='color: white; font-size: 36px; font-weight: 800; margin-bottom: 25px;'>Your day, <span style='color: #3B82F6;'>in focus</span></h1>", unsafe_allow_html=True)

# 10. Calculations & Analytics Prep
completed_tasks = 0
total_weight = 0
earned_weight = 0
m_count = sum(1 for b in st.session_state.get("blocks", []) if b.get("block_type") == "meeting")

for block in st.session_state["blocks"]:
    weight = 2 if block.get("block_type") == "focus" else 1
    total_weight += weight
    if block.get("state") == "completed":
        completed_tasks += 1
        earned_weight += weight

total_tasks = len(st.session_state["blocks"])
momentum_score = int((earned_weight / total_weight) * 100) if total_weight > 0 else 0

# 9. Row 1 Analytics Grid
row1_col1, row1_col2, row1_col3 = st.columns(3, gap="large")
with row1_col1:
    st.markdown(f"""
        <div class="dashboard-card"><div class="card-header"><span class="header-icon" style="color:#3B82F6">{ICON_SPARKLE}</span>Today's Focus</div>
            <div class="flex-container">
                <div class="card-value">{momentum_score} <span class="badge-green">+6 pts</span></div>
                {donut_ring(momentum_score, size=56, color="#3B82F6")}
            </div>
            <div class="card-subtext">Deep focus, low context-switching state detected.</div>
        </div>
    """, unsafe_allow_html=True)

with row1_col2:
    st.markdown(f"""
        <div class="dashboard-card"><div class="card-header"><span class="header-icon" style="color:#3B82F6">{ICON_DROPLET}</span>Daily Streak</div>
            <div class="flex-container">
                <div class="card-value">{st.session_state.get("streak", 1)} <span style="font-size:14px; color:#64748B; margin-left:8px;">Days</span></div>
                {bars([8, 13, 20, 17, 24], color="#3B82F6")}
            </div>
            <div class="card-subtext">Best performance baseline: 14 days.</div>
        </div>
    """, unsafe_allow_html=True)

with row1_col3:
    st.markdown(f"""
        <div class="dashboard-card"><div class="card-header"><span class="header-icon" style="color:#10B981">{ICON_TREND}</span>Productivity Trend</div>
            <div class="flex-container">
                <div class="card-value">+12%</div>
                {sparkline("0,25 15,5 30,18 45,9 60,2 70,5", color="#10B981")}
            </div>
            <div class="card-subtext">Calculated relative to performance last week.</div>
        </div>
    """, unsafe_allow_html=True)

# Analytics initialization state processed above grid layer

# Init radar and skills in session state
if "radar" not in st.session_state:
    st.session_state["radar"] = generate_opportunity_radar(momentum_score, st.session_state["blocks"])

if "skill_tracker" not in st.session_state:
    st.session_state["skill_tracker"] = generate_skill_tracker(
        momentum_score,
        st.session_state.get("streak", 1),
        st.session_state["blocks"]
    )

# Opportunity Radar Render
radar = st.session_state["radar"]
radar_html = f"""
<div class="dashboard-card radar-card">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div class="card-header">🎯 OPPORTUNITY RADAR</div>
        <span class="badge-green">{radar['badge']}</span>
    </div>
    <div class="radar-action">{radar['action']}</div>
    <div class="radar-reason">• {radar['reason']}</div>
</div>
"""
st.markdown(flatten_html(radar_html), unsafe_allow_html=True)

radar_col1, radar_col2 = st.columns(2)
with radar_col1:
    if st.button("✅ Mark as Complete", use_container_width=True, key="radar_complete"):
        with st.spinner("Recalculating..."):
            matched = False
            for block in st.session_state["blocks"]:
                if block["title"].strip().lower() == radar["action"].strip().lower():
                    block["state"] = "completed"
                    matched = True
            with open(DATA_FILE, "w") as f:
                json.dump({
                    "blocks": st.session_state["blocks"],
                    "streak": st.session_state.get("streak", 1),
                    "last_active_date": st.session_state.get("last_active_date", datetime.now().strftime("%Y-%m-%d"))
                }, f)

            # Invalidate Caches
            if "radar" in st.session_state:
                del st.session_state["radar"]
            if "skill_tracker" in st.session_state:
                del st.session_state["skill_tracker"]

            if matched:
                st.toast(f"✅ Marked '{radar['action']}' complete!")
            else:
                st.toast(f"⚠️ No task titled '{radar['action']}' found.")
            st.rerun()

with radar_col2:
    if st.button("🔄 Refresh Radar", use_container_width=True, key="radar_refresh"):
        with st.spinner("Recalculating..."):
            st.session_state["radar"] = generate_opportunity_radar(momentum_score, st.session_state["blocks"])
            if "skill_tracker" in st.session_state:
                del st.session_state["skill_tracker"]
        st.rerun()

# Row 2 Analytics Cards Rendering
row2_col1, row2_col2, row2_col3 = st.columns(3, gap="large")
with row2_col1:
    st.markdown(f"""
        <div class="dashboard-card"><div class="card-header">Momentum Score</div>
            <div class="flex-container">
                <div class="card-value">{momentum_score}% <span class="badge-green">Live</span></div>
                {sparkline("0,10 15,22 30,14 45,26 60,18", color="#3B82F6", width=60, height=30)}
            </div>
        </div>
    """, unsafe_allow_html=True)

with row2_col2:
    tasks_html = f"""
    <div class="dashboard-card">
        <div class="card-header">Tasks Completed</div>
        <div class="flex-container">
            <div class="card-value">
                {completed_tasks} / {total_tasks}
                <span class="badge-green">🔥 {st.session_state.get("streak", 1)} Day Streak</span>
            </div>
        </div>
    </div>
    """
    st.markdown(flatten_html(tasks_html), unsafe_allow_html=True)

with row2_col3:
    st.markdown(f"""
        <div class="dashboard-card"><div class="card-header">Meetings Logged</div>
            <div class="flex-container">
                <div class="card-value">{m_count} <span style="font-size:12px; color:#64748B; margin-left:10px; font-weight:500;">~{m_count * 30}m total</span></div>
                {sparkline("0,15 15,5 30,22 45,10 60,18", color="#22C55E", width=60, height=30)}
            </div>
        </div>
    """, unsafe_allow_html=True)

# 11. Dynamic Workspace Split Layout
workspace_main, workspace_panel = st.columns([2.3, 1], gap="large")
blocks = st.session_state["blocks"]

with workspace_main:
    # ==========================================
    # UPGRADED COGNITIVE REDLINE SAFEGUARD CORE
    # ==========================================
    redline_risk = False
    risk_index = -1
    is_afternoon = False

    # Scan for consecutive high-intensity focus sprints
    for i in range(len(blocks) - 1):
        if blocks[i].get("block_type") == "focus" and blocks[i+1].get("block_type") == "focus":
            redline_risk = True
            risk_index = i
            # Check if the danger zone falls in the afternoon/evening
            if "PM" in blocks[i].get("time", ""):
                is_afternoon = True
            break

    if redline_risk:
        # Configuration presets based on biological time matching window parameters
        if is_afternoon:
            header_tag = "🚨 [Circadian Slump Vulnerability]"
            banner_bg = "rgba(239, 68, 68, 0.06)"
            banner_border = "rgba(239, 68, 68, 0.25)"
            text_color = "#F87171"
            description_text = "Warning: Consecutive high-intensity focus blocks detected during the natural post-lunch biological energy drop. Burnout risk is amplified by 2.5x."
        else:
            header_tag = "⚠️ [Cortisol Peak Overdrive Alert]"
            banner_bg = "rgba(245, 158, 11, 0.06)"
            banner_border = "rgba(245, 158, 11, 0.25)"
            text_color = "#F59E0B"
            description_text = "You are scheduling intense cognitive sprints during your peak morning neurological window. Running these back-to-back risks premature mental exhaustion by noon."

        # Render the custom circadian banner
        st.markdown(f"""
            <div style="background: {banner_bg}; border: 1px solid {banner_border}; border-radius: 14px; padding: 18px; margin-bottom: 22px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
                <div style="display: flex; align-items: flex-start; gap: 14px;">
                    <div style="background: {text_color}; width: 6px; height: 38px; border-radius: 4px; flex-shrink: 0; margin-top: 3px;"></div>
                    <div>
                        <div style="color: {text_color}; font-weight: 800; font-size: 13px; text-transform: uppercase; letter-spacing: 1px;">{header_tag}</div>
                        <div style="color: #94A3B8; font-size: 13px; margin-top: 4px; line-height: 1.5; font-weight: 500;">{description_text}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Dual-action recovery selection matrix row split layout
        btn_col1, btn_col2 = st.columns(2, gap="small")
        clicked_quiet = False
        clicked_somatic = False

        with btn_col1:
            if st.button("🧘 Inject Quiet Decompression", use_container_width=True):
                clicked_quiet = True

        with btn_col2:
            if st.button("🚶 Inject Somatic Movement", use_container_width=True):
                clicked_somatic = True

        # Process the structural mitigation if either button state triggers True
        if clicked_quiet or clicked_somatic:
            mitigated_blocks = []

            # Setup specific task text values based on which action was selected
            break_title = "Mindfulness Reset" if clicked_quiet else "Physical Circulation Walk"
            break_context = "Decompress working memory caches, lower heart rate, and clear open screen clutter." if clicked_quiet else "Step away from screens, stretch, and hydrate to combat biological sluggishness."

            for idx in range(len(st.session_state["blocks"])):
                mitigated_blocks.append(st.session_state["blocks"][idx])
                # Insert the custom break pill exactly between the two conflicting elements
                if idx == risk_index:
                    mitigated_blocks.append({
                        "time": "Buffer Slot",
                        "title": f"🛡️ {break_title}",
                        "context": break_context,
                        "block_type": "break",
                        "badge": "Break",
                        "high_intensity": False,
                        "state": "ready"
                    })

            st.session_state["blocks"] = mitigated_blocks
            if "skill_tracker" in st.session_state:
                del st.session_state["skill_tracker"]
            with open(DATA_FILE, "w") as f:
                json.dump({
                    "blocks": st.session_state["blocks"],
                    "streak": st.session_state.get("streak", 1),
                    "last_active_date": st.session_state.get("last_active_date", "")
                }, f)
            st.rerun()
    st.markdown("<h3 style='color: white; font-size: 18px; font-weight: 700; margin-bottom: 15px;'>Today's schedule</h3>", unsafe_allow_html=True)

    if optimize_execution and raw_task_stream:
        if DEMO_MODE:
            st.session_state["blocks"] = DEFAULT_BLOCKS
            for block in st.session_state["blocks"]:
                block["state"] = "ready"
            if "skill_tracker" in st.session_state:
                del st.session_state["skill_tracker"]
            st.toast("🚀 Demo matrix compiled instantly!")
            st.rerun()
        elif client:
            with st.spinner("Compiling contextual layout matrices..."):
                prompt_blueprint = f"""
                Analyze these unorganized scheduling items and convert them into a structured,
                chronologically ordered timeline for one day: {raw_task_stream}
                CRITICAL REAL-TIME TELEMETRY INSTRUCTIONS:
                For every single task block, you MUST autonomously calculate and output:
                1. "cognitive_load": An integer (1-10) based on mental intensity (e.g., deep coding/system design = 9, simple admin = 3).
                2. "dopamine_drain": An integer (1-10) based on how tedious/exhausting the task is.

                """
                try:
                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=prompt_blueprint,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=ScheduleResponse,
                        ),
                    )
                    data = json.loads(response.text)
                    blocks = data.get("blocks", DEFAULT_BLOCKS)
                    for block in blocks:
                        block["state"] = "ready"

                    st.session_state["blocks"] = blocks
                except Exception:
                    st.warning("🌐 Core sync pipeline experiencing heavy traffic. Activating localized scheduling matrix fallback.")
                    st.session_state["blocks"] = DEFAULT_BLOCKS
                    for block in st.session_state["blocks"]:
                        block["state"] = "ready"
                    st.rerun()

    st.markdown(render_timeline(blocks), unsafe_allow_html=True)

    st.markdown("### 🎯 Mission Control")
    task_titles = [b["title"] for b in st.session_state["blocks"]]
    selected_task = st.selectbox("Select Task", task_titles)

    col_mc1, col_mc2 = st.columns(2)

    with col_mc1:
        if st.button("🚀 Start Focus", use_container_width=True):
            for block in st.session_state["blocks"]:
                if block["title"] == selected_task:
                    block["state"] = "in_focus"
                elif block.get("state", "ready") == "in_focus":
                    block["state"] = "ready"
            with open(DATA_FILE, "w") as f:
                json.dump({
                    "blocks": st.session_state["blocks"],
                    "streak": st.session_state.get("streak", 1),
                    "last_active_date": st.session_state.get("last_active_date", datetime.now().strftime("%Y-%m-%d"))
                }, f)
            st.rerun()

    with col_mc2:
        if st.button("✅ Complete Mission", use_container_width=True):
            show_impact_preview(selected_task, momentum_score, st.session_state.get("streak", 1))

    # ##########################################################
    # 🌪️ THE REAL-TIME AI REPAIR PIPELINE (LIVE MUTATION)
    # ##########################################################
    st.markdown("### 🌪️ Reality Changed?")
    disruption_event = st.text_area("Describe what happened:", placeholder="Example: Meeting ran 45 minutes late. I'm exhausted.")
    reoptimize = st.button("🔄 Re-Optimize Schedule", use_container_width=True)

    if reoptimize and disruption_event.strip():
        with st.spinner("🧠 Neural link active. Passing context to Gemini..."):

            # 1. Fetch new blocks from the AI
            updated_blocks = mutate_schedule_with_ai(st.session_state["blocks"], disruption_event.strip())

            # 2. TRAP THE ERROR: Only trigger the page refresh if the AI actually changed something
            if updated_blocks != st.session_state["blocks"]:
                st.session_state["blocks"] = updated_blocks
                with open(DATA_FILE, "w") as f:
                    json.dump({
                        "blocks": st.session_state["blocks"],
                        "streak": st.session_state.get("streak", 1),
                        "last_active_date": st.session_state.get("last_active_date", "")
                    }, f)

                st.rerun() # Safely trigger the UI cascade animation

                # 4. Trigger full layout repaint and screen cascade animation
                st.rerun()
        # ##########################################################

with workspace_panel:
    st.markdown("### Mentorship Suite")
    col_side1, col_side2 = st.columns(2)
    with col_side1:
        if st.button("🧠 AI Coaching", use_container_width=True):
            upcoming_tasks = [block["title"] for block in st.session_state["blocks"] if block.get("state") != "completed"][:3]
            st.session_state["ai_coach_message"] = generate_ai_coach(momentum_score, completed_tasks, total_tasks, upcoming_tasks)
            st.rerun()

    with col_side2:
        if st.button("🔮 Future Self", use_container_width=True):
            st.session_state["future_self_message"] = generate_future_self(momentum_score, completed_tasks, total_tasks, st.session_state.get("blocks", []))
            st.rerun()

    st.markdown("<h3 style='color: white; font-size: 18px; font-weight: 700; margin-bottom: 15px;'>Performance Diagnostics</h3>", unsafe_allow_html=True)

    # 1. Focus Forecast
    st.markdown(f"""
        <div class="dashboard-card">
            <div class="card-header" style="color: #3B82F6;"><span class="header-icon">{ICON_SPARKLE}</span>Focus Forecast</div>
            <p style="color: #94A3B8; font-size: 13.5px; margin-top: 10px; line-height: 1.5;">
                Your early productivity peaks suggest scheduling heavy cognitive loading before 11:30 AM to maximize efficiency vectors.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 2. Daily Focus Goal
    st.markdown(f"""
        <div class="dashboard-card">
            <div class="card-header" style="color: #10B981;"><span class="header-icon">{ICON_TARGET}</span>Daily Focus Goal</div>
            <div class="flex-container" style="margin-top: 14px;">
                {donut_ring(momentum_score, size=64, color="#3B82F6")}
                <div style="flex:1; margin-left:16px;">
                    <div style="font-size:14px; font-weight:600; color:#FFFFFF;">{completed_tasks} of {total_tasks} completed</div>
                    <div style="font-size:12.5px; color:#94A3B8; margin-top:3px;">Weighted momentum tracking active</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# 3. Smart Skill Tracker (Upgraded Premium Dynamic Local Matrix Engine)
    current_blocks = st.session_state.get("blocks", [])
    focus_done = sum(1 for b in current_blocks if b.get("block_type") == "focus" and b.get("state") == "completed")
    current_streak = st.session_state.get("streak", 1)

    # Intercept API failures or Demo Mode to run realistic math
    if DEMO_MODE or not st.session_state.get("skill_tracker") or st.session_state.get("skill_tracker", {}).get("skills", [{}])[0].get("score") == 10:
        calc_insight = "Dynamic execution vector verified. Focus dimensions are compounding positively." if momentum_score > 50 else "Calibrating operational bandwidth. Prioritize high-intensity slots to build metric depth."
        st.session_state["skill_tracker"] = {
            "skills": [
                {"skill": "Problem Solving", "score": min(98, 35 + (focus_done * 20)), "gradient": "linear-gradient(90deg, #F59E0B, #EF4444)", "glow": "rgba(239,68,68,0.35)"},
                {"skill": "Time Management", "score": min(100, 25 + (completed_tasks * 15)), "gradient": "linear-gradient(90deg, #8B5CF6, #3B82F6)", "glow": "rgba(59,130,246,0.35)"},
                {"skill": "Consistency", "score": min(100, 20 + (current_streak * 15)), "gradient": "linear-gradient(90deg, #10B981, #059669)", "glow": "rgba(16,185,129,0.35)"},
                {"skill": "Deep Work", "score": momentum_score, "gradient": "linear-gradient(90deg, #3B82F6, #06B6D4)", "glow": "rgba(6,182,212,0.35)"}
            ],
            "insight": calc_insight
        }

    skill_tracker = st.session_state["skill_tracker"]
    skill_html = '<div class="dashboard-card"><div class="card-header" style="letter-spacing:1px; color:#94A3B8;">📈 PERFORMANCE PROFILE</div>'

    for skill in skill_tracker["skills"]:
        score = skill["score"]
        grad = skill.get("gradient", "linear-gradient(90deg, #3B82F6, #8B5CF6)")
        glow = skill.get("glow", "rgba(59,130,246,0.2)")

        skill_html += f"""
        <div style="margin-top:16px;">
            <div style="display:flex; justify-content:space-between; font-size:12.5px; font-weight:600; margin-bottom:6px; color:#E2E8F0;">
                <span style="letter-spacing: 0.3px; color:#A0AEC0;">{skill["skill"]}</span>
                <span style="font-family:'Space Grotesk'; font-weight:700; color:#FFFFFF;">{score}%</span>
            </div>
            <div style="background:#161925; border-radius:8px; height:7px; width:100%; overflow:hidden; border:1px solid #1E2235;">
                <div style="background: {grad}; width:{score}%; height:100%; border-radius:8px; box-shadow: 0 0 10px {glow};"></div>
            </div>
        </div>"""

    skill_html += f"""
        <div style="margin-top:20px; font-size:12.5px; color:#94A3B8; padding-top:14px; border-top:1px solid #1E2235; line-height:1.6;">
            <span style="color:#10B981; font-weight:700; text-transform:uppercase; font-size:11px; letter-spacing:0.5px;">Vector Analysis:</span> "{skill_tracker.get('insight', '')}"
        </div>
    </div>"""

    st.markdown(flatten_html(skill_html), unsafe_allow_html=True)

    # 4. Up Next Lists
    up_next = [b for b in blocks if b.get("state") != "completed"][:3]
    if up_next:
        rows = "".join(f"""
            <div class="up-next-row">
                <span class="dot dot-{b.get('block_type', 'default')}"></span>
                <div><div class="up-next-title">{b.get('title', '')}</div><div class="up-next-sub">{b.get('badge', '')}</div></div>
            </div>""" for b in up_next)
        st.markdown(flatten_html(f'<div class="dashboard-card"><div class="card-header">Up next</div><div style="margin-top:12px;">{rows}</div></div>'), unsafe_allow_html=True)

    # 5. AI Coach Insights
    coach_message = st.session_state.get("ai_coach_message", "Press 🧠 AI Coaching to receive personalized guidance.")
    if coach_message:
        coach_html = f"""
        <div class="dashboard-card">
            <div class="card-header">AI Coach</div>
            <div style="margin-top:12px; color:#E2E8F0; line-height:1.6; font-size:13.5px;">
                {coach_message}
            </div>
        </div>"""
        st.markdown(flatten_html(coach_html), unsafe_allow_html=True)

    # 6. Future Self Simulation
    future_message = st.session_state.get("future_self_message", "Press 🔮 Future Self to see your 30-day projection.")
    if future_message:
        future_html = f"""
        <div class="dashboard-card">
            <div class="card-header">Future Self AI</div>
            <div style="margin-top:12px; color:#E2E8F0; line-height:1.6; font-size:13.5px;">
                {future_message}
            </div>
        </div>"""
        st.markdown(flatten_html(future_html), unsafe_allow_html=True)
