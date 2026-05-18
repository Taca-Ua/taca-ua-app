from typing import List

import requests

API_URL = "http://localhost/api2/admin"

HEADERS = {
    "X-Dev-Auth-Token": "super-secret-dev-token",
}

STATS = {
    "modalities_types": {"created": 0, "failed": 0, "skipped": 0},
    "nucleos": {"created": 0, "failed": 0, "skipped": 0},
    "courses": {"created": 0, "failed": 0, "skipped": 0},
    "modalities": {"created": 0, "failed": 0, "skipped": 0},
    "teams": {"created": 0, "failed": 0, "skipped": 0},
    "tournaments": {"created": 0, "failed": 0, "skipped": 0},
    "tournament_team_associations": {"created": 0, "failed": 0, "skipped": 0},
    "matches": {"created": 0, "failed": 0, "skipped": 0},
    "match_results": {"created": 0, "failed": 0, "skipped": 0},
}


def populate_modalities_types(step_by_step=False, delete_existing=False) -> int:
    global STATS

    check = requests.get(f"{API_URL}/modality-types", headers=HEADERS)
    if delete_existing and check.status_code == 200:
        for modality_type in check.json():
            del_response = requests.delete(
                f"{API_URL}/modality-types/{modality_type['id']}/", headers=HEADERS
            )
            if del_response.status_code == 204:
                print(f"Deleted modality type: {modality_type['name']}")
            else:
                print(
                    f"Failed to delete modality type: {modality_type['name']}, Status Code: {del_response.status_code}, Response: {del_response.text}"
                )
                raise Exception("Failed to delete modality types.")
    if check.status_code != 200:
        print(
            f"Failed to fetch modality types, Status Code: {check.status_code}, Response: {check.text}"
        )
        raise Exception("Failed to fetch modality types.")

    existing_modality_types = {mt["name"]: mt["id"] for mt in check.json()}

    modalities_types = [
        {
            "name": "Modalidades Coletivas Recorrentes",
            "description": "Modalidades coletivas que ocorrem de forma recorrente ao longo da época desportiva.",
            "tournament_competitor_type": "team",
            "is_playoff": False,
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
            "tournament_competitor_type": "team",
            "is_playoff": False,
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
            "tournament_competitor_type": "team",
            "is_playoff": False,
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
            "tournament_competitor_type": "individual",
            "is_playoff": False,
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
            "tournament_competitor_type": "team",
            "is_playoff": False,
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
            "is_playoff": True,
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
        if modality_type["name"] in existing_modality_types:
            print(f"Modality type already exists: {modality_type['name']}")
            STATS["modalities_types"]["skipped"] = (
                STATS["modalities_types"]["skipped"] + 1
            )
            ids[modality_type["name"]] = existing_modality_types[modality_type["name"]]
            continue

        if step_by_step:
            input(
                f"About to create modality type: {modality_type['name']}. Press Enter to continue..."
            )
        response = requests.post(
            f"{API_URL}/modality-types/", json=modality_type, headers=HEADERS
        )
        if response.status_code == 201:
            print(f"Created modality type: {modality_type['name']}")
            ids[modality_type["name"]] = response.json().get("id", None)
            STATS["modalities_types"]["created"] = (
                STATS["modalities_types"]["created"] + 1
            )
        else:
            print(
                f"Failed to create modality type: {modality_type['name']}, Status Code: {response.status_code}, Response: {response.text}"
            )
            STATS["modalities_types"]["failed"] = (
                STATS["modalities_types"]["failed"] + 1
            )
            raise Exception("Failed to populate modality types.")

    return len(ids)


def populate_courses():
    """Populate the database with courses and their corresponding núcleos based on the provided configuration."""
    global STATS

    # get existing nucleos to avoid redundant API calls
    current_nucleos = requests.get(f"{API_URL}/nucleos/", headers=HEADERS)
    if current_nucleos.status_code == 200:
        existing_nucleos = {
            nucleo["name"]: nucleo["id"] for nucleo in current_nucleos.json()
        }
    else:
        existing_nucleos = {}

    # get existing courses to avoid redundant API calls
    current_courses = requests.get(f"{API_URL}/courses/", headers=HEADERS)
    if current_courses.status_code == 200:
        existing_courses = {
            course["abbreviation"]: course["id"] for course in current_courses.json()
        }
    else:
        existing_courses = {}

    def _create_nucleo(name: str) -> str:
        """Helper function to create a núcleo if it doesn't exist and return its ID."""

        # Check if the núcleo already exists before attempting to create it
        if name in existing_nucleos:
            print(f"Núcleo already exists: {name}")
            STATS["nucleos"]["skipped"] = STATS["nucleos"]["skipped"] + 1
            return existing_nucleos[name]

        # If the núcleo doesn't exist, create it
        response = requests.post(
            f"{API_URL}/nucleos/",
            json={"name": name, "abbreviation": name},
            headers=HEADERS,
        )
        if response.status_code == 201:
            print(f"Created núcleo: {name}")
            return response.json().get("id", None)
        else:
            print(
                f"Failed to create núcleo: {name}, Status Code: {response.status_code}, Response: {response.text}"
            )
            STATS["nucleos"]["failed"] = STATS["nucleos"]["failed"] + 1
            return None

    def _create_course(
        course_name: str, course_abbreviation: str, nucleo_id: str
    ) -> str:
        """Helper function to create a course under a given núcleo."""
        if course_abbreviation in existing_courses:
            print(f"Course already exists: {course_name} ({course_abbreviation})")
            return existing_courses[course_abbreviation]

        course_payload = {
            "name": course_name,
            "abbreviation": course_abbreviation,
            "nucleo_id": nucleo_id,
        }
        response = requests.post(
            f"{API_URL}/courses/", json=course_payload, headers=HEADERS
        )

        if response.status_code == 201:
            print(f"Created course: {course_name} ({course_abbreviation})")
            return response.json().get("id", None)
        else:
            print(
                f"Failed to create course: {course_name} ({course_abbreviation}), Status Code: {response.status_code}, Response: {response.text}"
            )
            return None

    # Iterate through the provided courses data and create núcleos and courses accordingly
    from data.config_cursos_revised import courses_data

    nucleos_created = courses_created = 0
    for nucleo_name, courses in courses_data.items():
        # First, ensure the núcleo exists and get its ID
        nucleo_id = _create_nucleo(nucleo_name)
        if not nucleo_id:
            print(
                f"Skipping courses for núcleo: {nucleo_name} due to núcleo creation failure."
            )
            continue
        if nucleo_name not in existing_nucleos:
            nucleos_created += 1

        for course in courses:
            print("\t", flush=True, end="")  # Add indentation for course creation logs
            course_res = _create_course(
                course["displayName"], course["shortName"], nucleo_id
            )
            if course_res and course_res != existing_courses.get(course["shortName"]):
                courses_created += 1

    STATS["nucleos"]["created"] = nucleos_created
    STATS["courses"]["created"] = courses_created
    return nucleos_created, courses_created


def give_admin_permissions():
    """Give admin permissions to the user associated with the provided dev token."""
    response = requests.get(f"{API_URL}/admins/", headers=HEADERS)
    if response.status_code == 200:
        nucleo_admin = None
        for admin in response.json():
            if admin.get("username") == "admin_nucleo":
                nucleo_admin = admin
                break

        if not nucleo_admin:
            print("No admin user found with username 'admin_nucleo'.")
            return
    else:
        print(
            f"Failed to grant admin permissions, Status Code: {response.status_code}, Response: {response.text}"
        )
        return

    # get nucleos
    nucleos_response = requests.get(f"{API_URL}/nucleos/", headers=HEADERS)
    if nucleos_response.status_code != 200:
        print(
            f"Failed to fetch nucleos, Status Code: {nucleos_response.status_code}, Response: {nucleos_response.text}"
        )
        raise Exception("Failed to fetch nucleos.")

    nucleos = {nucleo["name"]: nucleo["id"] for nucleo in nucleos_response.json()}
    requests.put(
        f"{API_URL}/admins/{nucleo_admin['id']}/",
        json={"nucleos": list(nucleos.values())},
        headers=HEADERS,
    )
    if response.status_code == 200:
        print(
            f"Granted admin permissions to user 'admin_nucleo' for nucleos: {', '.join(nucleos.keys())}"
        )
    else:
        print(
            f"Failed to grant admin permissions, Status Code: {response.status_code}, Response: {response.text}"
        )


def populate_modalities():
    """Populate the database with modalities."""
    global STATS

    # get modality types to map modality type names to IDs
    modality_types_response = requests.get(
        f"{API_URL}/modality-types/", headers=HEADERS
    )
    if modality_types_response.status_code != 200:
        print(
            f"Failed to fetch modality types, Status Code: {modality_types_response.status_code}, Response: {modality_types_response.text}"
        )
        return 0
    modality_type_name_to_id = {
        mt["name"]: mt["id"] for mt in modality_types_response.json()
    }

    # check existing modalities to avoid duplicates
    existing_modalities_response = requests.get(
        f"{API_URL}/modalities/", headers=HEADERS
    )
    if existing_modalities_response.status_code == 200:
        existing_modalities = {
            m["name"]: m["id"] for m in existing_modalities_response.json()
        }
    else:
        print(
            f"Failed to fetch existing modalities, Status Code: {existing_modalities_response.status_code}, Response: {existing_modalities_response.text}"
        )
        existing_modalities = {}

    # Iterate through the modalities in the processed data and create them if they don't already exist
    from data.processed_data import processed_data_typed

    modalities_created = 0
    for modality in processed_data_typed:
        if modality.name in existing_modalities:
            print(f"Modality already exists: {modality.name}")
            STATS["modalities"]["skipped"] = STATS["modalities"]["skipped"] + 1
            continue

        payload = {
            "name": modality.name,
            "modality_type_id": modality_type_name_to_id.get(
                "Modalidades Coletivas Recorrentes"
            ),
        }
        response = requests.post(
            f"{API_URL}/modalities/", json=payload, headers=HEADERS
        )
        if response.status_code == 201:
            print(f"Created modality: {modality.name}")
            modalities_created += 1
        else:
            print(
                f"Failed to create modality: {modality.name}, Status Code: {response.status_code}, Response: {response.text}"
            )
            STATS["modalities"]["failed"] = STATS["modalities"]["failed"] + 1

    STATS["modalities"]["created"] = modalities_created
    return modalities_created


def populate_teams():
    """Populate the database with teams."""
    global STATS

    # get modalities to map modality names to IDs
    current_modalities = requests.get(f"{API_URL}/modalities/", headers=HEADERS)
    if current_modalities.status_code == 200:
        modality_name_to_id = {
            modality["name"]: modality["id"] for modality in current_modalities.json()
        }
    else:
        print(
            f"Failed to fetch modalities, Status Code: {current_modalities.status_code}, Response: {current_modalities.text}"
        )
        return 0

    # get courses to map course names to IDs
    current_courses = requests.get(f"{API_URL}/courses/", headers=HEADERS)
    if current_courses.status_code == 200:
        course_name_to_id = {
            course["name"]: course["id"] for course in current_courses.json()
        }
    else:
        print(
            f"Failed to fetch courses, Status Code: {current_courses.status_code}, Response: {current_courses.text}"
        )
        return 0

    # get existing teams to avoid duplicates
    existing_teams_response = requests.get(f"{API_URL}/teams/", headers=HEADERS)
    if existing_teams_response.status_code == 200:
        existing_teams = {
            (team["name"], team["modality"]["id"], team["course"]["id"]): team["id"]
            for team in existing_teams_response.json()
        }
    else:
        print(
            f"Failed to fetch existing teams, Status Code: {existing_teams_response.status_code}, Response: {existing_teams_response.text}"
        )
        existing_teams = {}

    from data.processed_data import processed_data_typed

    teams_created = 0
    create_team_payloads = []
    for modality in processed_data_typed:
        if modality.name not in modality_name_to_id:
            print(
                f"Modality not found for teams: {modality.name}. Skipping team creation for this modality."
            )
            continue

        print(f"Processing teams for modality: {modality.name}")
        for team in modality.teams:
            print("\t", flush=True, end="")  # Add indentation for team creation logs
            if (
                team,
                modality_name_to_id.get(modality.name),
                course_name_to_id.get(team),
            ) in existing_teams:
                print(f"Team already exists: {team}")
                STATS["teams"]["skipped"] = STATS["teams"]["skipped"] + 1
                continue

            if team not in course_name_to_id:
                print(f"Course not found for team: {team}. Skipping team creation.")
                STATS["teams"]["skipped"] = STATS["teams"]["skipped"] + 1
                continue

            team_payload = {
                "name": team,
                "modality_id": modality_name_to_id.get(modality.name),
                "course_id": course_name_to_id.get(team),
            }
            response = requests.post(
                f"{API_URL}/teams/", json=team_payload, headers=HEADERS
            )
            if response.status_code == 201:
                print(f"Created team: {team}")
                teams_created += 1
                create_team_payloads.append(team_payload)
            else:
                print(
                    f"Failed to create team: {team}, Status Code: {response.status_code}, Response: {response.text}"
                )
                STATS["teams"]["failed"] = STATS["teams"]["failed"] + 1

        # Delete teams that exist in the database but are not present in the processed data for the modality
        for existing_team_key in existing_teams:
            existing_team_name, existing_team_modality_id, existing_team_course_id = (
                existing_team_key
            )
            if (
                existing_team_modality_id == modality_name_to_id.get(modality.name)
                and existing_team_course_id in course_name_to_id.values()
                and existing_team_name not in modality.teams
            ):
                del_response = requests.delete(
                    f"{API_URL}/teams/{existing_teams[existing_team_key]}/",
                    headers=HEADERS,
                )
                if del_response.status_code == 204:
                    print(f"Deleted team: {existing_team_name}")
                else:
                    print(
                        f"Failed to delete team: {existing_team_name}, Status Code: {del_response.status_code}, Response: {del_response.text}"
                    )
                    STATS["teams"]["failed"] = STATS["teams"]["failed"] + 1

    STATS["teams"]["created"] = teams_created
    return teams_created


def populate_tournaments():
    """Populate the database with tournaments."""
    global STATS

    from data.processed_data import Match

    # get modalities to map modality names to IDs
    current_modalities = requests.get(f"{API_URL}/modalities/", headers=HEADERS)
    if current_modalities.status_code == 200:
        modality_name_to_id = {
            modality["name"]: modality["id"] for modality in current_modalities.json()
        }
    else:
        print(
            f"Failed to fetch modalities, Status Code: {current_modalities.status_code}, Response: {current_modalities.text}"
        )
        return 0

    # get existing tournaments to avoid duplicates
    existing_tournaments_response = requests.get(
        f"{API_URL}/tournaments/", headers=HEADERS
    )
    if existing_tournaments_response.status_code == 200:
        existing_tournaments = {
            tournament["name"]: tournament["id"]
            for tournament in existing_tournaments_response.json()
        }
    else:
        print(
            f"Failed to fetch existing tournaments, Status Code: {existing_tournaments_response.status_code}, Response: {existing_tournaments_response.text}"
        )
        existing_tournaments = {}

    def _create_tournament(tournament_name: str, modality_id: int) -> str:
        if tournament_name in existing_tournaments:
            print(f"Tournament already exists: {tournament_name}")
            return existing_tournaments[tournament_name]

        payload = {
            "name": tournament_name,
            "modality_id": modality_id,
            "is_playoff": False,
        }
        response = requests.post(
            f"{API_URL}/tournaments/", json=payload, headers=HEADERS
        )
        if response.status_code == 201:
            print(f"Created tournament: {tournament_name}")
            STATS["tournaments"]["created"] = STATS["tournaments"]["created"] + 1
            return response.json().get("id", None)
        else:
            print(
                f"Failed to create tournament: {tournament_name}, Status Code: {response.status_code}, Response: {response.text}"
            )
            STATS["tournaments"]["failed"] = STATS["tournaments"]["failed"] + 1
            return None

    def _associate_team_to_tournament(team_id: str, tournament_id: str) -> str:
        if team_id is None:
            print(
                f"Invalid team ID: {team_id}. Skipping association to tournament ID {tournament_id}."
            )
            return None

        payload = {
            "competitor_type": "team",
            "entity_id": team_id,
        }
        response = requests.put(
            f"{API_URL}/tournaments/{tournament_id}/competitors/add/",
            json=[payload],
            headers=HEADERS,
        )

        if response.status_code == 200:
            print(f"Associated team ID {team_id} to tournament ID {tournament_id}")
            STATS["tournament_team_associations"]["created"] = (
                STATS["tournament_team_associations"]["created"] + 1
            )
            return response.json().get("id", None)
        else:
            print(
                f"Failed to associate team ID {team_id} to tournament ID {tournament_id}, Status Code: {response.status_code}, Response: {response.text}"
            )
            STATS["tournament_team_associations"]["failed"] = (
                STATS["tournament_team_associations"]["failed"] + 1
            )
            return None

    def _create_matches_for_tournament(
        tournament_id: str, matches: List[Match]
    ) -> bool:
        # get registered teams for the tournament map team IDs to avoid redundant associations and to validate match team IDs
        tournament_teams_response = requests.get(
            f"{API_URL}/tournaments/{tournament_id}/", headers=HEADERS
        )
        if tournament_teams_response.status_code == 200:
            tournament_teams = {
                competitor["name"]: competitor["id"]
                for competitor in tournament_teams_response.json()["competitors"]
            }
        else:
            print(
                f"Failed to fetch teams for tournament ID {tournament_id}, Status Code: {tournament_teams_response.status_code}, Response: {tournament_teams_response.text}"
            )
            tournament_teams = {}

        # get existing matches for the tournament to avoid duplicates
        existing_matches_response = requests.get(
            f"{API_URL}/matches/?tournament_id={tournament_id}", headers=HEADERS
        )
        if existing_matches_response.status_code == 200:
            existing_matches = {
                tuple(
                    [
                        *sorted(
                            [
                                match["participants"][0]["name"],
                                match["participants"][1]["name"],
                            ]
                        ),
                        match["start_time"],
                        match["location"],
                    ]
                ): match["id"]
                for match in existing_matches_response.json()
            }
        else:
            print(
                f"Failed to fetch existing matches for tournament ID {tournament_id}, Status Code: {existing_matches_response.status_code}, Response: {existing_matches_response.text}"
            )
            existing_matches = {}

        atleast_one_match = False
        for match in matches:
            # create match
            print("\t\t", flush=True, end="")  # Add indentation for match creation logs
            if match.day == "":
                iso_time = "2026-01-01T00:00:00+00:00"  # Default to midnight if no day is provided
            else:
                hour_formatted = match.hour.lower().split("h")[0].zfill(2)
                minute_formatted = (
                    match.hour.lower().split("h")[1].zfill(2)
                    if "h" in match.hour.lower()
                    else "00"
                )
                iso_time = (
                    f"{match.day.split()[0]}T"
                    + f"{hour_formatted}:{minute_formatted}"
                    + ":00+00:00"
                )
            local = match.local if match.local else "TBD"

            if (match.team1 not in tournament_teams) or (
                match.team2 not in tournament_teams
            ):
                print(
                    f"One or both teams for the match between {match.team1} and {match.team2} are not registered in tournament ID {tournament_id}. Skipping match creation."
                )
                STATS["matches"]["skipped"] = STATS["matches"]["skipped"] + 1
                continue

            if (
                tuple([*sorted([match.team1, match.team2]), iso_time, local])
                in existing_matches
            ):
                print("Match already exists. Skipping match creation.")
                atleast_one_match = True
                STATS["matches"]["skipped"] = STATS["matches"]["skipped"] + 1
                continue

            payload = {
                "tournament_id": tournament_id,
                "location": local,
                "start_time": iso_time,
                "participants": [
                    tournament_teams.get(match.team1),
                    tournament_teams.get(match.team2),
                ],
            }
            response = requests.post(
                f"{API_URL}/matches/", json=payload, headers=HEADERS
            )

            if response.status_code == 201:
                response_data = response.json()
                print(
                    f"Created match between {response_data['participants'][0]['name']} and team {response_data['participants'][1]['name']}"
                )
                atleast_one_match = True
                STATS["matches"]["created"] = STATS["matches"]["created"] + 1
            else:
                print(
                    f"Failed to create match for tournament ID {tournament_id}, Status Code: {response.status_code}, Response: {response.text}"
                )
                STATS["matches"]["failed"] = STATS["matches"]["failed"] + 1
        return atleast_one_match

    def _insert_matches_results(tournament_id: str, matches: List[Match]) -> None:
        # get matches for the tournament to map match IDs and validate match existence before inserting results
        matches_response = requests.get(
            f"{API_URL}/matches/?tournament_id={tournament_id}", headers=HEADERS
        )
        if matches_response.status_code == 200:
            tournament_matches = {
                tuple(
                    [
                        *sorted(
                            [
                                match["participants"][0]["name"],
                                match["participants"][1]["name"],
                            ]
                        ),
                        match["start_time"],
                        match["location"],
                    ]
                ): match
                for match in matches_response.json()
            }
        else:
            print(
                f"Failed to fetch matches for tournament ID {tournament_id}, Status Code: {matches_response.status_code}, Response: {matches_response.text}"
            )
            tournament_matches = {}

        for match in matches:
            print(
                "\t\t", flush=True, end=""
            )  # Add indentation for match result insertion logs
            if match.team1_score is None or match.team2_score is None:
                print(
                    f"Match result not provided for match between {match.team1} and {match.team2}. Skipping result insertion."
                )
                STATS["match_results"]["skipped"] = (
                    STATS["match_results"]["skipped"] + 1
                )
                continue

            if match.day == "":
                iso_time = "2026-01-01T00:00:00+00:00"  # Default to midnight if no day is provided
            else:
                iso_time = (
                    f"{match.day.split()[0]}T{match.hour.replace('h', ':')}:00+00:00"
                )
            local = match.local if match.local else "TBD"

            if (
                tuple([*sorted([match.team1, match.team2]), iso_time, local])
                not in tournament_matches
            ):
                print(
                    f"Match between {match.team1} and {match.team2} not found in tournament ID {tournament_id}. Skipping result insertion."
                )
                STATS["match_results"]["skipped"] = (
                    STATS["match_results"]["skipped"] + 1
                )
                continue

            tournament_match = tournament_matches.get(
                tuple([*sorted([match.team1, match.team2]), iso_time, local])
            )

            if tournament_match.get("status") == "finished":
                print(
                    f"Match between {match.team1} and {match.team2} already has results. Skipping result insertion."
                )
                STATS["match_results"]["skipped"] = (
                    STATS["match_results"]["skipped"] + 1
                )
                continue

            participants_mapper = {
                tournament_match["participants"][0]["name"]: tournament_match[
                    "participants"
                ][0]["id"],
                tournament_match["participants"][1]["name"]: tournament_match[
                    "participants"
                ][1]["id"],
            }
            payload = {
                "participant_results": [
                    {
                        "participant_id": participants_mapper.get(match.team1),
                        "score": match.team1_score,
                    },
                    {
                        "participant_id": participants_mapper.get(match.team2),
                        "score": match.team2_score,
                    },
                ],
                "status": "finished",
            }
            response = requests.post(
                f"{API_URL}/matches/{tournament_match['id']}/results/",
                json=payload,
                headers=HEADERS,
            )

            if response.status_code == 200:
                print(
                    f"Inserted result for match between {match.team1} and {match.team2}"
                )
                STATS["match_results"]["created"] = (
                    STATS["match_results"]["created"] + 1
                )
            else:
                print(
                    f"Failed to insert result for match between {match.team1} and {match.team2}, Status Code: {response.status_code}, Response: {response.text}"
                )
                STATS["match_results"]["failed"] = STATS["match_results"]["failed"] + 1

    from data.processed_data import processed_data_typed

    for modality in processed_data_typed:
        if modality.name not in modality_name_to_id:
            print(
                f"Modality not found for tournaments: {modality.name}. Skipping tournament creation for this modality."
            )
            continue

        # get teams for the modality to associate them with the tournaments
        teams_response = requests.get(
            f"{API_URL}/teams/?modality_id={modality_name_to_id.get(modality.name)}",
            headers=HEADERS,
        )
        if teams_response.status_code != 200:
            print(f"Failed to fetch teams for modality: {modality.name}")
            continue
        relevant_teams = {team["name"]: team["id"] for team in teams_response.json()}

        for tournament in modality.tournaments:
            # create tournament and get its ID for team association and match creation
            tournament_id = _create_tournament(
                tournament.name, modality_name_to_id.get(modality.name)
            )
            if not tournament_id:
                print(
                    f"Skipping team association and match creation for tournament: {tournament.name} due to tournament creation failure."
                )
                continue

            # get teams for the tournament to avoid redundant associations
            tournament_teams_response = requests.get(
                f"{API_URL}/tournaments/{tournament_id}/", headers=HEADERS
            )
            if tournament_teams_response.status_code == 200:
                tournament_teams = {
                    competitor["name"]: competitor["id"]
                    for competitor in tournament_teams_response.json()["competitors"]
                }
            else:
                print(f"Failed to fetch teams for tournament: {tournament.name}")
                tournament_teams = {}

            for team in tournament.teams:
                print(
                    "\t", flush=True, end=""
                )  # Add indentation for tournament creation logs
                if team in tournament_teams:
                    print(
                        f"Team already associated with tournament: {team} in {tournament.name}"
                    )
                    continue

                _associate_team_to_tournament(relevant_teams.get(team), tournament_id)

            # create matches for the tournament
            atleast_one_match = _create_matches_for_tournament(
                tournament_id, tournament.matches
            )

            # insert matches results
            _insert_matches_results(tournament_id, tournament.matches)

            # activate tournament if at least one match was created and results were inserted
            if atleast_one_match:
                activate_response = requests.put(
                    f"{API_URL}/tournaments/{tournament_id}/",
                    json={"status": "active"},
                    headers=HEADERS,
                )
                if activate_response.status_code == 200:
                    print(f"\tActivated tournament: {tournament.name}")
                else:
                    print(
                        f"\tFailed to activate tournament: {tournament.name}, Status Code: {activate_response.status_code}, Response: {activate_response.text}"
                    )


def main():
    from scraper import main as information_stealer

    print("Extracting information from the source...")
    try:
        information_stealer()
    except Exception as e:
        print(f"Error occurred while extracting information: {e}")
        return
    print("Information extracted and processed successfully.")

    print()
    input("Press Enter to continue to populate modality types...")
    modality_types_ids = populate_modalities_types(
        step_by_step=False, delete_existing=False
    )
    print("Created modality types:", modality_types_ids)

    print()
    input("Press Enter to continue to populate courses...")
    print("Populating courses and núcleos...")
    nucleos_created, courses_created = populate_courses()
    print(f"Created nucleos: {nucleos_created}, Created courses: {courses_created}")

    print(
        "\nGranting admin permissions to the user associated with the provided dev token..."
    )
    give_admin_permissions()

    print()
    input("Press Enter to continue to populate modalities...")
    print("Populating modalities...")
    modalities_created = populate_modalities()
    print(f"Created modalities: {modalities_created}")

    print()
    input("Press Enter to continue to populate teams...")
    print("Populating teams...")
    teams_created = populate_teams()
    print(f"Created teams: {teams_created}")

    print()
    input("Press Enter to continue to populate tournaments...")
    print("Populating tournaments...")
    populate_tournaments()

    print("\nPopulation completed. Summary of operations:")
    for category, stats in STATS.items():
        print(f"  {category.capitalize()}:")
        for action, count in stats.items():
            print(f"    {action.replace('_', ' ').title()}: {count}")


if __name__ == "__main__":
    main()
