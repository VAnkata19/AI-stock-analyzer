import streamlit as st
import json
from pathlib import Path

# File path for persisting conversations
DATA_DIR = Path(__file__).parent.parent / "data"
CONVERSATIONS_FILE = DATA_DIR / "conversations.json"


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


def save_conversations():
    """Save conversations to file."""
    _ensure_data_dir()
    try:
        # Only save the serializable parts (messages and stock_data)
        data = {}
        for symbol, conv in st.session_state.stock_conversations.items():
            data[symbol] = {
                "messages": conv.get("messages", []),
                "stock_data": conv.get("stock_data")
            }
        with open(CONVERSATIONS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"Error saving conversations: {e}")


def clear_conversations():
    """Clear all persisted conversations."""
    if CONVERSATIONS_FILE.exists():
        CONVERSATIONS_FILE.unlink()
