import re
import pdfplumber
from .models import EvaluationRecord, german_float


def parse_pdf(filepath: str, lecturer_name: str, semester: str, is_wpf: bool) -> EvaluationRecord:
    """Parse a single evaluation PDF and return an EvaluationRecord."""
    filename = filepath.rsplit('/', 1)[-1] if '/' in filepath else filepath

    record = EvaluationRecord(
        pdf_filename=filename,
        pdf_path=filepath,
        lecturer_name=lecturer_name,
        semester=semester,
        is_wpf=is_wpf,
    )

    with pdfplumber.open(filepath) as pdf:
        page1_text = pdf.pages[0].extract_text() or ''
        full_text = '\n'.join(
            (p.extract_text() or '') for p in pdf.pages
        )

    _parse_header(page1_text, record)
    _parse_global_ratings(page1_text, record)
    _parse_free_text(full_text, record)

    return record


def _parse_header(text: str, record: EvaluationRecord):
    """Extract course title, response count and rate from page 1 header."""
    lines = text.split('\n')

    # Line 2 is typically the course title
    if len(lines) >= 2:
        record.course_title = lines[1].strip()

    # Look for "erfasste Fragebögen = N" and "Rücklaufquote = X Prozent"
    m = re.search(r'erfasste\s+Frageb[öo]gen\s*=\s*(\d+)', text)
    if m:
        record.num_responses = int(m.group(1))

    m = re.search(r'R[üu]cklaufquote\s*=\s*([\d,\.]+)\s*Prozent', text)
    if m:
        record.response_rate = german_float(m.group(1))


def _find_section(text: str, keyword: str) -> int:
    """Find a section in text, handling doubled-character evasys headers.

    evasys PDFs render bold headers with doubled chars, e.g.:
      'Globalwerte' -> 'GGlloobbaallwweerrttee'
      'offenen Fragen' -> 'ooffffeenneenn FFrraaggeenn'
    """
    idx = text.find(keyword)
    if idx != -1:
        return idx
    # Build doubled version
    doubled = ''.join(c + c for c in keyword)
    idx = text.find(doubled)
    if idx != -1:
        return idx
    return -1


def _parse_global_ratings(text: str, record: EvaluationRecord):
    """Extract LR01-LR07 mean values from the Globalwerte section on page 1.

    The text contains patterns like:
      LR01 ... mw=4,9
      LR07 ... mw=5
    """
    # Find the Globalwerte section (ends at the next major section)
    start = _find_section(text, 'Globalwerte')
    end = _find_section(text, 'Auswertungsteil')
    if start == -1:
        return

    section = text[start:end] if end != -1 else text[start:]

    # Find all LR labels and mw values, then match them positionally
    lr_positions = [(m.start(), m.group(1)) for m in re.finditer(r'LR(0[1-7])', section)]
    mw_positions = [(m.start(), m.group(1)) for m in re.finditer(r'mw=([\d]+[,.]?[\d]*)', section)]

    for lr_pos, lr_num in lr_positions:
        for mw_pos, mw_val in mw_positions:
            if mw_pos > lr_pos:
                value = german_float(mw_val)
                setattr(record, f'lr{lr_num}', value)
                break


# Patterns for the three open-ended questions
_Q_METHODS = 'Durch welche Lehrmethoden'
_Q_POSITIVE = 'Was hat Ihnen an dieser Veranstaltung besonders gut gefallen'
_Q_IMPROVE = 'Was hätten Sie sich anders gewünscht'
# Fallback without umlaut (some PDFs may have different encoding)
_Q_IMPROVE_ALT = 'Was haetten Sie sich anders'


def _parse_free_text(text: str, record: EvaluationRecord):
    """Extract free-text responses from the 'Auswertungsteil der offenen Fragen' section."""
    # Find the open questions section - try both normal and doubled versions
    # Use rfind/last occurrence to skip table-of-contents mentions
    marker_normal = 'offenen Fragen'
    marker_doubled = 'ooffffeenneenn FFrraaggeenn'

    start = text.rfind(marker_doubled)
    marker_len = len(marker_doubled)
    if start == -1:
        start = text.rfind(marker_normal)
        marker_len = len(marker_normal)
    if start == -1:
        return

    section = text[start + marker_len:]

    # Find positions of each question
    positions = []
    for label, attr in [
        (_Q_METHODS, 'motivating_methods'),
        (_Q_POSITIVE, 'positive_feedback'),
        (_Q_IMPROVE, 'improvement_suggestions'),
    ]:
        idx = section.find(label)
        if idx == -1 and label == _Q_IMPROVE:
            idx = section.find(_Q_IMPROVE_ALT)
        if idx != -1:
            positions.append((idx, attr, label))

    positions.sort(key=lambda x: x[0])

    # Extract text between each question and the next (or end of section)
    for i, (pos, attr, label) in enumerate(positions):
        # Start after the question text (find end of question line)
        q_start = section.find('\n', pos)
        if q_start == -1:
            continue
        q_start += 1

        # End at the next section header or end
        if i + 1 < len(positions):
            q_end = positions[i + 1][0]
        else:
            q_end = len(section)

        block = section[q_start:q_end].strip()

        # Remove evasys footer lines
        block = re.sub(r'\d{2}\.\d{2}\.\d{4}\s+evasys.*', '', block)
        # Remove doubled-char section headers (e.g. GGeessaammtteeiinnsscchhäättzzuunngg)
        # These have every letter doubled, so detect with pattern: two identical chars repeated
        block = re.sub(r'^((.)\2)+\s*$', '', block, flags=re.MULTILINE)
        # Also remove header lines like "LLeehhrrmmeetthhooddeenn uunndd LLeerrnnmmaatteerriiaalliieenn"
        block = re.sub(r'^([A-ZÄÖÜa-zäöüß])\1([A-ZÄÖÜa-zäöüß])\2.*$', '', block, flags=re.MULTILINE)

        responses = _split_responses(block)
        setattr(record, attr, responses)


def _split_responses(block: str) -> list[str]:
    """Split a free-text block into individual student responses.

    Each student response starts on a new line. Multi-line responses
    have continuation lines that start with a lowercase letter
    (indicating a PDF line wrap mid-sentence).
    """
    lines = block.strip().split('\n')
    responses = []
    current = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current:
                responses.append(' '.join(current))
                current = []
            continue

        # A line starting with lowercase is a continuation of the previous response
        # (German nouns are capitalized, so lowercase start reliably indicates
        # a wrapped line rather than a new response)
        if current and stripped[0].islower():
            current.append(stripped)
        else:
            if current:
                responses.append(' '.join(current))
            current = [stripped]

    if current:
        responses.append(' '.join(current))

    # Filter out noise (very short artifacts, stray punctuation)
    responses = [r for r in responses if len(r) > 2]
    return responses
