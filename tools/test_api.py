"""
TACA Competition API - Complete Test Script

This script demonstrates the full API workflow by:
1. Creating modalities (sports)
2. Creating courses
3. Creating students
4. Creating teams
5. Creating seasons
6. Creating tournaments
7. Creating matches
8. Registering match results
9. Viewing rankings

Run with: python test_api.py
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any
import sys

# API Configuration
API_BASE_URL = "http://localhost/api/admin"
HEADERS = {"Content-Type": "application/json"}


# Color codes for output
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_data(label: str, data: Any):
    """Print formatted data"""
    print(f"{Colors.OKBLUE}{label}:{Colors.ENDC}")
    print(json.dumps(data, indent=2, default=str))


def make_request(
    method: str, endpoint: str, data: Dict = None, params: Dict = None
) -> Dict:
    """Make HTTP request to API"""
    url = f"{API_BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, headers=HEADERS, params=params)
        elif method == "POST":
            response = requests.post(url, headers=HEADERS, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=HEADERS, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=HEADERS)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()

        if response.status_code == 204:
            return {}

        return response.json()

    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {method} {endpoint}")
        print_error(f"Error: {str(e)}")
        if hasattr(e.response, "text"):
            print_error(f"Response: {e.response.text}")
        with open("error_response.json", "w") as f:
            if hasattr(e.response, "text"):
                f.write(e.response.text)
        sys.exit(1)


class CompetitionSetup:
    """Main class to set up the competition"""

    def __init__(self):
        self.modalities = {}
        self.courses = {}
        self.students = {}
        self.teams = {}
        self.seasons = {}
        self.tournaments = {}
        self.matches = {}

    def run(self):
        """Run the complete setup"""
        print_header("TACA COMPETITION API - DEMONSTRATION SCRIPT")
        print_info("This script will create a complete competition scenario")
        print_info(f"API Base URL: {API_BASE_URL}\n")

        # Note: Some endpoints may not be implemented yet
        self.create_modalities()
        input("Press Enter to continue ...")
        self.list_modalities()
        input("Press Enter to continue ...")

        print_info(
            "\nNOTE: Courses, Seasons, Regulations, and Users endpoints are not yet"
        )
        print_info("implemented with microservices (returning dummy data).\n")

        # These will return dummy data for now
        input("Press Enter to continue ...")
        self.create_courses_placeholder()
        input("Press Enter to continue ...")
        self.create_students()
        input("Press Enter to continue ...")
        self.list_students()

        input("Press Enter to continue ...")
        self.create_teams()
        input("Press Enter to continue ...")
        self.list_teams()

        input("Press Enter to continue ...")
        self.create_seasons_placeholder()
        input("Press Enter to continue ...")
        self.create_tournaments()
        input("Press Enter to continue ...")
        self.list_tournaments()

        input("Press Enter to continue ...")
        self.create_matches()
        input("Press Enter to continue ...")
        self.list_matches()

        input("Press Enter to continue ...")
        self.register_match_results()
        input("Press Enter to continue ...")
        self.add_match_lineups()

        input("Press Enter to continue ...")
        self.finish_tournament()

        print_header("DEMONSTRATION COMPLETE")
        print_success("All API endpoints have been tested successfully!")
        print_info("\nCreated Resources Summary:")
        print(f"  • Modalities: {len(self.modalities)}")
        print(f"  • Teams: {len(self.teams)}")
        print(f"  • Tournaments: {len(self.tournaments)}")
        print(f"  • Matches: {len(self.matches)}")

    def create_modalities(self):
        """Create sports modalities"""
        print_header("1. CREATING MODALITIES (SPORTS)")

        modalities_data = [
            {
                "name": "Futebol",
                "type": "coletiva",
                "scoring_schema": {"win": 3, "draw": 1, "loss": 0},
            },
            {
                "name": "Futsal",
                "type": "coletiva",
                "scoring_schema": {"win": 3, "draw": 1, "loss": 0},
            },
            {
                "name": "Basquetebol",
                "type": "coletiva",
                "scoring_schema": {"win": 2, "loss": 0},
            },
        ]

        for modality_data in modalities_data:
            result = make_request("POST", "/modalities", modality_data)
            self.modalities[modality_data["name"]] = result
            print_success(f"Created modality: {modality_data['name']}")
            print_data("Response", result)

    def list_modalities(self):
        """List all modalities"""
        print_header("2. LISTING MODALITIES")

        result = make_request("GET", "/modalities")
        print_success(f"Retrieved {len(result)} modalities")
        print_data("Modalities", result)

    def create_courses_placeholder(self):
        """Create courses (note: not fully implemented)"""
        print_header("3. CREATING COURSES")
        print_info("NOTE: Courses endpoint not yet implemented with microservices")
        print_info("Using placeholder course IDs for demonstration\n")

        # Store placeholder course IDs
        self.courses = {
            "MECT": "00000000-0000-0000-0000-000000000001",
            "LEI": "00000000-0000-0000-0000-000000000002",
            "MIEET": "00000000-0000-0000-0000-000000000003",
        }

        for name, id in self.courses.items():
            print_info(f"Course: {name} (ID: {id})")

    def create_students(self):
        """Create students"""
        print_header("4. CREATING STUDENTS")

        students_data = [
            # MECT students
            {
                "course_id": self.courses["MECT"],
                "full_name": "João Silva",
                "student_number": "100001",
                "email": "joao@ua.pt",
                "is_member": True,
            },
            {
                "course_id": self.courses["MECT"],
                "full_name": "Maria Santos",
                "student_number": "100002",
                "email": "maria@ua.pt",
                "is_member": True,
            },
            {
                "course_id": self.courses["MECT"],
                "full_name": "Pedro Costa",
                "student_number": "100003",
                "email": "pedro@ua.pt",
                "is_member": True,
            },
            {
                "course_id": self.courses["MECT"],
                "full_name": "Ana Rodrigues",
                "student_number": "100004",
                "email": "ana@ua.pt",
                "is_member": True,
            },
            {
                "course_id": self.courses["MECT"],
                "full_name": "Carlos Ferreira",
                "student_number": "100005",
                "email": "carlos@ua.pt",
                "is_member": True,
            },
            # LEI students
            {
                "course_id": self.courses["LEI"],
                "full_name": "Sofia Oliveira",
                "student_number": "200001",
                "email": "sofia@ua.pt",
                "is_member": True,
            },
            {
                "course_id": self.courses["LEI"],
                "full_name": "Miguel Pereira",
                "student_number": "200002",
                "email": "miguel@ua.pt",
                "is_member": True,
            },
            {
                "course_id": self.courses["LEI"],
                "full_name": "Rita Alves",
                "student_number": "200003",
                "email": "rita@ua.pt",
                "is_member": True,
            },
            {
                "course_id": self.courses["LEI"],
                "full_name": "Bruno Martins",
                "student_number": "200004",
                "email": "bruno@ua.pt",
                "is_member": True,
            },
            {
                "course_id": self.courses["LEI"],
                "full_name": "Catarina Sousa",
                "student_number": "200005",
                "email": "catarina@ua.pt",
                "is_member": True,
            },
            # MIEET students
            {
                "course_id": self.courses["MIEET"],
                "full_name": "Tiago Lopes",
                "student_number": "300001",
                "email": "tiago@ua.pt",
                "is_member": True,
            },
            {
                "course_id": self.courses["MIEET"],
                "full_name": "Beatriz Gomes",
                "student_number": "300002",
                "email": "beatriz@ua.pt",
                "is_member": True,
            },
            {
                "course_id": self.courses["MIEET"],
                "full_name": "André Silva",
                "student_number": "300003",
                "email": "andre@ua.pt",
                "is_member": True,
            },
            {
                "course_id": self.courses["MIEET"],
                "full_name": "Inês Costa",
                "student_number": "300004",
                "email": "ines@ua.pt",
                "is_member": True,
            },
            {
                "course_id": self.courses["MIEET"],
                "full_name": "Rui Santos",
                "student_number": "300005",
                "email": "rui@ua.pt",
                "is_member": True,
            },
        ]

        for student_data in students_data:
            result = make_request("POST", "/students", student_data)
            self.students[student_data["student_number"]] = result
            print_success(
                f"Created student: {student_data['full_name']} ({student_data['student_number']})"
            )

    def list_students(self):
        """List students by course"""
        print_header("5. LISTING STUDENTS BY COURSE")

        for course_name, course_id in self.courses.items():
            result = make_request("GET", "/students", params={"course_id": course_id})
            print_success(f"Retrieved {len(result)} students from {course_name}")
            print_data(f"{course_name} Students", result)

    def create_teams(self):
        """Create teams for each course and modality"""
        print_header("6. CREATING TEAMS")

        # Get student IDs by course
        mect_student_ids = [s["id"] for s in list(self.students.values())[:5]]
        lei_student_ids = [s["id"] for s in list(self.students.values())[5:10]]
        mieet_student_ids = [s["id"] for s in list(self.students.values())[10:15]]

        futebol_id = self.modalities["Futebol"]["id"]
        futsal_id = self.modalities["Futsal"]["id"]
        basquete_id = self.modalities["Basquetebol"]["id"]

        teams_data = [
            # Futebol teams
            {
                "modality_id": futebol_id,
                "course_id": self.courses["MECT"],
                "name": "MECT Futebol",
                "players": mect_student_ids,
            },
            {
                "modality_id": futebol_id,
                "course_id": self.courses["LEI"],
                "name": "LEI Futebol",
                "players": lei_student_ids,
            },
            {
                "modality_id": futebol_id,
                "course_id": self.courses["MIEET"],
                "name": "MIEET Futebol",
                "players": mieet_student_ids,
            },
            # Futsal teams
            {
                "modality_id": futsal_id,
                "course_id": self.courses["MECT"],
                "name": "MECT Futsal",
                "players": mect_student_ids,
            },
            {
                "modality_id": futsal_id,
                "course_id": self.courses["LEI"],
                "name": "LEI Futsal",
                "players": lei_student_ids,
            },
            # Basquetebol teams
            {
                "modality_id": basquete_id,
                "course_id": self.courses["MECT"],
                "name": "MECT Basquete",
                "players": mect_student_ids[:5],
            },
            {
                "modality_id": basquete_id,
                "course_id": self.courses["LEI"],
                "name": "LEI Basquete",
                "players": lei_student_ids[:5],
            },
        ]

        for team_data in teams_data:
            result = make_request("POST", "/teams", team_data)
            self.teams[team_data["name"]] = result
            print_success(
                f"Created team: {team_data['name']} with {len(team_data['players'])} players"
            )

    def list_teams(self):
        """List all teams"""
        print_header("7. LISTING TEAMS")

        result = make_request("GET", "/teams")
        print_success(f"Retrieved {len(result)} teams")
        print_data("Teams", result)

    def create_seasons_placeholder(self):
        """Create seasons (note: not fully implemented)"""
        print_header("8. CREATING SEASONS")
        print_info("NOTE: Seasons endpoint not yet implemented with microservices")
        print_info("Using placeholder season ID for demonstration\n")

        # Store placeholder season ID
        self.seasons["2025"] = "00000000-0000-0000-0000-000000000010"
        print_info(f"Season: 2025 (ID: {self.seasons['2025']})")

    def create_tournaments(self):
        """Create tournaments"""
        print_header("9. CREATING TOURNAMENTS")

        futebol_id = self.modalities["Futebol"]["id"]
        futsal_id = self.modalities["Futsal"]["id"]
        basquete_id = self.modalities["Basquetebol"]["id"]
        season_id = self.seasons["2025"]

        # Get team IDs
        futebol_teams = [
            self.teams["MECT Futebol"]["id"],
            self.teams["LEI Futebol"]["id"],
            self.teams["MIEET Futebol"]["id"],
        ]
        futsal_teams = [self.teams["MECT Futsal"]["id"], self.teams["LEI Futsal"]["id"]]
        basquete_teams = [
            self.teams["MECT Basquete"]["id"],
            self.teams["LEI Basquete"]["id"],
        ]

        tournaments_data = [
            {
                "modality_id": futebol_id,
                "name": "Campeonato de Futebol 2025",
                "season_id": season_id,
                "rules": {"format": "eliminatória", "num_teams": 3},
                "teams": futebol_teams,
                "start_date": (datetime.now() + timedelta(days=7)).isoformat(),
            },
            {
                "modality_id": futsal_id,
                "name": "Campeonato de Futsal 2025",
                "season_id": season_id,
                "rules": {"format": "todos_contra_todos", "num_teams": 2},
                "teams": futsal_teams,
                "start_date": (datetime.now() + timedelta(days=14)).isoformat(),
            },
            {
                "modality_id": basquete_id,
                "name": "Campeonato de Basquetebol 2025",
                "season_id": season_id,
                "rules": {"format": "melhor_de_3", "num_teams": 2},
                "teams": basquete_teams,
                "start_date": (datetime.now() + timedelta(days=21)).isoformat(),
            },
        ]

        for tournament_data in tournaments_data:
            result = make_request("POST", "/tournaments", tournament_data)
            self.tournaments[tournament_data["name"]] = result
            print_success(f"Created tournament: {tournament_data['name']}")
            print_data("Tournament Details", result)

    def list_tournaments(self):
        """List all tournaments"""
        print_header("10. LISTING TOURNAMENTS")

        result = make_request("GET", "/tournaments")
        print_success(f"Retrieved {len(result)} tournaments")
        print_data("Tournaments", result)

    def create_matches(self):
        """Create matches for tournaments"""
        print_header("11. CREATING MATCHES")

        # Futebol tournament matches
        futebol_tournament = self.tournaments["Campeonato de Futebol 2025"]
        mect_futebol = self.teams["MECT Futebol"]["id"]
        lei_futebol = self.teams["LEI Futebol"]["id"]
        mieet_futebol = self.teams["MIEET Futebol"]["id"]

        futebol_matches = [
            {
                "tournament_id": futebol_tournament["id"],
                "team_home_id": mect_futebol,
                "team_away_id": lei_futebol,
                "location": "Campo Principal UA",
                "start_time": (
                    datetime.now() + timedelta(days=7, hours=15)
                ).isoformat(),
            },
            {
                "tournament_id": futebol_tournament["id"],
                "team_home_id": lei_futebol,
                "team_away_id": mieet_futebol,
                "location": "Campo Principal UA",
                "start_time": (
                    datetime.now() + timedelta(days=8, hours=15)
                ).isoformat(),
            },
            {
                "tournament_id": futebol_tournament["id"],
                "team_home_id": mect_futebol,
                "team_away_id": mieet_futebol,
                "location": "Campo Principal UA",
                "start_time": (
                    datetime.now() + timedelta(days=9, hours=15)
                ).isoformat(),
            },
        ]

        # Futsal tournament matches
        futsal_tournament = self.tournaments["Campeonato de Futsal 2025"]
        mect_futsal = self.teams["MECT Futsal"]["id"]
        lei_futsal = self.teams["LEI Futsal"]["id"]

        futsal_matches = [
            {
                "tournament_id": futsal_tournament["id"],
                "team_home_id": mect_futsal,
                "team_away_id": lei_futsal,
                "location": "Pavilhão Gimnodesportivo",
                "start_time": (
                    datetime.now() + timedelta(days=14, hours=18)
                ).isoformat(),
            },
            {
                "tournament_id": futsal_tournament["id"],
                "team_home_id": lei_futsal,
                "team_away_id": mect_futsal,
                "location": "Pavilhão Gimnodesportivo",
                "start_time": (
                    datetime.now() + timedelta(days=15, hours=18)
                ).isoformat(),
            },
        ]

        all_matches = futebol_matches + futsal_matches

        for i, match_data in enumerate(all_matches):
            result = make_request("POST", "/matches", match_data)
            self.matches[f"match_{i+1}"] = result
            print_success(f"Created match #{i+1}")
            print_data("Match Details", result)

    def list_matches(self):
        """List all matches"""
        print_header("12. LISTING MATCHES")

        result = make_request("GET", "/matches")
        print_success(f"Retrieved {len(result)} matches")
        print_data("Matches", result)

    def register_match_results(self):
        """Register results for some matches"""
        print_header("13. REGISTERING MATCH RESULTS")

        # Register results for the first 2 matches
        matches_to_complete = list(self.matches.values())[:2]

        results = [
            {"home_score": 3, "away_score": 1},
            {"home_score": 2, "away_score": 2},
        ]

        for match, result_data in zip(matches_to_complete, results):
            result = make_request("POST", f"/matches/{match['id']}/result", result_data)
            print_success(
                f"Registered result: {result_data['home_score']} - {result_data['away_score']}"
            )
            print_data("Updated Match", result)

    def add_match_lineups(self):
        """Add player lineups to matches"""
        print_header("14. ADDING MATCH LINEUPS")

        # Add lineup for first match
        first_match = list(self.matches.values())[0]

        # Get first 5 students for lineup (simplified)
        student_ids = list(self.students.values())[:5]

        lineup_data = {
            "team_id": first_match["team_home_id"],
            "players": [
                {
                    "player_id": student_ids[0]["id"],
                    "jersey_number": 7,
                    "is_starter": True,
                },
                {
                    "player_id": student_ids[1]["id"],
                    "jersey_number": 10,
                    "is_starter": True,
                },
                {
                    "player_id": student_ids[2]["id"],
                    "jersey_number": 9,
                    "is_starter": True,
                },
                {
                    "player_id": student_ids[3]["id"],
                    "jersey_number": 11,
                    "is_starter": False,
                },
                {
                    "player_id": student_ids[4]["id"],
                    "jersey_number": 8,
                    "is_starter": False,
                },
            ],
        }

        result = make_request(
            "POST", f"/matches/{first_match['id']}/lineup", lineup_data
        )
        print_success("Added lineup for home team")
        print_data("Lineup Result", result)

    def finish_tournament(self):
        """Finish a tournament"""
        print_header("15. FINISHING TOURNAMENT")

        # Finish the futsal tournament
        futsal_tournament = self.tournaments["Campeonato de Futsal 2025"]

        result = make_request("POST", f"/tournaments/{futsal_tournament['id']}/finish")
        print_success(f"Finished tournament: {futsal_tournament['name']}")
        print_data("Final Tournament State", result)


def main():
    """Main entry point"""
    try:
        setup = CompetitionSetup()
        setup.run()
    except KeyboardInterrupt:
        print_error("\n\nScript interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
