import numpy as np


def filtered_prioritization(data: dict[str, list[str]], prioritization_q: dict, exclusion_q: dict) -> dict:
    """
    Horizontale Analyse: Für jeden Teilnehmer werden ausgeschlossene Optionen (Q2)
    aus der Priorisierung (Q1) herausgerechnet.
    """
    prio_options = prioritization_q["options"]
    excl_options = exclusion_q["options"]

    # Mapping: Q2-Spalte → Q1-Spalte über gemeinsame Labels
    excl_to_prio = {}
    label_to_prio_col = {label: col for col, label in prio_options.items()}
    for excl_col, label in excl_options.items():
        if label in label_to_prio_col:
            excl_to_prio[excl_col] = label_to_prio_col[label]

    num_respondents = len(next(iter(data.values())))

    # Bereinigte Häufigkeiten zählen
    result = {prio_options[col]: {} for col in prio_options}

    for i in range(num_respondents):
        for excl_col, prio_col in excl_to_prio.items():
            excluded = data.get(excl_col, ["0"] * num_respondents)[i] == "1"
            if excluded:
                continue
            rank = data.get(prio_col, [""] * num_respondents)[i]
            if rank and rank != "0":
                label = prio_options[prio_col]
                result[label][rank] = result[label].get(rank, 0) + 1

    # Ränge sortieren
    result = {label: dict(sorted(ranks.items())) for label, ranks in result.items()}

    # Scores berechnen (gleiche Logik wie PrioritizationQuestion)
    amount_options = len(result)
    scores = {}
    for label, ranks in result.items():
        for rank, count in ranks.items():
            rank_int = amount_options + 1 - int(rank)
            scores[label] = scores.get(label, 0) + rank_int * count

    return {"result": result, "scores": scores}


def visualize_filtered_prioritization(axes, result: dict, scores: dict):
    """Visualisiert die bereinigte Priorisierung (Detail + Score)."""
    ax_detail, ax_score = axes

    options = list(result.keys())
    ranks = sorted({r for vals in result.values() for r in vals.keys()})
    x = np.arange(len(options))
    width = 0.8 / len(ranks) if ranks else 0.8

    for i, rank in enumerate(ranks):
        counts = [result[opt].get(rank, 0) for opt in options]
        ax_detail.bar(x + i * width, counts, width, label=f"Priorität {rank}")
    ax_detail.set_xticks(x + width * (len(ranks) - 1) / 2)
    ax_detail.set_xticklabels(options, rotation=15, ha='right')
    ax_detail.set_ylabel("Anzahl")
    ax_detail.legend()

    score_values = [scores.get(opt, 0) for opt in options]
    ax_score.bar(options, score_values, color='steelblue')
    ax_score.set_ylabel("Score")
    ax_score.set_title("Gewichteter Score (bereinigt)", fontsize=10)
