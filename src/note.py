import json
from typing import Any, Dict, List

from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

from .custom_field import Field
from .tipo_dado import TipoDado
from .secure_actions import SecureCopyAction


# Global clipboard timeout - will be set by extension
_clipboard_timeout = 15


def set_clipboard_timeout(timeout: int):
    """Set the global clipboard timeout for secure copy actions."""
    global _clipboard_timeout
    _clipboard_timeout = max(5, timeout)


class Note:
    def __init__(self, raw: Dict[str, Any] | str):
        self.tipo_dado = TipoDado.NOTA
        self.image = TipoDado.get_icon(self.tipo_dado)

        if isinstance(raw, str):
            raw = json.loads(raw)

        self.notes = raw.get("notes")

        # Campos personalizados do tipo texto
        self.fields: List[Field] = [
            Field(self.tipo_dado, f)
            for f in raw.get("fields", [])
            if f.get("type") == "text"
        ]

    def get_itens(self) -> List[ExtensionResultItem]:
        items: List[ExtensionResultItem] = []

        # Nota principal
        if self.notes:
            display_notes = self.notes[:30] + " [...]" if len(self.notes) > 30 else self.notes

            items.append(
                ExtensionResultItem(
                    icon=self.image,
                    name=f"NOTA:   {display_notes}",
                    on_enter=SecureCopyAction(self.notes, _clipboard_timeout),
                )
            )

        # Campos personalizados
        for field in self.fields:
            item = field.get_item()
            if item:
                items.append(item)

        return items
