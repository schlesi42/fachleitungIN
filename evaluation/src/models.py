from dataclasses import dataclass, field
import re


def german_float(s: str) -> float:
    """Convert German decimal format to float. '4,9' -> 4.9"""
    return float(s.replace(',', '.'))


def semester_sort_key(semester: str) -> int:
    """Convert semester string to sortable integer.
    WiSe2023 -> 20231, SoSe2024 -> 20240, WiSe2024 -> 20241, etc.
    """
    match = re.search(r'(\d{4})', semester)
    if not match:
        return 0
    year = int(match.group(1))
    is_winter = semester.startswith('WiSe')
    return year * 2 + (1 if is_winter else 0)


SEMESTER_ORDER = ['WiSe2023', 'SoSe2024', 'WiSe2024', 'SoSe2025', 'WiSe2025']


@dataclass
class EvaluationRecord:
    """One evaluation PDF = one record."""
    pdf_filename: str
    pdf_path: str

    # Metadata from filename + folder
    lecturer_name: str
    semester: str
    is_wpf: bool

    # Metadata from PDF header
    course_title: str = ''
    num_responses: int = 0
    response_rate: float = 0.0

    # Global ratings LR01-LR07 (mean values, scale 1-6)
    lr01: float | None = None
    lr02: float | None = None
    lr03: float | None = None
    lr04: float | None = None
    lr05: float | None = None
    lr06: float | None = None
    lr07: float | None = None

    # Free-text responses
    motivating_methods: list[str] = field(default_factory=list)
    positive_feedback: list[str] = field(default_factory=list)
    improvement_suggestions: list[str] = field(default_factory=list)
