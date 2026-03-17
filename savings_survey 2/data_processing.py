import model
import file_reader
import config_survey


def data_processing(data_in_stream, structure) -> list:
    questions = []
    for question in structure:
        question_obj = model.QuestionFactory.create_question(question_data=question)
        question_obj.process_data(data_in_stream)
        question_obj.calculate_score()
        questions.append(question_obj)
    return questions


if __name__ == '__main__':
    filename = config_survey.DATA_PATH
    data_in_stream = file_reader.read_csv_to_dict(filename)
    print("Daten eingelesen.")
    questions = data_processing(data_in_stream, config_survey.SURVEY_STRUCTURE)
    for q in questions:
        print(q.question_text[:60], "...")
        print("  result:", q.result)
        print("  scores:", q.scores)
