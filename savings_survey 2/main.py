import file_reader
import data_processing
import config_survey
import report


def main():
    data = file_reader.read_csv_to_dict(config_survey.DATA_PATH)
    print("Daten eingelesen.")

    questions = data_processing.data_processing(data, config_survey.SURVEY_STRUCTURE)
    print(f"{len(questions)} Fragen verarbeitet.")

    report.generate_pdf(questions, output_path="output/report.pdf")


if __name__ == '__main__':
    main()
