import re
import json
from typing import Dict, Any, List

from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

from .tipo_dado import TipoDado
from .custom_field import Field
from .secure_actions import SecureCopyAction


# Global clipboard timeout - will be set by extension
_clipboard_timeout = 15


def set_clipboard_timeout(timeout: int):
    """Set the global clipboard timeout for secure copy actions."""
    global _clipboard_timeout
    _clipboard_timeout = max(5, timeout)


class Identity:
    def __init__(self, raw: Dict[str, Any]):
        self.tipo_dado = TipoDado.IDENTIDADE
        self.image = TipoDado.get_icon(self.tipo_dado)

        if isinstance(raw, str):
            raw = json.loads(raw)

        data = raw.get("data", {})

        self.title = data.get("title", "") or ""
        self.first_name = data.get("first_name", "") or ""
        self.middle_name = data.get("middle_name", "") or ""
        self.last_name = data.get("last_name", "") or ""

        self.full_name = self._join_fields(
            self.title,
            self.first_name,
            self.middle_name,
            self.last_name
        )

        self.address = self._join_fields(
            data.get("address1"),
            data.get("address2"),
            data.get("address3"),
            sep=", "
        )

        self.city_state = self._join_fields(
            data.get("city"),
            data.get("state"),
            sep="/"
        )

        self.postal_code = data.get("postal_code", "") or ""
        self.phone = data.get("phone", "") or ""
        self.email = data.get("email", "") or ""
        self.doc = data.get("ssn", "") or ""
        self.license_number = data.get("license_number", "") or ""
        self.passport_number = data.get("passport_number", "") or ""
        self.username = data.get("username", "") or ""
        self.notes = raw.get("notes", "") or ""

        self.fields: List[Field] = [
            Field(self.tipo_dado, f)
            for f in raw.get("fields", [])
            if f.get("type") == "text"
        ]

    @staticmethod
    def is_not_blank(value):
        return value is not None and str(value).strip().lower() not in ["", "null"]

    def _join_fields(self, *fields, sep=" "):
        return sep.join(
            str(f).strip() for f in fields if self.is_not_blank(f)
        )

    def get_itens(self) -> List[ExtensionResultItem]:
        items = []

        def add_item(label: str, content: str, mask: bool = False):
            if not self.is_not_blank(content):
                return

            display_value = content
            if mask:
                cleaned = re.sub(r'\D', '', content).zfill(12)
                masked = f'XXX.{cleaned[2:5]}.XXX-{cleaned[-2:]}'
                display_value = masked
                clipboard_value = cleaned
            else:
                clipboard_value = content

            items.append(ExtensionResultItem(
                icon=self.image,
                name=f"{label.upper()}:   {display_value}",
                on_enter=SecureCopyAction(clipboard_value, _clipboard_timeout)
            ))

        # 1. Nome completo
        add_item("Nome completo", self.full_name)

        # 2. Documento
        add_item("Documento", self.doc, mask=True)

        # 3. Passaporte
        add_item("Passaporte", self.passport_number)

        # 4. Licença
        add_item("Licença", self.license_number)

        # 5. Usuário
        add_item("Usuário", self.username)

        # 6. Telefone
        add_item("Telefone", self.phone)

        # 7. Email
        add_item("Email", self.email)

        # 8. CAMPOS PERSONALIZADOS (fields) — ANTES do endereço
        for f in self.fields:
            item = f.get_item()
            if item:
                items.append(item)

        # 9. Endereço
        add_item("Endereço", self.address)

        # 10. Cidade/Estado
        add_item("Cidade/Estado", self.city_state)

        # 11. CEP
        add_item("CEP", self.postal_code)

        # 12. Notas
        if self.is_not_blank(self.notes):
            display_notes = self.notes[:30] + ' [...]' if len(self.notes) > 30 else self.notes
            items.append(ExtensionResultItem(
                icon=self.image,
                name=f'NOTAS:   {display_notes}',
                on_enter=SecureCopyAction(self.notes, _clipboard_timeout)
            ))

        return items

