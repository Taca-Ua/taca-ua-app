import requests

API_URL = "http://localhost/api/admin"


def populate_modalities_types():
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

    ids = []
    for modality_type in modalities_types:
        response = requests.post(f"{API_URL}/modality-types", json=modality_type)
        if response.status_code == 201:
            print(f"Created modality type: {modality_type['name']}")
            ids.append(response.json().get("id", None))
        else:
            print(
                f"Failed to create modality type: {modality_type['name']}, Status Code: {response.status_code}, Response: {response.text}"
            )

    return ids


def main():
    modality_types_ids = populate_modalities_types()
    print("Populated Modality Types IDs:", modality_types_ids)


if __name__ == "__main__":
    main()
