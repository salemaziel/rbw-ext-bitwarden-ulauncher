import json
from typing import Dict, Any, List

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


class Card:
    def __init__(self, raw: Dict[str, Any]):
        self.tipo_dado = TipoDado.CARTAO
        self.image = TipoDado.get_icon(self.tipo_dado)

        if isinstance(raw, str):
            raw = json.loads(raw)

        data = raw.get("data", {})
        self.code = data.get("code")
        self.notes = raw.get("notes")
        self.number = data.get("number")
        self.exp_year = data.get("exp_year")
        self.exp_month = data.get("exp_month")
        self.name = data.get("cardholder_name")

        self.fields: List[Field] = [
            Field(self.tipo_dado, f)
            for f in raw.get("fields", [])
            if f.get("type") == "text"
        ]

    def get_itens(self) -> List[ExtensionResultItem]:
        items: List[ExtensionResultItem] = []

        # Nome impresso
        if self.name:
            items.append(ExtensionResultItem(
                icon=self.image,
                name=f"NOME IMPRESSO:   {self.name}",
                on_enter=SecureCopyAction(self.name, _clipboard_timeout)
            ))

        # Número do cartão
        if self.number:
            items.append(ExtensionResultItem(
                icon=self.image,
                name=f"NÚMERO CARTÃO:   {self.number}",
                on_enter=SecureCopyAction(self.number, _clipboard_timeout)
            ))

        # Data de expiração (MM/YY)
        month = self.exp_month.zfill(2) if self.exp_month else None
        year = self.exp_year.zfill(2) if self.exp_year else None

        if month and year:
            items.append(ExtensionResultItem(
                icon=self.image,
                name=f"MM/YY:   {month}/{year}",
                on_enter=SecureCopyAction(f"{month}/{year}", _clipboard_timeout)
            ))

        elif month:
            items.append(ExtensionResultItem(
                icon=self.image,
                name=f"MÊS:   {month}",
                on_enter=SecureCopyAction(month, _clipboard_timeout)
            ))

        elif year:
            items.append(ExtensionResultItem(
                icon=self.image,
                name=f"ANO:   {year}",
                on_enter=SecureCopyAction(year, _clipboard_timeout)
            ))

        # CVV
        if self.code:
            masked_cvv = "*" * len(self.code.zfill(3))
            items.append(ExtensionResultItem(
                icon=self.image,
                name=f"CVV:   {masked_cvv}",
                on_enter=SecureCopyAction(self.code.zfill(3), _clipboard_timeout)
            ))

        # Notas
        if self.notes:
            display_notes = self.notes[:30] + " [...]" if len(self.notes) > 30 else self.notes
            items.append(ExtensionResultItem(
                icon=self.image,
                name=f"NOTA:   {display_notes}",
                on_enter=SecureCopyAction(self.notes, _clipboard_timeout)
            ))

        # Campos personalizados
        for field in self.fields:
            item = field.get_item()
            if item:
                items.append(item)

        return items
