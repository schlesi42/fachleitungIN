import os
import csv
import json
from .models import EvaluationRecord, semester_sort_key
from .filename_parser import (
    extract_semester_from_path,
    extract_lecturer_from_filename,
    is_bunte_liste,
    is_wpf,
)
from .pdf_parser import parse_pdf


def run_pipeline(data_dir: str = 'data', output_dir: str = 'output'):
    """Main pipeline: discover PDFs -> parse -> store."""
    records: list[EvaluationRecord] = []
    errors: list[tuple[str, str]] = []

    for root, _dirs, files in os.walk(data_dir):
        semester = extract_semester_from_path(root)

        for f in sorted(files):
            if not f.endswith('.pdf'):
                continue
            if is_bunte_liste(f):
                continue

            filepath = os.path.join(root, f)
            lecturer = extract_lecturer_from_filename(f)
            if lecturer is None:
                errors.append((filepath, 'Could not extract lecturer name'))
                continue

            wpf = is_wpf(filepath)

            try:
                record = parse_pdf(filepath, lecturer, semester, wpf)
                records.append(record)
            except Exception as e:
                errors.append((filepath, str(e)))
                print(f'  ERROR: {f[:60]}... -> {e}')

    # Sort by semester then lecturer
    records.sort(key=lambda r: (semester_sort_key(r.semester), r.lecturer_name))

    os.makedirs(output_dir, exist_ok=True)
    _save_evaluations_csv(records, output_dir)
    _save_free_text_csv(records, output_dir)

    print(f'\nProcessed {len(records)} evaluations, {len(errors)} errors')
    if errors:
        print('Errors:')
        for path, msg in errors:
            print(f'  {path}: {msg}')

    return records, errors


def _save_evaluations_csv(records: list[EvaluationRecord], output_dir: str):
    path = os.path.join(output_dir, 'evaluations.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'lecturer_name', 'semester', 'semester_sort_key', 'is_wpf',
            'course_title', 'num_responses', 'response_rate',
            'lr01', 'lr02', 'lr03', 'lr04', 'lr05', 'lr06', 'lr07',
            'pdf_filename',
        ])
        for r in records:
            writer.writerow([
                r.lecturer_name, r.semester, semester_sort_key(r.semester),
                r.is_wpf, r.course_title, r.num_responses, r.response_rate,
                r.lr01, r.lr02, r.lr03, r.lr04, r.lr05, r.lr06, r.lr07,
                r.pdf_filename,
            ])
    print(f'Saved {path} ({len(records)} rows)')


def _save_free_text_csv(records: list[EvaluationRecord], output_dir: str):
    path = os.path.join(output_dir, 'free_text.csv')
    row_count = 0
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'lecturer_name', 'semester', 'course_title', 'category', 'response_text',
        ])
        for r in records:
            for category, responses in [
                ('motivating_methods', r.motivating_methods),
                ('positive_feedback', r.positive_feedback),
                ('improvement_suggestions', r.improvement_suggestions),
            ]:
                for text in responses:
                    writer.writerow([
                        r.lecturer_name, r.semester, r.course_title,
                        category, text,
                    ])
                    row_count += 1
    print(f'Saved {path} ({row_count} rows)')


if __name__ == '__main__':
    run_pipeline()
