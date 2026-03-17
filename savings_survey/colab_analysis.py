"""
Survey-Analyse: Einsparoptionen
Zur Ausführung in Google Colab. CSV-Datei (data.csv) wird per Upload eingelesen.
"""

import csv
import io
import matplotlib.pyplot as plt
import numpy as np
from google.colab import files

# --- Config ---

SURVEY_STRUCTURE = [
    {
        "question": "Bringen Sie die Optionen in die von Ihnen bevorzugte Reihenfolge (weiter oben bedeutet: Ich bevorzuge die Option)",
        "type": "prioritization",
        "options": {
            "v_1": "Industrie 1 Kurs einsparen",
            "v_2": "Handel 1 Kurs einsparen",
            "v_3": "Studiengang Gesundheitsmanagement stoppen"
        }
    },
    {
        "question": "Die vorherige Frage gewichtet die drei Optionen, aber schließt keine aus. Würden Sie Optionen komplett ausschließen?",
        "type": "selection",
        "options": {
            "v_6": "Industrie 1 Kurs einsparen",
            "v_7": "Handel 1 Kurs einsparen",
            "v_8": "Studiengang Gesundheitsmanagement stoppen"
        }
    },
    {
        "question": "Gibt es sonstiges Feedback (zu den drei Optionen oder weiteren Optionen, ganz neue Vorschläge etc.)?",
        "type": "text",
        "options": {
            "v_11": "Gibt es sonstiges Feedback (zu den drei Optionen oder weiteren Optionen, ganz neue Vorschläge etc.)?"
        }
    }
]

# --- File Reader ---

def read_csv_to_dict(content_bytes):
    result = {}
    text = content_bytes.decode('utf-8')
    reader = csv.DictReader(io.StringIO(text), delimiter=';')
    for fieldname in reader.fieldnames:
        result[fieldname] = []
    for row in reader:
        for key, value in row.items():
            result[key].append(value)
    return result

# --- Model ---

class SurveyQuestion:
    def __init__(self, question_text, question_type, options, result=None, scores=None):
        self.question_text = question_text
        self.question_type = question_type
        self.options = options
        self.result = result if result is not None else {}
        self.scores = scores if scores is not None else {}

    @property
    def num_axes(self):
        return 1

    def process_data(self, data):
        pass

    def calculate_score(self):
        pass

    def visualize(self, axes):
        pass


class PrioritizationQuestion(SurveyQuestion):
    def __init__(self, question_text, options):
        super().__init__(question_text, "prioritization", options)

    def process_data(self, data):
        for option in self.options.keys():
            data_list = data.get(option, [])
            values = set(v for v in data_list if v and v != "0")
            amounts = [data_list.count(value) for value in values]
            key = self.options[option]
            self.result[key] = dict(sorted(zip(values, amounts)))

    def calculate_score(self):
        amount_options = len(self.result)
        scores = {}
        for key in self.result.keys():
            values = self.result[key]
            for rank in values.keys():
                rank_int = amount_options + 1 - int(rank)
                count = values[rank]
                score = rank_int * count
                scores[key] = scores.get(key, 0) + score
        self.scores = scores

    @property
    def num_axes(self):
        return 2

    def visualize(self, axes):
        ax_detail, ax_score = axes

        options = list(self.result.keys())
        ranks = sorted({r for vals in self.result.values() for r in vals.keys()})
        x = np.arange(len(options))
        width = 0.8 / len(ranks)
        for i, rank in enumerate(ranks):
            counts = [self.result[opt].get(rank, 0) for opt in options]
            ax_detail.bar(x + i * width, counts, width, label=f"Priorität {rank}")
        ax_detail.set_xticks(x + width * (len(ranks) - 1) / 2)
        ax_detail.set_xticklabels(options, rotation=15, ha='right')
        ax_detail.set_ylabel("Anzahl")
        ax_detail.legend()

        score_values = [self.scores.get(opt, 0) for opt in options]
        ax_score.bar(options, score_values, color='steelblue')
        ax_score.set_ylabel("Score")
        ax_score.set_title("Gewichteter Score", fontsize=10)


class SelectionQuestion(SurveyQuestion):
    def __init__(self, question_text, options):
        super().__init__(question_text, "selection", options)
        self.result = {}

    def process_data(self, data):
        for option in self.options.keys():
            data_list = data.get(option, [])
            count_yes = data_list.count("1")
            key = self.options[option]
            self.result[key] = count_yes

    def calculate_score(self):
        scores = {key: 0 for key in self.result.keys()}
        for key in self.result.keys():
            if self.result[key] > 0:
                scores[key] = self.result[key]
        self.scores = scores

    def visualize(self, axes):
        ax = axes[0]
        options = list(self.result.keys())
        counts = [self.result[opt] for opt in options]
        ax.bar(options, counts)
        ax.set_ylabel("Anzahl")


class TextQuestion(SurveyQuestion):
    def __init__(self, question_text, options):
        super().__init__(question_text, "text", options)
        self.responses = []

    def process_data(self, data):
        for option in self.options.keys():
            data_list = data.get(option, [])
            self.responses.extend(data_list)
        self.result = self.responses

    def visualize(self, axes):
        ax = axes[0]
        ax.axis('off')
        text = "\n".join(f"- {r}" for r in self.responses if r and r != "-99")
        ax.text(0, 1, text, transform=ax.transAxes, verticalalignment='top',
                fontsize=9, wrap=True)


class QuestionFactory:
    @staticmethod
    def create_question(question_data):
        question_type = question_data["type"]
        if question_type == "prioritization":
            return PrioritizationQuestion(question_data["question"], question_data["options"])
        elif question_type == "selection":
            return SelectionQuestion(question_data["question"], question_data["options"])
        elif question_type == "text":
            return TextQuestion(question_data["question"], question_data["options"])
        else:
            raise ValueError(f"Unsupported question type: {question_type}")

# --- Horizontale Analyse ---

def filtered_prioritization(data, prioritization_q, exclusion_q):
    """
    Für jeden Teilnehmer werden ausgeschlossene Optionen (Q2)
    aus der Priorisierung (Q1) herausgerechnet.
    """
    prio_options = prioritization_q["options"]
    excl_options = exclusion_q["options"]

    excl_to_prio = {}
    label_to_prio_col = {label: col for col, label in prio_options.items()}
    for excl_col, label in excl_options.items():
        if label in label_to_prio_col:
            excl_to_prio[excl_col] = label_to_prio_col[label]

    num_respondents = len(next(iter(data.values())))
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

    result = {label: dict(sorted(ranks.items())) for label, ranks in result.items()}

    amount_options = len(result)
    scores = {}
    for label, ranks in result.items():
        for rank, count in ranks.items():
            rank_int = amount_options + 1 - int(rank)
            scores[label] = scores.get(label, 0) + rank_int * count

    return {"result": result, "scores": scores}


# --- Ausführung ---

print("Bitte data.csv hochladen:")
uploaded = files.upload()
filename = list(uploaded.keys())[0]
data = read_csv_to_dict(uploaded[filename])
print(f"{len(list(data.values())[0])} Antworten eingelesen.\n")

questions = []
for q in SURVEY_STRUCTURE:
    obj = QuestionFactory.create_question(q)
    obj.process_data(data)
    obj.calculate_score()
    questions.append(obj)

for obj in questions:
    print(f"Frage: {obj.question_text}")
    print(f"  Ergebnis: {obj.result}")
    print(f"  Scores:   {obj.scores}")
    print()

total_axes = sum(q.num_axes for q in questions)
fig, axes = plt.subplots(total_axes, 1, figsize=(10, 4 * total_axes))
if total_axes == 1:
    axes = [axes]

idx = 0
for obj in questions:
    n = obj.num_axes
    axes[idx].set_title(obj.question_text, fontsize=11, fontweight='bold')
    obj.visualize(axes[idx:idx + n])
    idx += n

plt.tight_layout()
plt.show()

# --- Bereinigte Priorisierung (horizontale Analyse) ---

prio_q = next(q for q in SURVEY_STRUCTURE if q["type"] == "prioritization")
excl_q = next(q for q in SURVEY_STRUCTURE if q["type"] == "selection")
h_result = filtered_prioritization(data, prio_q, excl_q)

print("Bereinigte Priorisierung (nach Ausschluss):")
print(f"  Ergebnis: {h_result['result']}")
print(f"  Scores:   {h_result['scores']}")
print()

fig_h, axes_h = plt.subplots(2, 1, figsize=(10, 8))
ax_detail, ax_score = axes_h

ax_detail.set_title("Bereinigte Priorisierung (nach Ausschluss)", fontsize=11, fontweight='bold')
options_h = list(h_result["result"].keys())
ranks_h = sorted({r for vals in h_result["result"].values() for r in vals.keys()})
x_h = np.arange(len(options_h))
width_h = 0.8 / len(ranks_h) if ranks_h else 0.8

for i, rank in enumerate(ranks_h):
    counts = [h_result["result"][opt].get(rank, 0) for opt in options_h]
    ax_detail.bar(x_h + i * width_h, counts, width_h, label=f"Priorität {rank}")
ax_detail.set_xticks(x_h + width_h * (len(ranks_h) - 1) / 2)
ax_detail.set_xticklabels(options_h, rotation=15, ha='right')
ax_detail.set_ylabel("Anzahl")
ax_detail.legend()

score_values_h = [h_result["scores"].get(opt, 0) for opt in options_h]
ax_score.bar(options_h, score_values_h, color='steelblue')
ax_score.set_ylabel("Score")
ax_score.set_title("Gewichteter Score (bereinigt)", fontsize=10)

plt.tight_layout()
plt.show()
