# bot_control.py
import threading


# Global control flags
stop_event = threading.Event()
paused_event = threading.Event()

def pause_bot():
    """Pauses the bot"""
    paused_event.set()
    return {"status": "Bot paused"}

def unpause_bot():
    """Unpauses the bot"""
    paused_event.clear()
    return {"status": "Bot resumed"}

def stop_bot():
    """Stops the bot completely"""
    stop_event.set()
    return {"status": "Bot stopped"}

