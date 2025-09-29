import random
import pandas as pd
import json

random.seed(1)


def get_questions_answers(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.read()

    question_answer_lines = lines.split("\n\n")
    question_answer_lines = [line.split('\n') for line in question_answer_lines]

    df = pd.DataFrame(question_answer_lines, columns=['question', 'answers_1', 'answers_2', 'answers_3', 'answers_4'])
    answer_columns = df.columns[1:]
    for col in answer_columns:
        df[col] = df[col].apply(str.strip)
    df["question_number"] = df["question"].str.split('.').str[0].astype(int)
    df["correct_answer"] = df["answers_1"]

    def reorder_answers(row):
        answers = row[answer_columns].tolist()
        correct_answer = row["correct_answer"]
        random.shuffle(answers)
        row[answer_columns] = answers
        correct_answer_index = answers.index(correct_answer)
        row["correct_answer"] = ["a", "b", "c", "d"][correct_answer_index]
        return row

    df = df.apply(reorder_answers, axis=1)
    df = df.sort_values(by="question_number").reset_index(drop=True)
    df = df.set_index('question_number')
    return df

def load_images(images_json):
    with open(images_json, 'r', encoding='utf-8') as f:
        images = json.load(f)["images"]
    images_dict = {}
    for image in images:
        nr = image["question_no"]
        if nr not in images_dict:
            images_dict[nr] = []
        images_dict[nr].append(image)
    return images_dict

def df_to_html_section(df, title, images_dict):
    html = f'<h2>{title}</h2>\n'
    for idx, row in df.iterrows():
        html += f'<details>\n'
        html += f'    <summary>{row["question"]}</summary>\n'
        html += f'    Korrekte Antwort: {row["correct_answer"]}.\n'
        html += f'</details>\n'
        # Insert images if available
        question_no = row.name
        if question_no in images_dict:
            html += '<br>\n'
            for image in images_dict[question_no]:
                image_link = image["link"]
                html += f'<div><img src="{image_link}" alt="Bild zur Frage {question_no}" style="max-width:300px;"></div>\n'
        html += '<ol type="a">\n'
        for i in range(1, 5):
            html += f'    <li>{row[f"answers_{i}"]}</li>\n'
        html += '</ol>\n'
        html += '<br>\n'
        html += '\n'
    return html

def main():
    basisfragen = get_questions_answers('questions/basisfragen.txt')
    spezifische_fragen_binnen = get_questions_answers('questions/spezifische_fragen_binnen.txt')
    spezifische_fragen_segel = get_questions_answers('questions/spezifische_fragen_segeln.txt')
    images_dict = load_images('images.json')

    html = '<!DOCTYPE html>\n<html lang="de">\n<head>\n    <meta charset="UTF-8">\n    <title>SBF Binnen Theoriefragen</title>\n</head>\n<body>\n'
    html += '    <h1>SBF Binnen Theoriefragen (Segel + Motor)</h1>\n'
    html += df_to_html_section(basisfragen, "Basisfragen", images_dict)
    html += df_to_html_section(spezifische_fragen_binnen, "Spezifische Fragen Binnen", images_dict)
    html += df_to_html_section(spezifische_fragen_segel, "Spezifische Fragen Segel", images_dict)
    html += '</body>\n</html>'

    with open('sbf_binnen_fragen.html', 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    main()
