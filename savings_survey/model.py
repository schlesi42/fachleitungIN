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
                rank_int = amount_options+1-int(rank)
                count = values[rank]
                score = rank_int * count
                scores[key] = scores.get(key, 0) + score
        self.scores = scores

    @property
    def num_axes(self):
        return 2

    def visualize(self, axes):
        import numpy as np
        ax_detail, ax_score = axes

        # Detail: Grouped bar chart per option with priorities
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

        # Score: Simple bar chart
        score_values = [self.scores.get(opt, 0) for opt in options]
        ax_score.bar(options, score_values, color='steelblue')
        ax_score.set_ylabel("Score")
        ax_score.set_title("Gewichteter Score", fontsize=10)


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
        ax = axes[0]
        options = list(self.result.keys())
        counts = [self.result[opt] for opt in options]
        ax.bar(options, counts)
        ax.set_ylabel("Anzahl")


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
        else:
            raise ValueError(f"Unsupported question type: {question_type}")
    