from pathlib import Path
import re

from app.models.attendee import Attendee
from app.models.field_mapping import FieldMapping
from app.models.template import CertificateTemplate

try:
    import fitz
except ImportError:  # pragma: no cover - dependency is declared for runtime use.
    fitz = None

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
except ImportError:  # pragma: no cover - optional fallback if dependencies are not installed yet.
    arabic_reshaper = None
    get_display = None


TEXT_FIELD_VALUES = {
    "attendee_name": lambda attendee, defaults: attendee.full_name or "",
    "workshop_title": lambda attendee, defaults: attendee.workshop_title or defaults.get("workshop_title", ""),
    "certificate_date": lambda attendee, defaults: attendee.certificate_date or defaults.get("certificate_date", ""),
}

ARABIC_RE = re.compile(r"[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff]")
FONT_FILE_CANDIDATES = {
    "arial": [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ],
    "tahoma": [
        Path("C:/Windows/Fonts/tahoma.ttf"),
        Path("/usr/share/fonts/truetype/msttcorefonts/Tahoma.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ],
    "segoe_ui": [
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ],
    "dejavu_sans": [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ],
}
BUILT_IN_FONTS = {"helv", "cour", "tiro", "times", "courier", "helvetica"}
ARABIC_FALLBACK_ORDER = ("tahoma", "arial", "segoe_ui", "dejavu_sans")


class CertificateRenderer:
    def render(
        self,
        template: CertificateTemplate,
        attendee: Attendee,
        mappings: list[FieldMapping],
        template_path: Path,
        output_path: Path,
        default_values: dict[str, str] | None = None,
    ) -> None:
        if fitz is None:
            raise RuntimeError("PyMuPDF is required for certificate rendering.")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        document = self._create_base_document(template, template_path)
        page = document[0]

        for mapping in mappings:
            if not mapping.visible or mapping.field_key not in TEXT_FIELD_VALUES:
                continue
            value = TEXT_FIELD_VALUES[mapping.field_key](attendee, default_values or {})
            if value:
                self._draw_text(page, mapping, value)

        document.save(output_path)
        document.close()

    def _create_base_document(self, template: CertificateTemplate, template_path: Path):
        if template.file_type == "pdf":
            source = fitz.open(template_path)
            document = fitz.open()
            document.insert_pdf(source, from_page=0, to_page=0)
            source.close()
            return document

        width = template.page_width or 1000
        height = template.page_height or 700
        document = fitz.open()
        page = document.new_page(width=width, height=height)
        page.insert_image(fitz.Rect(0, 0, width, height), filename=str(template_path))
        return document

    def _draw_text(self, page, mapping: FieldMapping, value: str) -> None:
        rect = fitz.Rect(mapping.x, mapping.y, mapping.x + mapping.width, mapping.y + mapping.height)
        color = self._hex_to_rgb(mapping.font_color or "#111827")
        alignments = {"left": fitz.TEXT_ALIGN_LEFT, "center": fitz.TEXT_ALIGN_CENTER, "right": fitz.TEXT_ALIGN_RIGHT}
        rendered_value = self._prepare_text_for_rendering(value)
        font_name, font_file = self._resolve_font(mapping.font_family, self._contains_arabic(value))
        font_args = {"fontname": font_name}
        if font_file is not None:
            font_args["fontfile"] = str(font_file)

        page.insert_textbox(
            rect,
            rendered_value,
            fontsize=mapping.font_size or 36,
            color=color,
            align=alignments.get(mapping.alignment or "center", fitz.TEXT_ALIGN_CENTER),
            **font_args,
        )

    def _prepare_text_for_rendering(self, value: str) -> str:
        if self._contains_arabic(value) and arabic_reshaper is not None and get_display is not None:
            return get_display(arabic_reshaper.reshape(value))
        return value

    def _contains_arabic(self, value: str) -> bool:
        return ARABIC_RE.search(value) is not None

    def _resolve_font(self, requested_font: str | None, contains_arabic: bool) -> tuple[str, Path | None]:
        normalized = (requested_font or "helv").lower().replace(" ", "_").replace("-", "_")

        if normalized in FONT_FILE_CANDIDATES:
            font_file = self._first_existing_font(FONT_FILE_CANDIDATES[normalized])
            if font_file is not None:
                return normalized, font_file

        if contains_arabic:
            for fallback in ARABIC_FALLBACK_ORDER:
                font_file = self._first_existing_font(FONT_FILE_CANDIDATES[fallback])
                if font_file is not None:
                    return fallback, font_file

        if normalized in {"times", "times_roman"}:
            return "tiro", None
        if normalized in {"courier", "courier_new"}:
            return "cour", None
        if normalized in BUILT_IN_FONTS:
            return normalized, None
        return "helv", None

    def _first_existing_font(self, candidates: list[Path]) -> Path | None:
        return next((path for path in candidates if path.exists()), None)

    def _hex_to_rgb(self, color: str) -> tuple[float, float, float]:
        normalized = color.lstrip("#")
        if len(normalized) != 6:
            normalized = "111827"
        return tuple(int(normalized[index : index + 2], 16) / 255 for index in (0, 2, 4))
