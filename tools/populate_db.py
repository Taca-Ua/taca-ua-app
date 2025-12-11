import requests

API_URL = "http://localhost/api/admin"


def populate_modalities_types():
    check = requests.get(f"{API_URL}/modality-types")
    if check.status_code == 200 and len(check.json()) > 0:
        print("Modality types already populated.")
        return None

    modalities_types = [
        {
            "name": "Modalidades Coletivas Recorrentes",
            "description": "Modalidades coletivas que ocorrem de forma recorrente ao longo da época desportiva.",
            "escaloes": [
                {
                    "escalao": "A",
                    "minParticipants": 41,
                    "maxParticipants": None,
                    "points": [140, 130, 120, 110, 90, 80, 70, 60, 40, 30, 20, 10],
                },
                {
                    "escalao": "B",
                    "minParticipants": 32,
                    "maxParticipants": 40,
                    "points": [105, 98, 90, 83, 68, 60, 53, 45, 30, 23, 15, 8],
                },
                {
                    "escalao": "C",
                    "minParticipants": 19,
                    "maxParticipants": 31,
                    "points": [92, 86, 79, 73, 60, 53, 46, 40, 27, 20, 13, 7],
                },
                {
                    "escalao": "D",
                    "minParticipants": 9,
                    "maxParticipants": 18,
                    "points": [79, 73, 68, 62, 51, 45, 39, 34, 23, 17, 11, 6],
                },
                {
                    "escalao": "E",
                    "minParticipants": None,
                    "maxParticipants": 8,
                    "points": [59, 55, 51, 46, 38, 34, 30, 25],
                },
            ],
        },
        {
            "name": "Modalidades Coletivas Pontuais",
            "description": "Modalidades coletivas que ocorrem de forma pontual ao longo da época desportiva.",
            "escaloes": [
                {
                    "escalao": "A",
                    "minParticipants": 15,
                    "maxParticipants": None,
                    "points": [92, 86, 79, 73, 60, 53, 46, 40, 27, 20, 13, 7],
                },
                {
                    "escalao": "B",
                    "minParticipants": 11,
                    "maxParticipants": 15,
                    "points": [79, 73, 68, 62, 51, 45, 39, 34, 23, 17],
                },
                {
                    "escalao": "C",
                    "minParticipants": 7,
                    "maxParticipants": 10,
                    "points": [59, 55, 51, 46, 38, 34, 30],
                },
                {
                    "escalao": "D",
                    "minParticipants": None,
                    "maxParticipants": 6,
                    "points": [45, 41, 38, 35],
                },
            ],
        },
        {
            "name": "Modalidades Duplas/pares",
            "description": "Modalidades praticadas em duplas ou pares.",
            "escaloes": [
                {
                    "escalao": "A",
                    "minParticipants": 15,
                    "maxParticipants": None,
                    "points": [49, 44, 39, 35, 28, 24, 21, 18, 15, 13, 11, 9],
                },
                {
                    "escalao": "B",
                    "minParticipants": 11,
                    "maxParticipants": 15,
                    "points": [39, 34, 30, 27, 21, 18, 16, 14, 9, 7],
                },
                {
                    "escalao": "C",
                    "minParticipants": 6,
                    "maxParticipants": 10,
                    "points": [31, 27, 23, 21, 16, 14],
                },
                {
                    "escalao": "D",
                    "minParticipants": None,
                    "maxParticipants": 5,
                    "points": [25, 21, 18],
                },
            ],
        },
        {
            "name": "Modalidades Individuais",
            "description": "Modalidades praticadas individualmente.",
            "escaloes": [
                {
                    "escalao": "A",
                    "minParticipants": 25,
                    "maxParticipants": None,
                    "points": [36, 31, 28, 24, 21, 19, 16, 14, 11, 9, 7, 5],
                },
                {
                    "escalao": "B",
                    "minParticipants": 17,
                    "maxParticipants": 25,
                    "points": [30, 26, 21, 18, 16, 14, 12, 10, 8, 6, 4, 3],
                },
                {
                    "escalao": "C",
                    "minParticipants": 9,
                    "maxParticipants": 16,
                    "points": [24, 21, 18, 16, 13, 11, 9, 8, 5, 4, 2],
                },
                {
                    "escalao": "D",
                    "minParticipants": 4,
                    "maxParticipants": 8,
                    "points": [19, 16, 13, 11, 8, 6, 4, 2],
                },
                {
                    "escalao": "E",
                    "minParticipants": None,
                    "maxParticipants": 3,
                    "points": [15, 12, 9],
                },
            ],
        },
        {
            "name": "Troféus Coletivos",
            "description": "Troféus atribuídos a equipas coletivas com base no desempenho em várias competições.",
            "escaloes": [
                {
                    "escalao": "A",
                    "minParticipants": 10,
                    "maxParticipants": None,
                    "points": [78, 71, 63, 56, 50, 43, 35, 30, 20, 15, 10, 5],
                },
                {
                    "escalao": "B",
                    "minParticipants": 8,
                    "maxParticipants": 10,
                    "points": [59, 53, 48, 43, 38, 33, 28, 23, 15, 11],
                },
                {
                    "escalao": "C",
                    "minParticipants": 5,
                    "maxParticipants": 7,
                    "points": [39, 37, 34, 31, 25, 23, 20],
                },
                {
                    "escalao": "D",
                    "minParticipants": None,
                    "maxParticipants": 4,
                    "points": [30, 27, 25, 23],
                },
            ],
        },
        {
            "name": "Apuramento para os Playoffs",
            "description": "Apuramento para os playoffs com base no desempenho em competições.",
            "escaloes": [
                {
                    "escalao": "-",
                    "minParticipants": None,
                    "maxParticipants": None,
                    "points": [30, 26, 23, 19, 14, 12, 10, 9],
                }
            ],
        },
    ]

    ids = {}
    for modality_type in modalities_types:
        response = requests.post(f"{API_URL}/modality-types", json=modality_type)
        if response.status_code == 201:
            print(f"Created modality type: {modality_type['name']}")
            ids[modality_type["name"]] = response.json().get("id", None)
        else:
            print(
                f"Failed to create modality type: {modality_type['name']}, Status Code: {response.status_code}, Response: {response.text}"
            )

    return ids


def populate_modalidades(modality_types_dict=None):
    if modality_types_dict is None:
        data = requests.get(f"{API_URL}/modality-types")
        modality_types = data.json()
        modality_types_dict = {mt["name"]: mt["id"] for mt in modality_types}

    print("Modality Types Dict:", modality_types_dict)

    check = requests.get(f"{API_URL}/modalities")
    if check.status_code == 200 and len(check.json()) > 0:
        print("Modalities already populated.")
        return check.json()

    modalidades = [
        {
            "name": "Andebol",
            "modality_type_id": modality_types_dict[
                "Modalidades Coletivas Recorrentes"
            ],
        },
        {
            "name": "Atletismo",
            "modality_type_id": modality_types_dict["Modalidades Individuais"],
        },
        {
            "name": "Badminton",
            "modality_type_id": modality_types_dict["Modalidades Duplas/pares"],
        },
        {
            "name": "Basquetebol 3x3",
            "modality_type_id": modality_types_dict[
                "Modalidades Coletivas Recorrentes"
            ],
        },
        {
            "name": "Stand-Up Paddle",
            "modality_type_id": modality_types_dict["Modalidades Individuais"],
        },
        {
            "name": "Canoagem",
            "modality_type_id": modality_types_dict["Modalidades Individuais"],
        },
        {
            "name": "Ciclismo",
            "modality_type_id": modality_types_dict["Modalidades Individuais"],
        },
        {
            "name": "Corfebol",
            "modality_type_id": modality_types_dict["Modalidades Coletivas Pontuais"],
        },
        {
            "name": "EA Sports FC",
            "modality_type_id": modality_types_dict["Modalidades Individuais"],
        },
        {
            "name": "Valorant",
            "modality_type_id": modality_types_dict["Modalidades Coletivas Pontuais"],
        },
        {
            "name": "CS 2",
            "modality_type_id": modality_types_dict["Modalidades Coletivas Pontuais"],
        },
        {
            "name": "League of Legends",
            "modality_type_id": modality_types_dict["Modalidades Coletivas Pontuais"],
        },
        {
            "name": "Futsal",
            "modality_type_id": modality_types_dict[
                "Modalidades Coletivas Recorrentes"
            ],
        },
        {
            "name": "Corta-mato",
            "modality_type_id": modality_types_dict["Modalidades Individuais"],
        },
        {
            "name": "Futebol 7 Masculino",
            "modality_type_id": modality_types_dict[
                "Modalidades Coletivas Recorrentes"
            ],
        },
        {
            "name": "Futebol 7 Feminino",
            "modality_type_id": modality_types_dict["Modalidades Coletivas Pontuais"],
        },
        {
            "name": "Matraquilhos",
            "modality_type_id": modality_types_dict["Modalidades Duplas/pares"],
        },
        {
            "name": "Natação",
            "modality_type_id": modality_types_dict["Modalidades Individuais"],
        },
        {
            "name": "Orientação",
            "modality_type_id": modality_types_dict["Modalidades Individuais"],
        },
        {
            "name": "Padel",
            "modality_type_id": modality_types_dict["Modalidades Individuais"],
        },
        {
            "name": "Squash",
            "modality_type_id": modality_types_dict["Modalidades Individuais"],
        },
        {
            "name": "Ténis",
            "modality_type_id": modality_types_dict["Modalidades Duplas/pares"],
        },
        {
            "name": "Ténis de Mesa",
            "modality_type_id": modality_types_dict["Modalidades Duplas/pares"],
        },
        {
            "name": "Voleibol 4x4",
            "modality_type_id": modality_types_dict[
                "Modalidades Coletivas Recorrentes"
            ],
        },
        {
            "name": "Xadrez",
            "modality_type_id": modality_types_dict["Modalidades Individuais"],
        },
        {
            "name": "Polybat",
            "modality_type_id": modality_types_dict["Modalidades Individuais"],
        },
        {
            "name": "Taekwondo",
            "modality_type_id": modality_types_dict["Modalidades Individuais"],
        },
        {
            "name": "Ultimate Frisbee",
            "modality_type_id": modality_types_dict["Modalidades Coletivas Pontuais"],
        },
        {
            "name": "Dardos",
            "modality_type_id": modality_types_dict["Modalidades Individuais"],
        },
        {
            "name": "Touch Rugby",
            "modality_type_id": modality_types_dict["Modalidades Coletivas Pontuais"],
        },
        {
            "name": "Dr. Why",
            "modality_type_id": modality_types_dict["Modalidades Individuais"],
        },
        {
            "name": "Sueca",
            "modality_type_id": modality_types_dict["Modalidades Duplas/pares"],
        },
        {
            "name": "Goalball",
            "modality_type_id": modality_types_dict["Modalidades Coletivas Pontuais"],
        },
    ]

    resp_modalidades = []
    for modalidade in modalidades:
        response = requests.post(f"{API_URL}/modalities", json=modalidade)
        if response.status_code == 201:
            print(f"Created modality: {modalidade['name']}")
            resp_modalidades.append(response.json())
        else:
            print(
                f"Failed to create modality: {modalidade['name']}, Status Code: {response.status_code}, Response: {response.text}"
            )

    return resp_modalidades


def populate_nucleos():
    check = requests.get(f"{API_URL}/nucleos")
    if check.status_code == 200 and len(check.json()) > 0:
        print("Nucleos already populated.")
        return check.json()

    nucleos = [
        {"name": "NEAP", "abbreviation": "NEAP"},
        {"name": "NEEA", "abbreviation": "NEEA"},
        {"name": "NEB", "abbreviation": "NEB"},
        {"name": "NEBEC", "abbreviation": "NEBEC"},
        {"name": "NECiB", "abbreviation": "NECiB"},
        {"name": "NEMu", "abbreviation": "NEMu"},
        {"name": "NEMTC", "abbreviation": "NEMTC"},
        {"name": "NED", "abbreviation": "NED"},
        {"name": "NEG", "abbreviation": "NEG"},
        {"name": "NEEC", "abbreviation": "NEEC"},
        {"name": "NEGPT", "abbreviation": "NEGPT"},
        {"name": "NEEMec", "abbreviation": "NEEMec"},
        {"name": "NEECT", "abbreviation": "NEECT"},
        {"name": "NEEET", "abbreviation": "NEEET"},
        {"name": "NEI", "abbreviation": "NEI"},
        {"name": "NECM", "abbreviation": "NECM"},
        {"name": "NEMOC", "abbreviation": "NEMOC"},
        {"name": "NEEF", "abbreviation": "NEEF"},
        {"name": "NEM", "abbreviation": "NEM"},
        {"name": "NEP", "abbreviation": "NEP"},
        {"name": "NEEB", "abbreviation": "NEEB"},
        {"name": "NEBG", "abbreviation": "NEBG"},
        {"name": "NEGeo", "abbreviation": "NEGeo"},
        {"name": "NEEE", "abbreviation": "NEEE"},
        {"name": "NELLC", "abbreviation": "NELLC"},
        {"name": "NELRE", "abbreviation": "NELRE"},
        {"name": "NET", "abbreviation": "NET"},
        {"name": "NEMat", "abbreviation": "NEMat"},
        {"name": "NEEQu", "abbreviation": "NEEQu"},
        {"name": "NEQ", "abbreviation": "NEQ"},
        {"name": "NAE-ESAN", "abbreviation": "NAE-ESAN"},
        {"name": "NAE-ESSUA", "abbreviation": "NAE-ESSUA"},
        {"name": "NAE-ESTGA", "abbreviation": "NAE-ESTGA"},
        {"name": "NAE-ISCA", "abbreviation": "NAE-ISCA"},
        {"name": "NEMOG", "abbreviation": "NEMOG"},
    ]

    resp_nucleos = []
    for nucleo in nucleos:
        response = requests.post(f"{API_URL}/nucleos", json=nucleo)
        if response.status_code == 201:
            print(f"Created nucleo: {nucleo['name']}")
            resp_nucleos.append(response.json())
        else:
            print(
                f"Failed to create nucleo: {nucleo['name']}, Status Code: {response.status_code}, Response: {response.text}"
            )

    return resp_nucleos


def populate_courses(nucleos):
    check = requests.get(f"{API_URL}/courses")
    if check.status_code == 200 and len(check.json()) > 0:
        print("Courses already populated.")
        return check.json()

    nucleos_dict = {nucleo["abbreviation"]: nucleo["id"] for nucleo in nucleos}

    courses = [
        {"name": "Administração Pública", "nucleo_id": nucleos_dict["NEAP"]},
        {
            "name": "Automação e Sistemas de Produção",
            "nucleo_id": nucleos_dict["NAE-ESAN"],
        },
        {"name": "Biologia", "nucleo_id": nucleos_dict["NEB"]},
        {"name": "Biologia e Geologia", "nucleo_id": nucleos_dict["NEBG"]},
        {"name": "Bioquímica", "nucleo_id": nucleos_dict["NEQ"]},
        {"name": "Biotecnologia", "nucleo_id": nucleos_dict["NEQ"]},
        {"name": "Ciências Biomédicas", "nucleo_id": nucleos_dict["NECiB"]},
        {"name": "Ciências do Mar", "nucleo_id": nucleos_dict["NECM"]},
        {"name": "Contabilidade", "nucleo_id": nucleos_dict["NAE-ISCA"]},
        {"name": "Contabilidade pós-laboral", "nucleo_id": nucleos_dict["NAE-ISCA"]},
        {"name": "Design", "nucleo_id": nucleos_dict["NED"]},
        {
            "name": "Design de Produto e Tecnologia",
            "nucleo_id": nucleos_dict["NAE-ESAN"],
        },
        {"name": "Economia", "nucleo_id": nucleos_dict["NEEC"]},
        {"name": "Educação Básica", "nucleo_id": nucleos_dict["NEEB"]},
        {
            "name": "Eletrónica e Mecânica Industrial",
            "nucleo_id": nucleos_dict["NAE-ESTGA"],
        },
        {"name": "Enfermagem", "nucleo_id": nucleos_dict["NAE-ESSUA"]},
        {"name": "Engenharia Aeroespacial", "nucleo_id": nucleos_dict["NEEET"]},
        {"name": "Engenharia Biomédica", "nucleo_id": nucleos_dict["NEEF"]},
        {"name": "Engenharia Civil", "nucleo_id": nucleos_dict["NAE-ISCA"]},
        {"name": "Engenharia Computacional", "nucleo_id": nucleos_dict["NEEF"]},
        {
            "name": "Engenharia de Automação Industrial",
            "nucleo_id": nucleos_dict["NEEMec"],
        },
        {
            "name": "Engenharia de Computadores e Informática",
            "nucleo_id": nucleos_dict["NEECT"],
        },
        {"name": "Engenharia de Materiais", "nucleo_id": nucleos_dict["NEM"]},
        {"name": "Engenharia do Ambiente", "nucleo_id": nucleos_dict["NEEA"]},
        {
            "name": "Engenharia Eletrotécnica e de Computadores",
            "nucleo_id": nucleos_dict["NEEET"],
        },
        {"name": "Engenharia Física", "nucleo_id": nucleos_dict["NEEF"]},
        {"name": "Engenharia Informática", "nucleo_id": nucleos_dict["NEI"]},
        {
            "name": "Engenharia Informática Aplicada",
            "nucleo_id": nucleos_dict["NAE-ESTGA"],
        },
        {"name": "Engenharia Mecânica", "nucleo_id": nucleos_dict["NEEMec"]},
        {"name": "Engenharia Química", "nucleo_id": nucleos_dict["NEEQu"]},
        {"name": "Finanças", "nucleo_id": nucleos_dict["NAE-ISCA"]},
        {"name": "Finanças pós-laboral", "nucleo_id": nucleos_dict["NAE-ISCA"]},
        {"name": "Física", "nucleo_id": nucleos_dict["NEEF"]},
        {"name": "Fisioterapia", "nucleo_id": nucleos_dict["NAE-ESSUA"]},
        {"name": "Geologia", "nucleo_id": nucleos_dict["NEGeo"]},
        {"name": "Gestão", "nucleo_id": nucleos_dict["NEG"]},
        {"name": "Gestão Comercial", "nucleo_id": nucleos_dict["NAE-ESTGA"]},
        {"name": "Gestão da Qualidade", "nucleo_id": nucleos_dict["NAE-ESTGA"]},
        {"name": "Gestão e Planeamento em Turismo", "nucleo_id": nucleos_dict["NEGPT"]},
        {"name": "Gestão Pública", "nucleo_id": nucleos_dict["NAE-ESTGA"]},
        {
            "name": "Imagem Médica e Radioterapia",
            "nucleo_id": nucleos_dict["NAE-ESSUA"],
        },
        {"name": "Línguas e Estudos Editoriais", "nucleo_id": nucleos_dict["NEEE"]},
        {"name": "Línguas e Relações Empresariais", "nucleo_id": nucleos_dict["NELRE"]},
        {"name": "Línguas, Literaturas e Culturas", "nucleo_id": nucleos_dict["NELLC"]},
        {"name": "Marketing", "nucleo_id": nucleos_dict["NAE-ISCA"]},
        {"name": "Marketing pós-laboral", "nucleo_id": nucleos_dict["NAE-ISCA"]},
        {"name": "Matemática", "nucleo_id": nucleos_dict["NEMat"]},
        {
            "name": "Meteorologia, Oceanografia e Clima",
            "nucleo_id": nucleos_dict["NEMOC"],
        },
        {
            "name": "Multimédia e Tecnologias da Comunicação",
            "nucleo_id": nucleos_dict["NEMTC"],
        },
        {"name": "Música", "nucleo_id": nucleos_dict["NEMu"]},
        {"name": "Psicologia", "nucleo_id": nucleos_dict["NEP"]},
        {"name": "Química", "nucleo_id": nucleos_dict["NEQ"]},
        {
            "name": "Secretariado e Comunicação Empresarial",
            "nucleo_id": nucleos_dict["NAE-ESTGA"],
        },
        {"name": "Terapia da Fala", "nucleo_id": nucleos_dict["NAE-ESSUA"]},
        {"name": "Tradução", "nucleo_id": nucleos_dict["NET"]},
    ]

    abreviations_set = set()
    for i in range(len(courses)):
        courses[i]["abbreviation"] = (
            "".join(
                word[0]
                for word in courses[i]["name"].replace("-", " ").split()
                if len(word) > 2
            )
            .upper()
            .strip()
        )

        if len(courses[i]["abbreviation"]) < 3:
            courses[i]["abbreviation"] = "".join(
                word[:3]
                for word in courses[i]["name"].replace("-", " ").split()
                if len(word) > 2
            ).strip()
        # Ensure uniqueness
        original_abbr = courses[i]["abbreviation"]
        counter = 1
        while courses[i]["abbreviation"] in abreviations_set:
            courses[i]["abbreviation"] = f"{original_abbr}{counter}"
            counter += 1

        abreviations_set.add(courses[i]["abbreviation"])

    print("Courses to be created:", [course["abbreviation"] for course in courses])
    resp = []
    for course in courses:
        response = requests.post(f"{API_URL}/courses", json=course)
        if response.status_code == 201:
            print(f"Created course: {course['name']}")
            resp.append(response.json())
        else:
            print(
                f"Failed to create course: {course['name']}, Status Code: {response.status_code}, Response: {response.text}"
            )

    return resp


def delete_all_courses():
    response = requests.get(f"{API_URL}/courses")
    if response.status_code != 200:
        print("Failed to fetch courses for deletion.")
        return

    courses = response.json()
    for course in courses:
        del_response = requests.delete(f"{API_URL}/courses/{course['id']}")
        if del_response.status_code == 204:
            print(f"Deleted course: {course['name']}")
        else:
            print(
                f"Failed to delete course: {course['name']}, Status Code: {del_response.status_code}, Response: {del_response.text}"
            )


def main():
    modality_types_ids = populate_modalities_types()
    print("Populated Modality Types IDs:", modality_types_ids)

    modalities = populate_modalidades(modality_types_ids)
    print("Populated Modalities:", [mod["name"] for mod in modalities])

    nucleos = populate_nucleos()
    print("Populated Nucleos:", [nucleo["name"] for nucleo in nucleos])

    delete_all_courses()
    courses = populate_courses(nucleos)
    print("Populated Courses: ", [course["abbreviation"] for course in courses])


if __name__ == "__main__":
    main()
