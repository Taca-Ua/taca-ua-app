from __future__ import annotations

import itertools
import random
from typing import Hashable, List, Optional, Sequence, Tuple

Match = Tuple[Hashable, ...]
Round = List[Match]


class RoundRobinScheduler:
    BYE = "BYE"

    def __init__(
        self,
        participants: Sequence[Hashable],
        match_size: int = 2,
        num_faceoffs: int = 1,
        shuffle: bool = False,
        seed: Optional[int] = None,
    ):
        """
        participants : list of participant names/ids
        match_size   : how many participants share a single match (2 = classic 1v1)
        num_faceoffs : how many times each pair/group must meet
                       (1 = single round robin, 2 = double round robin, ...)
        shuffle      : randomize round order / candidate order for variety
        seed         : optional RNG seed for reproducibility
        """
        if match_size < 2:
            raise ValueError("match_size must be at least 2")
        if len(participants) < match_size:
            raise ValueError("Not enough participants for the given match size")
        if num_faceoffs < 1:
            raise ValueError("num_faceoffs must be at least 1")

        self.participants = list(participants)
        self.match_size = match_size
        self.num_faceoffs = num_faceoffs
        self.shuffle = shuffle

        if seed is not None:
            random.seed(seed)

    def generate(self, *, show_bye_matches: bool = True) -> List[Round]:
        """Return the full schedule as a list of rounds, each a list of matches."""
        if self.match_size == 2:
            rounds = self._generate_pairwise()
        else:
            rounds = self._generate_general()

        rounds = [self._drop_full_bye_matches(r) for r in rounds]
        if not show_bye_matches:
            # drop matches with any BYE participants
            rounds = [self._drop_bye_matches(r) for r in rounds]
        rounds = [r for r in rounds if r]  # drop now-empty rounds

        if self.shuffle:
            random.shuffle(rounds)

        return rounds

    @staticmethod
    def print_schedule(rounds: List[Round]) -> None:
        for i, round_matches in enumerate(rounds, start=1):
            print(f"Round {i}:")
            for match in round_matches:
                print("   " + " vs ".join(str(p) for p in match))
        print()

    def _generate_pairwise(self) -> List[Round]:
        """Generate rounds for pairwise matches using the circle method."""
        players = list(self.participants)
        if len(players) % 2 != 0:
            players.append(self.BYE)

        n = len(players)
        half = n // 2

        fixed = players[0]
        rotating = players[1:]

        base_rounds: List[Round] = []
        for _ in range(n - 1):
            current = [fixed] + rotating
            round_matches = [(current[i], current[n - 1 - i]) for i in range(half)]
            base_rounds.append(round_matches)
            rotating = [rotating[-1]] + rotating[:-1]

        all_rounds: List[Round] = []
        for leg in range(self.num_faceoffs):
            for round_matches in base_rounds:
                if leg % 2 == 1:
                    # alternate order on odd legs (e.g. "home/away" swap)
                    round_matches = [(b, a) for a, b in round_matches]
                all_rounds.append(list(round_matches))

        return all_rounds

    def _generate_general(self) -> List[Round]:
        """Generate rounds for matches with more than 2 participants using a greedy approach."""
        players = list(self.participants)
        k = self.match_size

        if len(players) % k != 0:
            missing = k - (len(players) % k)
            players += [f"{self.BYE}_{i}" for i in range(missing)]

        all_groups = list(itertools.combinations(players, k))
        remaining = {frozenset(g): self.num_faceoffs for g in all_groups}

        rounds: List[Round] = []
        safety_cap = len(all_groups) * self.num_faceoffs + len(players)

        while any(v > 0 for v in remaining.values()) and len(rounds) < safety_cap:
            round_matches: Round = []
            used = set()

            candidates = [g for g, v in remaining.items() if v > 0]
            candidates.sort(key=lambda g: -remaining[g])
            if self.shuffle:
                random.shuffle(candidates)

            for group in candidates:
                if used.isdisjoint(group):
                    round_matches.append(tuple(group))
                    used.update(group)
                    remaining[group] -= 1
                    if remaining[group] == 0:
                        del remaining[group]

            if not round_matches:
                break  # stuck, avoid infinite loop
            rounds.append(round_matches)

        return rounds

    def _drop_full_bye_matches(self, round_matches: Round) -> Round:
        """Drop matches that consist entirely of BYE participants."""
        return [
            m for m in round_matches if not all(str(p).startswith(self.BYE) for p in m)
        ]

    def _drop_bye_matches(self, round_matches: Round) -> Round:
        """Drop matches that contain any BYE participants."""
        return [
            m for m in round_matches if not any(str(p).startswith(self.BYE) for p in m)
        ]
