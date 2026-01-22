import streamlit as st
import json
from pathlib import Path

# File path for persisting conversations
DATA_DIR = Path(__file__).parent.parent / "data"
CONVERSATIONS_FILE = DATA_DIR / "conversations.json"
SETTINGS_FILE = DATA_DIR / "settings.json"


def _ensure_data_dir():
    """Ensure the data directory exists."""
    DATA_DIR.mkdir(exist_ok=True)


def load_conversations() -> dict:
    """Load conversations from file."""
    _ensure_data_dir()
    if CONVERSATIONS_FILE.exists():
        try:
            with open(CONVERSATIONS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def load_settings() -> dict:
    """Load settings from file."""
    _ensure_data_dir()
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_settings(settings: dict):
    """Save settings to file."""
    _ensure_data_dir()
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except IOError as e:
        print(f"Error saving settings: {e}")


def save_conversations():
    """Save conversations to file."""
    _ensure_data_dir()
    try:
        # Save serializable parts (messages, stock_data, and competitor_analysis)
        data = {}
        for symbol, conv in st.session_state.stock_conversations.items():
            data[symbol] = {
                "messages": conv.get("messages", []),
                "stock_data": conv.get("stock_data"),
                "competitor_analysis": conv.get("competitor_analysis")
            }
        with open(CONVERSATIONS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"Error saving conversations: {e}")


def clear_conversations():
    """Clear all persisted conversations."""
    if CONVERSATIONS_FILE.exists():
        CONVERSATIONS_FILE.unlink()


def clear_settings():
    """Clear all persisted settings."""
    if SETTINGS_FILE.exists():
        SETTINGS_FILE.unlink()
