import csv
import json
import os
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import pandas as pd
import requests as httpx

current_dir = os.path.dirname(os.path.abspath(__file__))


def step1(year: str = "25_26") -> bool:
    """Baixar os arquivos CSV de classificação, detalhe e elo para cada modalidade esportiva e salvar localmente."""

    """
    const modalidades = [
        { value: 'ANDEBOL MISTO', label: t('ANDEBOL_MISTO') },
        { value: 'BASQUETEBOL FEMININO', label: t('BASQUETEBOL_FEMININO') },
        { value: 'BASQUETEBOL MASCULINO', label: t('BASQUETEBOL_MASCULINO') },
        { value: 'FUTEBOL DE 7 MASCULINO', label: t('FUTEBOL_DE_7_MASCULINO') },
        { value: 'FUTSAL FEMININO', label: t('FUTSAL_FEMININO') },
        { value: 'FUTSAL MASCULINO', label: t('FUTSAL_MASCULINO') },
        { value: 'VOLEIBOL FEMININO', label: t('VOLEIBOL_FEMININO') },
        { value: 'VOLEIBOL MASCULINO', label: t('VOLEIBOL_MASCULINO') }
    ];

    const classificacaoPath = `output/elo_ratings/classificacao_${mod}.csv`;
    const detalhePath = `output/elo_ratings/detalhe_${mod}.csv`;
    const eloPath = `output/elo_ratings/elo_${mod}.csv`;

    https://slicf.github.io/mmr_ta-aua/output/elo_ratings/classificacao_ANDEBOL MISTO_25_26.csv
    https://slicf.github.io/mmr_ta-aua/output/elo_ratings/classificacao_ANDEBOL%20MISTO_25_26.csv
    """

    mods = [
        "ANDEBOL MISTO",
        "BASQUETEBOL FEMININO",
        "BASQUETEBOL MASCULINO",
        "FUTEBOL DE 7 MASCULINO",
        "FUTSAL FEMININO",
        "FUTSAL MASCULINO",
        "VOLEIBOL FEMININO",
        "VOLEIBOL MASCULINO",
    ]
    base_url = "https://slicf.github.io/mmr_ta-aua/"

    output_dir = os.path.join(current_dir, "data/step1-raw-data/")
    os.makedirs(output_dir, exist_ok=True)

    if all(
        os.path.exists(f"{output_dir}/{mod}/detalhe.csv") for mod in mods
    ) and os.path.exists(f"{output_dir}/config_cursos.json"):
        user_input = input(
            "Arquivos já existem localmente. Deseja baixá-los novamente? [s/N]: "
        )
        if user_input.lower() != "s":
            return True

    # download cursos configuration file1
    with open(f"{output_dir}/config_cursos.json", "wb+") as f:
        # https://slicf.github.io/mmr_ta-aua/config/config_cursos.json
        full_url = f"{base_url}config/config_cursos.json"
        resp = httpx.get(full_url)
        if resp.status_code == 200:
            f.write(resp.content)
            print("Arquivo config_cursos.json baixado com sucesso!")
        else:
            print(f"Erro ao baixar config_cursos.json: {resp.status_code}")
            return False

    # download detalhe.csv for each modality
    for mod in mods:
        os.makedirs(f"{output_dir}/{mod}/", exist_ok=True)

        with open(f"{output_dir}/{mod}/detalhe.csv", "wb+") as f:
            full_url = f"{base_url}output/csv_modalidades/{mod}_{year}.csv"
            resp = httpx.get(full_url)
            if resp.status_code == 200:
                f.write(resp.content)
                print(f"Arquivo detalhe.csv para {mod} baixado com sucesso!")
            else:
                print(f"Erro ao baixar detalhe.csv para {mod}: {resp.status_code}")
                return False

        with open(f"{output_dir}/{mod}/classificacao.csv", "wb+") as f:
            full_url = f"{base_url}output/elo_ratings/classificacao_{mod}_{year}.csv"
            resp = httpx.get(full_url)
            if resp.status_code == 200:
                f.write(resp.content)
                print(f"Arquivo classificacao.csv para {mod} baixado com sucesso!")
            else:
                print(
                    f"Erro ao baixar classificacao.csv para {mod}: {resp.status_code}"
                )
                return False

    return True


def step2():
    """Process the courses configuration file, group courses by their núcleo, and save the revised structure to a new JSON file."""
    raw_config_path = os.path.join(
        current_dir, "data/step1-raw-data/config_cursos.json"
    )
    output_dir = os.path.join(current_dir, "data/step2-processed-data/")
    os.makedirs(output_dir, exist_ok=True)

    @dataclass
    class FileElement:
        id: str
        displayName: str
        shortName: str
        nucleus: str
        emblem: str
        colors: Tuple[str, str]

        def to_dict(self):
            return {
                "displayName": self.displayName,
                "shortName": self.shortName,
                "nucleus": self.nucleus,
                "emblem": self.emblem,
                "colors": self.colors,
            }

    elems: List[FileElement] = []
    with open(raw_config_path, "r") as f:
        data: dict = json.load(f)["courses"]
        for i, c in data.items():
            elem = FileElement(
                id=i,
                displayName=c["displayName"],
                shortName=c["shortName"],
                nucleus=c["nucleus"],
                emblem=c["emblem"],
                colors=tuple(c["colors"]),
            )
            elems.append(elem)

    # Agrupar por núcleo
    a = {}
    translator = {}
    for elem in elems:
        if elem.nucleus not in a:
            a[elem.nucleus] = []

        translator[elem.id] = elem.displayName

        if any(e.shortName == elem.shortName for e in a[elem.nucleus]):
            continue
        a[elem.nucleus].append(elem)

    # Salvar em um novo arquivo
    with open(f"{output_dir}/config_cursos_revised.json", "w") as f:
        json.dump(a, f, indent=4, default=lambda o: o.to_dict(), ensure_ascii=False)
    print("Arquivo config_cursos_revised.json salvo com sucesso!")

    # save translator
    with open(f"{output_dir}/translator.json", "w") as f:
        json.dump(translator, f, indent=4, ensure_ascii=False)
    print("Arquivo translator.json salvo com sucesso!")

    return True


def linear_system_solver(
    header: List[str], data: List[List[str]]
) -> Tuple[float, float, float]:

    # Load dataframe
    df = pd.DataFrame(data, columns=header)

    # Build system:
    # pontos = vitorias*x + empates*y + derrotas*z

    A = df[["vitorias", "empates", "derrotas"]].to_numpy(dtype=float)
    b = df["pontos"].to_numpy(dtype=float)

    # Detect if there are any draw-related rows
    has_draws = np.any(A[:, 1] != 0)

    # CASE 1:
    # No draws at all -> assume:
    # y = (x + z) / 2
    #
    # Then:
    # pontos = v*x + e*((x+z)/2) + d*z
    #
    # Rewrite into 2 unknowns:
    # pontos = (v + e/2)*x + (d + e/2)*z

    if not has_draws:

        A_reduced = np.column_stack(
            [
                A[:, 0] + A[:, 1] / 2,  # coefficient for x
                A[:, 2] + A[:, 1] / 2,  # coefficient for z
            ]
        )

        rank_A = np.linalg.matrix_rank(A_reduced)
        rank_augmented = np.linalg.matrix_rank(np.c_[A_reduced, b])

        if rank_augmented > rank_A:
            raise ValueError("Impossible mathematically: inconsistent equations.")

        if rank_A < 2:
            raise ValueError(
                "Impossible mathematically: insufficient independent data."
            )

        solution, residuals, _, _ = np.linalg.lstsq(A_reduced, b, rcond=None)

        x, z = solution
        y = (x + z) / 2

        reconstructed = A_reduced @ solution

        if not np.allclose(reconstructed, b):
            raise ValueError("No exact solution exists.")

    # CASE 2:
    # Normal 3-variable system

    else:

        rank_A = np.linalg.matrix_rank(A)
        rank_augmented = np.linalg.matrix_rank(np.c_[A, b])

        if rank_augmented > rank_A:
            raise ValueError("Impossible mathematically: inconsistent equations.")

        if rank_A < 3:
            raise ValueError(
                "Impossible mathematically: insufficient independent data."
            )

        solution, residuals, _, _ = np.linalg.lstsq(A, b, rcond=None)

        x, y, z = solution

        reconstructed = A @ solution

        if not np.allclose(reconstructed, b):
            raise ValueError("No exact solution exists.")

    return tuple(map(round, (x, y, z)))


def step3():
    """Process classificação.csv and detalhe.csv"""
    translator_path = os.path.join(
        current_dir, "data/step2-processed-data/translator.json"
    )
    output_dir = os.path.join(current_dir, "data/step3-final-data/")
    os.makedirs(output_dir, exist_ok=True)

    course_variants_translator = {}
    with open(translator_path, "r") as f:
        course_variants_translator = json.load(f)

    def get_tournament_name(mod: str, row: List[str], header: List[str]) -> str:
        tournament_name = f"Tourneio {mod.title()}"

        header_encoded = [h.encode("utf-8") for h in header]
        if b"Divis\xc3\x83\xc2\xa3o" in header_encoded:
            div_idx = header_encoded.index(b"Divis\xc3\x83\xc2\xa3o")
            division = row[div_idx]
            tournament_name += f" - Div {division}" if division else ""
        elif b"Divisao" in header_encoded:
            div_idx = header_encoded.index(b"Divisao")
            division = row[div_idx]
            tournament_name += f" - Div {division}" if division else ""

        if "Grupo" in header:
            group_idx = header.index("Grupo")
            group = row[group_idx]
            tournament_name += f" - Grupo {group}" if group else ""

        return tournament_name

    def calculate_tournament_format(
        mod: str, tournament_target: str
    ) -> Tuple[str, dict]:
        # Por enquanto, vamos assumir que todos os torneios são do tipo "league"
        with open(
            os.path.join(current_dir, f"data/step1-raw-data/{mod}/classificacao.csv"),
            "r",
        ) as f:
            config_data = list(csv.reader(f))

        d: dict[str, list] = {}
        header = config_data[0]
        for row in config_data[1:]:
            tournament_name = get_tournament_name(mod, row, header)
            if tournament_name not in d:
                d[tournament_name] = []
            d[tournament_name].append(row)

        for tournament_name, rows in d.items():
            if tournament_target and tournament_name != tournament_target:
                continue
            try:
                x, y, z = linear_system_solver(header=header, data=rows)
            except Exception as e:
                print(f"Erro ao resolver sistema linear para {tournament_name}: {e}")
                return 3, 1, 0  # fallback para formato clássico de pontos

            print(
                f"Formato deduzido para {tournament_name}: win={x} pts, draw={y} pts, loss={z} pts"
            )
            return x, y, z

        print(f"Não foi possível deduzir formato para {tournament_target} em {mod}.")
        return 3, 1, 0  # fallback para formato clássico de pontos

    def process_detalhe_csv(mod: str, detalhe_path: str, processed_data: dict):
        with open(detalhe_path, "r") as f:
            data = list(csv.reader(f))

        header = data[0]
        temp_data = {}
        for row in data[1:]:  # Skip header
            tounament_name = get_tournament_name(mod, row, header)
            joranada = row[header.index("Jornada")]
            day = row[header.index("Dia")]
            hour = row[header.index("Hora")]
            local = row[header.index("Local")]
            team1 = row[header.index("Equipa 1")]
            team2 = row[header.index("Equipa 2")]
            team1_score = row[header.index("Golos 1")]
            team2_score = row[header.index("Golos 2")]

            # Traduzir variantes de cursos para nomes canônicos
            team1 = course_variants_translator.get(team1, team1)
            team2 = course_variants_translator.get(team2, team2)

            if tounament_name not in temp_data:
                temp_data[tounament_name] = []

            temp_data[tounament_name].append(
                {
                    "joranada": joranada,
                    "day": day,
                    "hour": hour,
                    "local": local,
                    "team1": team1,
                    "team2": team2,
                    "team1_score": int(float(team1_score)) if team1_score else None,
                    "team2_score": int(float(team2_score)) if team2_score else None,
                }
            )

        for tournament_name, matches in temp_data.items():
            pw, pd, pl = calculate_tournament_format(
                mod, tournament_target=tournament_name
            )
            processed_data["tournaments"].append(
                {
                    "name": tournament_name,
                    "teams": list(
                        set(
                            [m["team1"] for m in matches]
                            + [m["team2"] for m in matches]
                        )
                    ),
                    "matches": matches,
                    "format": "league",
                    "format_data": {
                        "win_points": pw,
                        "draw_points": pd,
                        "loss_points": pl,
                    },
                }
            )

        processed_data["teams"] = list(
            set(
                processed_data["teams"]
                + [t for t in processed_data["tournaments"] for t in t["teams"]]
            )
        )

    csvs_dir = os.path.join(current_dir, "data/step1-raw-data/")
    all_data = {}
    for mod in os.listdir(csvs_dir):
        if not os.path.isdir(os.path.join(csvs_dir, mod)):
            continue

        print(f"Processando modalidade: {mod.title()}")
        mod_processed_data = {
            "teams": [],
            "tournaments": [],
        }

        # Processar detalhe.csv
        detalhe_path = os.path.join(csvs_dir, mod, "detalhe.csv")
        if not os.path.exists(detalhe_path):
            print(f"Arquivo de detalhe não encontrado para {mod}, pulando...")
            continue
        process_detalhe_csv(mod, detalhe_path, mod_processed_data)

        # Por enquanto, vamos apenas imprimir os dados processados para cada modalidade
        all_data[mod.title()] = mod_processed_data

    with open(os.path.join(output_dir, "processed_data.json"), "w") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

    # copy config_cursos_revised.json to final data dir
    config_src = os.path.join(
        current_dir, "data/step2-processed-data/config_cursos_revised.json"
    )
    config_dst = os.path.join(output_dir, "config_cursos_revised.json")
    with open(config_src, "r") as src, open(config_dst, "w") as dst:
        dst.write(src.read())


def main():
    succes = step1(year="25_26")
    if not succes:
        print("Erro ao processar config_cursos.json")
        return

    step2()
    step3()


if __name__ == "__main__":
    main()
