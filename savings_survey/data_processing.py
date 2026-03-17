import matplotlib.pyplot as plt
import model
import file_reader
import config_survey
import custom_analysis

def data_processing(data_in_stream, structure) -> dict[str, dict[str,int]|str]:
    processed_data = {}
    for question in structure:
        question_obj = model.QuestionFactory.create_question(question_data=question)
        question_obj.process_data(data_in_stream)
        question_obj.calculate_score()
        processed_data[question["question"]] = {
            "result": question_obj.result,
            "scores": question_obj.scores
        }
    return processed_data

def horizontal_analysis(data_in_stream, structure) -> dict:
    prio_q = next(q for q in structure if q["type"] == "prioritization")
    excl_q = next(q for q in structure if q["type"] == "selection")
    return custom_analysis.filtered_prioritization(data_in_stream, prio_q, excl_q)


def visualize(data_in_stream, structure):
    question_objs = []
    for question in structure:
        question_obj = model.QuestionFactory.create_question(question_data=question)
        question_obj.process_data(data_in_stream)
        question_obj.calculate_score()
        question_objs.append(question_obj)

    total_axes = sum(q.num_axes for q in question_objs)
    fig, axes = plt.subplots(total_axes, 1, figsize=(10, 4 * total_axes))
    if total_axes == 1:
        axes = [axes]

    idx = 0
    for question_obj in question_objs:
        n = question_obj.num_axes
        axes[idx].set_title(question_obj.question_text, fontsize=11, fontweight='bold')
        question_obj.visualize(axes[idx:idx + n])
        idx += n
    # Horizontale Analyse: Bereinigte Priorisierung
    h_result = horizontal_analysis(data_in_stream, structure)
    fig_h, axes_h = plt.subplots(2, 1, figsize=(10, 8))
    axes_h[0].set_title("Bereinigte Priorisierung (nach Ausschluss)", fontsize=11, fontweight='bold')
    custom_analysis.visualize_filtered_prioritization(axes_h, h_result["result"], h_result["scores"])

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    filename = config_survey.DATA_PATH
    data_in_stream = file_reader.read_csv_to_dict(filename)
    print("Daten eingelesen.")
    processed_data = data_processing(data_in_stream, config_survey.SURVEY_STRUCTURE)
    print(processed_data)
    h_result = horizontal_analysis(data_in_stream, config_survey.SURVEY_STRUCTURE)
    print("\nBereinigte Priorisierung (nach Ausschluss):")
    print(h_result)
    visualize(data_in_stream, config_survey.SURVEY_STRUCTURE)
    