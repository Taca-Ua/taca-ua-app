import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

with open(
    os.path.join(current_dir, "step3-final-data/config_cursos_revised.json"), "rb"
) as f:
    courses_data = json.load(f)

if not courses_data:
    raise ValueError(
        "Courses data is empty. Please run the script to generate the config_cursos_revised.json file."
    )
