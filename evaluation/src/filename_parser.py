import os
import re


def extract_semester_from_path(filepath: str) -> str:
    """Extract semester identifier from the folder path.

    The data directory structure uses folders like:
      '95 WiSe2025_5.Sem.23_3.Sem.24_1.Sem.25'
      '99 WiSe2023_5.Sem21_3.Sem.22_1.Sem.23'
    """
    parts = filepath.replace('\\', '/').split('/')
    for part in parts:
        match = re.search(r'((?:WiSe|SoSe)\d{4})', part)
        if match:
            return match.group(1)
    return 'Unknown'


def is_bunte_liste(filename: str) -> bool:
    """Check if a file is a 'Bunte Liste' aggregate file (not an individual evaluation)."""
    return 'Bunte Liste' in filename or filename.startswith('FB2 ')


def is_wpf(filepath: str) -> bool:
    """Detect if the evaluation is for an elective (WPF) course."""
    parent_dir = os.path.basename(os.path.dirname(filepath))
    return parent_dir.startswith('WPF') or 'WPF' in parent_dir


def extract_lecturer_from_filename(filename: str) -> str | None:
    """Extract lecturer name from PDF filename.

    Naming patterns:
      'Schlesinger,Sebastian-BWL_IN-...'
      'von_Saucken,Anna-Maria-BWL_IN-...'
      'Wagner,Ralf_Fritz-BWL_IN-...'
      'von Saucken,Anna-Maria BWL-...' (space-delimited)
      'Loock-Wagner-BWL-...' (no first name, rare)

    Returns 'Nachname, Vorname' or None if unparseable.
    """
    basename = os.path.splitext(filename)[0]

    comma_pos = basename.find(',')
    if comma_pos == -1:
        # No comma -> try pattern like 'Loock-Wagner-BWL-...'
        match = re.match(r'^([A-Za-zÄÖÜäöüß_-]+?)[-\s]+(BWL|WPF)', basename)
        if match:
            return match.group(1).replace('_', ' ')
        return None

    last_name = basename[:comma_pos]

    rest = basename[comma_pos + 1:]

    # Find where the first name ends: a hyphen or space followed by BWL or WPF
    match = re.search(r'[-\s]+(BWL|WPF)', rest)
    if match:
        first_name = rest[:match.start()]
    else:
        first_name = rest

    last_name = last_name.replace('_', ' ')
    first_name = first_name.replace('_', ' ')

    return f'{last_name}, {first_name}'
