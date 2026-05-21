import json
import os
from dataclasses import dataclass
from typing import List, Optional

current_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(current_dir, "step3-final-data/processed_data.json"), "rb") as f:
    processed_data = json.load(f)

if not processed_data:
    raise ValueError(
        "Processed data is empty. Please run the script to generate the processed_data.json file."
    )


@dataclass
class Match:
    jornada: int
    day: str
    hour: str
    local: str
    team1: str
    team2: str
    team1_score: Optional[int]
    team2_score: Optional[int]


@dataclass
class Tournament:
    name: str
    teams: List[str]
    matches: List[Match]
    format: str
    format_data: dict

    def __post_init__(self):
        self.matches = [
            Match(
                jornada=match["joranada"],
                day=match["day"],
                hour=match["hour"],
                local=match["local"],
                team1=match["team1"],
                team2=match["team2"],
                team1_score=match["team1_score"],
                team2_score=match["team2_score"],
            )
            for match in self.matches
        ]


@dataclass
class Modality:
    name: str
    teams: List[str]
    tournaments: List[Tournament]

    def __post_init__(self):
        self.tournaments = [
            Tournament(
                name=tournament["name"],
                teams=tournament["teams"],
                matches=tournament["matches"],
                format=tournament["format"],
                format_data=tournament["format_data"],
            )
            for tournament in self.tournaments
        ]


processed_data_typed = [
    Modality(**{**processed_data[modality], "name": modality})
    for modality in processed_data
]
