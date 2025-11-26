from typing import Dict, Any, Optional

from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

from .tipo_dado import TipoDado
from .secure_actions import SecureCopyAction


# Global clipboard timeout - will be set by extension
_clipboard_timeout = 15


def set_clipboard_timeout(timeout: int):
    """Set the global clipboard timeout for secure copy actions."""
    global _clipboard_timeout
    _clipboard_timeout = max(5, timeout)


class Field:
    def __init__(self, tipo_dado: TipoDado, field_data: Dict[str, Any]):
        self.tipo_dado = tipo_dado
        self.name: str = field_data.get("name", "Campo")
        self.value: str = field_data.get("value", "")

    def get_item(self) -> Optional[ExtensionResultItem]:
        # Apenas retorna se houver valor
        if not self.value:
            return None

        display_value = self.value[:30] + " [...]" if len(self.value) > 30 else self.value

        return ExtensionResultItem(
            icon=TipoDado.get_icon(self.tipo_dado),
            name=f"{self.name.upper()}:   {display_value}",
            on_enter=SecureCopyAction(self.value, _clipboard_timeout)
        )
