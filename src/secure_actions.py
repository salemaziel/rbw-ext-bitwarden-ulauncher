"""
Secure clipboard actions with auto-clear functionality.
"""
import logging

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib

from ulauncher.api.shared.action.BaseAction import BaseAction

logger = logging.getLogger(__name__)


class SecureCopyAction(BaseAction):
    """
    Custom action that copies text to clipboard and clears it after a timeout.
    
    Args:
        text: The text to copy to clipboard
        clear_after: Seconds after which to clear the clipboard (min 5s for safety)
    """
    
    def __init__(self, text: str, clear_after: int = 15):
        self.text = text
        self.clear_after = max(5, clear_after)  # Minimum 5s safety

    def run(self):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(self.text, -1)
        clipboard.store()
        
        logger.debug(
            "Copied secret to clipboard (len=%d). Will clear in %ds",
            len(self.text),
            self.clear_after
        )
        
        # Store text reference for comparison when clearing
        text_to_clear = self.text
        
        def _clear():
            try:
                current = clipboard.wait_for_text() or ""
                if current == text_to_clear:
                    clipboard.set_text("", -1)
                    clipboard.store()
                    logger.debug("Cleared secret from clipboard")
                else:
                    logger.debug(
                        "Clipboard content changed, skipping clear"
                    )
            except Exception:
                logger.exception("Error clearing clipboard")
            return False  # Return False to stop the timeout from repeating
        
        GLib.timeout_add_seconds(self.clear_after, _clear)
