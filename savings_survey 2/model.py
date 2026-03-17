class SurveyQuestion:
    def __init__(self, question_text: str, question_type: str, options: dict[str, str], result=None, scores=None):
        self.question_text = question_text
        self.question_type = question_type
        self.options = options
        self.result = result if result is not None else {}
        self.scores = scores if scores is not None else {}
    
    def process_data(self, data: dict[str, list[str]]):
        pass
    
    def calculate_score(self):
        pass

    @property
    def num_axes(self):
        return 1

    def visualize(self, axes):
        pass


class PrioritizationQuestion(SurveyQuestion):
    def __init__(self, question_text: str, options: dict[str, str]):
        super().__init__(question_text, "prioritization", options)

        
    
    def process_data(self, data: dict[str, list[str]]):
            
        for option in self.options.keys():
            data_list = data.get(option, [])
            values = set(data_list)
            amounts = [data_list.count(value) for value in values]
            key = self.options[option]
            self.result[key] = dict(sorted(zip(values, amounts)))
        
    # Borda-Count-Verfahren: Je höher die Priorität (niedrigere Zahl), desto mehr Punkte
    def calculate_score(self):
        amount_options = len(self.result)
        scores = {}
        for key in self.result.keys():
            values = self.result[key]
            for rank in values.keys():
                rank_int = amount_options - int(rank)
                count = values[rank]
                score = rank_int * count
                scores[key] = scores.get(key, 0) + score
        self.scores = scores

    @property
    def num_axes(self):
        return 3

    def visualize(self, axes):
        import re
        import numpy as np
        import textwrap
        import matplotlib.pyplot as plt
        ax_detail, ax_score, ax_table = axes

        options = list(self.result.keys())
        ranks = sorted({r for vals in self.result.values() for r in vals.keys()}, key=int)

        def abbrev(text):
            m = re.search(r'\(([A-Z]+)\)', text)
            return m.group(1) if m else textwrap.fill(text, width=10)

        wrapped_labels = [textwrap.fill(opt, width=18) for opt in options]
        abbrev_labels  = [abbrev(opt) for opt in options]

        # --- Detail: Grouped bar chart ---
        x = np.arange(len(options))
        width = 0.8 / len(ranks)
        for i, rank in enumerate(ranks):
            counts = [self.result[opt].get(rank, 0) for opt in options]
            ax_detail.bar(x + i * width, counts, width, label=f"Priorität {rank}")
        ax_detail.set_xticks(x + width * (len(ranks) - 1) / 2)
        ax_detail.set_xticklabels(wrapped_labels, rotation=30, ha='right', fontsize=8)
        ax_detail.set_ylabel("Anzahl")
        ax_detail.set_title("Rangverteilung", fontsize=10)
        ax_detail.legend(fontsize=8)

        # --- Score: horizontal bar chart with grid ---
        score_values = [self.scores.get(opt, 0) for opt in options]
        ax_score.barh(abbrev_labels, score_values, color='steelblue', height=0.6)
        ax_score.set_xlabel("Score")
        ax_score.set_title("Borda-Score", fontsize=10)
        ax_score.invert_yaxis()
        ax_score.xaxis.set_major_locator(plt.MaxNLocator(integer=True, nbins=6))
        ax_score.xaxis.grid(True, linestyle='--', linewidth=0.6, alpha=0.5, color='gray')
        ax_score.set_axisbelow(True)

        # --- Tabelle: Optionen × Anzahl pro Rang ---
        table_data = [[self.result[opt].get(rank, 0) for rank in ranks] for opt in options]
        col_labels  = [f"Rang {r}" for r in ranks]
        table = ax_table.table(
            cellText=table_data,
            rowLabels=abbrev_labels,
            colLabels=col_labels,
            loc='center',
            cellLoc='center',
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.8)
        ax_table.axis('off')
        ax_table.set_title("Übersicht Rangverteilung", fontsize=10)


class SelectionQuestion(SurveyQuestion):
    def __init__(self, question_text: str, options: dict[str, str]):
        super().__init__(question_text, "selection", options)
        self.result = {}
       

    def process_data(self, data: dict[str, list[str]]):
        for option in self.options.keys():
            data_list = data.get(option, [])
            count_yes = data_list.count("1")
            key = self.options[option]
            self.result[key] = count_yes  

    def calculate_score(self):
        scores = {key:0 for key in self.result.keys()}
        for key in self.result.keys():
            if self.result[key] > 0:
                scores[key] = self.result[key]
        self.scores = scores

    def visualize(self, axes):
        import textwrap
        ax = axes[0]
        options = list(self.result.keys())
        short_labels = [textwrap.fill(opt, width=18) for opt in options]
        counts = [self.result[opt] for opt in options]
        ax.barh(short_labels, counts, color='steelblue')
        ax.set_xlabel("Anzahl")
        ax.invert_yaxis()

class MultiSelectionQuestion(SurveyQuestion):
    def __init__(self, question_text: str, options: dict[str, str]):
        super().__init__(question_text, "multi_selection", options)
        self.result = {}
       

    def process_data(self, data: dict[str, list[str]]):
        for option in self.options.keys():
            data_list = data.get(option, [])
            count_yes = data_list.count("1")
            key = self.options[option]
            self.result[key] = count_yes  

    def calculate_score(self):
        scores = {key:0 for key in self.result.keys()}
        for key in self.result.keys():
            if self.result[key] > 0:
                scores[key] = self.result[key]
        self.scores = scores

    def visualize(self, axes):
        import textwrap
        ax = axes[0]
        options = list(self.result.keys())
        short_labels = [textwrap.fill(opt, width=18) for opt in options]
        counts = [self.result[opt] for opt in options]
        ax.barh(short_labels, counts, color='steelblue')
        ax.set_xlabel("Anzahl")
        ax.invert_yaxis()

class TextQuestion(SurveyQuestion):
    def __init__(self, question_text: str, options: dict[str, str]):
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
    def create_question(question_data: dict) -> SurveyQuestion:
        question_type = question_data["type"]

        if question_type == "prioritization":
            return PrioritizationQuestion(
                question_text=question_data["question"],
                options=question_data["options"]
            )
        elif question_type == "selection":
            return SelectionQuestion(
                question_text=question_data["question"],
                options=question_data["options"]
            )
        elif question_type == "text":
            return TextQuestion(
                question_text=question_data["question"],
                options=question_data["options"]
            )
        elif question_type == "multi_selection":
            return MultiSelectionQuestion(
                question_text=question_data["question"],
                options=question_data["options"]
            )
        else:
            raise ValueError(f"Unsupported question type: {question_type}")
    