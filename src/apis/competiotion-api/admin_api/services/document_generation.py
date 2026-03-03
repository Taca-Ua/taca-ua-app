from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import List

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .enricher_service import MatchCompletedDTO, enricher_service
from .matches_service import CommentDTO, LineupDTO, MatchDTO, matches_service_client
from .modalities_service import modalities_service_client
from .tournaments_service import tournaments_service_client

# ── Colours matching the team sheet style ──────────────────────────────
HEADER_BG = colors.HexColor("#1F4E79")  # dark blue title bar
ROW_DARK = colors.HexColor("#D6E4F0")  # light-blue alternating rows
COL_LABEL = colors.HexColor("#2E75B6")  # medium-blue label cells
WHITE = colors.white
BLACK = colors.black


@dataclass
class MatchReportDTO(MatchCompletedDTO):
    comments: list[CommentDTO] = None
    lineups: list[LineupDTO] = None


@dataclass
class MatchTeamReportDTO:
    team_name: str
    team_course: str
    modality_name: str
    tournament_name: str

    staff_team: list
    lineup: List[LineupDTO]

    season: str = None


def _build_match_report_dto(match: MatchDTO) -> MatchReportDTO:
    res = MatchReportDTO(**match.__dict__)

    res.comments = matches_service_client.get_comments(match.id)

    linups = matches_service_client.get_lineup(match.id)
    enricher_service.complete_lineup_info(linups)
    res.lineups = linups

    return res


def _build_match_team_report_dto(match_id: str, team_id: str) -> MatchTeamReportDTO:
    team = modalities_service_client.get_team(team_id)
    match = matches_service_client.get_match(match_id)
    tournament = tournaments_service_client.get_tournament(match.tournament_id)

    lineups = matches_service_client.get_lineup(match_id)
    lineups = enricher_service.complete_lineup_info(lineups)

    return MatchTeamReportDTO(
        team_name=team.name,
        team_course=team.course.name,
        modality_name=team.modality.name,
        tournament_name=tournament.name,
        staff_team=[],
        lineup=lineups,
    )


class DocumentGenerationService:
    def __init__(self):
        pass

    def _make_style(
        self,
        name,
        fontName="Helvetica",
        fontSize=9,
        textColor=BLACK,
        alignment=TA_LEFT,
        bold=False,
    ):
        """Create a paragraph style"""
        fn = "Helvetica-Bold" if bold else fontName
        return ParagraphStyle(
            name,
            fontName=fn,
            fontSize=fontSize,
            textColor=textColor,
            alignment=alignment,
            leading=fontSize * 1.3,
        )

    def _P(self, text, style):
        """Create a Paragraph with given style"""
        return Paragraph(str(text), style)

    def _base_ts(self):
        """Common TableStyle commands"""
        return [
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]

    def generate_match_report(self, match: MatchDTO) -> bytes:
        """Generate a PDF report for a match

        Args:
            match_id: The ID of the match to generate a report for

        Returns:
            bytes: PDF file content
        """
        # Build match report DTO with lineups
        match = _build_match_report_dto(match)

        # Create a BytesIO buffer to hold the PDF
        buffer = BytesIO()

        # Page dimensions
        PAGE_W = A4[0]
        MARGIN = 20 * mm
        TABLE_W = PAGE_W - 2 * MARGIN

        # Create styles
        style_normal = self._make_style("normal")
        style_bold = self._make_style("bold", bold=True)
        style_white_b = self._make_style("white_b", bold=True, textColor=WHITE)
        style_center = self._make_style("center", alignment=TA_CENTER)
        # style_center_b = self._make_style("center_b", alignment=TA_CENTER, bold=True)
        style_label = self._make_style("label", bold=True, textColor=WHITE)

        # Build story
        story = []

        # ── 1. Main title ─────────────────────────────────────────────────────────
        title_data = [[self._P("Ficha de Jogo", style_white_b)]]
        title_tbl = Table(title_data, colWidths=[TABLE_W])
        title_tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), HEADER_BG),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(title_tbl)
        story.append(Spacer(1, 4))

        # ── 2. Match info table ────────────────────────────────────────────────────
        # Format start time
        try:
            start_dt = datetime.fromisoformat(match.start_time.replace("Z", "+00:00"))
            formatted_time = start_dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            formatted_time = match.start_time

        match_info = [
            ("ID do Jogo", str(match.id)),
            ("Localização", match.location),
            ("Data/Hora", formatted_time),
            ("Estado", match.status.upper()),
        ]

        match_rows = []
        for label, value in match_info:
            match_rows.append([self._P(label, style_label), self._P(value, style_bold)])

        col_w = [TABLE_W * 0.35, TABLE_W * 0.65]
        match_tbl = Table(match_rows, colWidths=col_w)
        ts = self._base_ts() + [
            ("BACKGROUND", (0, r), (0, r), COL_LABEL) for r in range(len(match_rows))
        ]
        # Alternating right column
        for r in range(len(match_rows)):
            if r % 2 == 1:
                ts.append(("BACKGROUND", (1, r), (1, r), ROW_DARK))
        match_tbl.setStyle(TableStyle(ts))
        story.append(match_tbl)
        story.append(Spacer(1, 10))

        # ── 3. Participants section ────────────────────────────────────────────────
        team_participants = [
            p for p in match.participants if p.participant_type == "team"
        ]
        athlete_participants = [
            p for p in match.participants if p.participant_type != "team"
        ]

        # --- 3a. Athlete participants (simple summary table) -------------------
        if athlete_participants:
            athlete_col_w = [
                TABLE_W * 0.45,
                TABLE_W * 0.15,
                TABLE_W * 0.15,
                TABLE_W * 0.25,
            ]
            athlete_header = [
                self._P("Atleta", style_label),
                self._P("Tipo", style_label),
                self._P("Pontuação", style_label),
                self._P("Posição", style_label),
            ]
            athlete_rows = [athlete_header]
            for participant in athlete_participants:
                athlete = participant.athlete
                name = (
                    athlete.full_name.strip()
                    if athlete and athlete.full_name
                    else "N/A"
                )
                athlete_rows.append(
                    [
                        self._P(name, style_normal),
                        self._P(participant.participant_type.upper(), style_center),
                        self._P(
                            (
                                str(participant.score)
                                if participant.score is not None
                                else "-"
                            ),
                            style_center,
                        ),
                        self._P(
                            (
                                str(participant.position)
                                if participant.position is not None
                                else "-"
                            ),
                            style_center,
                        ),
                    ]
                )

            athlete_tbl = Table(athlete_rows, colWidths=athlete_col_w)
            ts = self._base_ts() + [("BACKGROUND", (0, 0), (-1, 0), COL_LABEL)]
            for r in range(1, len(athlete_rows)):
                if r % 2 == 0:
                    ts.append(("BACKGROUND", (0, r), (-1, r), ROW_DARK))
            athlete_tbl.setStyle(TableStyle(ts))
            story.append(athlete_tbl)
            story.append(Spacer(1, 6))

        # --- 3b. One sub-table per team participant ----------------------------
        player_col_w = [
            TABLE_W * 0.08,
            TABLE_W * 0.42,
            TABLE_W * 0.30,
            TABLE_W * 0.20,
        ]

        for participant in team_participants:
            team = participant.team
            team_name = team.name if team else "N/A"
            score_str = str(participant.score) if participant.score is not None else "-"
            position_str = (
                str(participant.position) if participant.position is not None else "-"
            )

            # Team header row: name | Pontuação label+value | Posição label+value
            team_header_data = [
                [
                    self._P(f"EQUIPA: {team_name}", style_white_b),
                    self._P(f"Pontuação: {score_str}", style_white_b),
                    self._P(f"Posição: {position_str}", style_white_b),
                ]
            ]
            team_header_col_w = [TABLE_W * 0.50, TABLE_W * 0.25, TABLE_W * 0.25]
            team_header_tbl = Table(team_header_data, colWidths=team_header_col_w)
            team_header_tbl.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), HEADER_BG),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
                    ]
                )
            )
            story.append(team_header_tbl)

            # Lineup sub-table - filter lineups for this team
            team_lineups = (
                [
                    lineup
                    for lineup in (match.lineups or [])
                    if lineup.team_id == team.id
                ]
                if team
                else []
            )

            player_header_row = [
                self._P("#", style_label),
                self._P("Nome", style_label),
                self._P("Curso", style_label),
                self._P("Nº Estudante", style_label),
            ]
            player_rows = [player_header_row]

            for idx, lineup in enumerate(team_lineups, start=1):
                athlete = lineup.player if hasattr(lineup, "player") else None
                full_name = (
                    athlete.full_name
                    if athlete and hasattr(athlete, "full_name")
                    else "N/A"
                )
                course_name = (
                    athlete.course.abbreviation
                    if athlete
                    and hasattr(athlete, "course")
                    and athlete.course
                    and hasattr(athlete.course, "abbreviation")
                    else "-"
                )
                student_number = (
                    athlete.student_number
                    if athlete and hasattr(athlete, "student_number")
                    else "-"
                )
                jersy_number = (
                    lineup.jersey_number if hasattr(lineup, "jersey_number") else "-"
                )

                player_rows.append(
                    [
                        self._P(jersy_number, style_center),
                        self._P(full_name, style_normal),
                        self._P(course_name, style_center),
                        self._P(student_number or "-", style_center),
                    ]
                )

            if len(player_rows) == 1:
                # No lineup registered
                player_rows.append(
                    [self._P("Sem convocatória registada", style_normal), "", "", ""]
                )

            players_tbl = Table(player_rows, colWidths=player_col_w)
            ts = self._base_ts() + [("BACKGROUND", (0, 0), (-1, 0), COL_LABEL)]
            for r in range(1, len(player_rows)):
                if r % 2 == 0:
                    ts.append(("BACKGROUND", (0, r), (-1, r), ROW_DARK))
            players_tbl.setStyle(TableStyle(ts))
            story.append(players_tbl)
            story.append(Spacer(1, 8))

        story.append(Spacer(1, 4))

        # ── 4. Notes/Observations section ──────────────────────────────────────────
        notes_header = [[self._P("Observações", style_label)]]
        notes_tbl = Table(notes_header, colWidths=[TABLE_W])
        notes_tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), COL_LABEL),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(notes_tbl)

        # Comments/Observations body
        comments = match.comments or []
        if comments:
            notes_body = []
            for comment in comments:
                comment_text = (
                    comment.message if hasattr(comment, "message") else str(comment)
                )
                notes_body.append([self._P(comment_text, style_normal)])
        else:
            # Empty space for notes if no comments
            notes_body = [[""], [""], [""], [""]]

        notes_body_tbl = Table(
            notes_body,
            colWidths=[TABLE_W],
            rowHeights=None if comments else [15 * mm] * 4,
        )
        notes_body_tbl.setStyle(TableStyle(self._base_ts()))
        story.append(notes_body_tbl)

        # ══════════════════════════════════════════════════════════════════════════
        # BUILD PDF
        # ══════════════════════════════════════════════════════════════════════════
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN,
        )
        doc.build(story)

        # Get the PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    def generate_match_team_report(self, match_id: str, team_id: str) -> bytes:
        """Generate a PDF report for a match and team

        Args:
            match_id: The match ID to generate a report for
            team_id: The team ID to filter the report by

        Returns:
            bytes: PDF file content
        """
        data = _build_match_team_report_dto(match_id, team_id)

        buffer = BytesIO()

        PAGE_W = A4[0]
        MARGIN = 20 * mm
        TABLE_W = PAGE_W - 2 * MARGIN

        # Styles
        style_normal = self._make_style("normal")
        style_bold = self._make_style("bold", bold=True)
        style_white_b = self._make_style("white_b", bold=True, textColor=WHITE)
        style_center = self._make_style("center", alignment=TA_CENTER)
        style_label = self._make_style("label", bold=True, textColor=WHITE)

        story = []

        # ── 1. Title bar ──────────────────────────────────────────────────────────
        title_data = [[self._P("Ficha de Equipa", style_white_b)]]
        title_tbl = Table(title_data, colWidths=[TABLE_W])
        title_tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), HEADER_BG),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(title_tbl)
        story.append(Spacer(1, 4))

        # ── 2. General info table ─────────────────────────────────────────────────
        general_info = [
            ("Equipa", data.team_name),
            ("Curso", data.team_course),
            ("Época", data.season or "-"),
            ("Modalidade", data.modality_name),
            ("Campeonato", data.tournament_name),
        ]

        col_w = [TABLE_W * 0.35, TABLE_W * 0.65]
        general_rows = []
        for label, value in general_info:
            general_rows.append(
                [self._P(label, style_label), self._P(value, style_bold)]
            )

        general_tbl = Table(general_rows, colWidths=col_w)
        ts = self._base_ts() + [
            ("BACKGROUND", (0, r), (0, r), COL_LABEL) for r in range(len(general_rows))
        ]
        for r in range(len(general_rows)):
            if r % 2 == 1:
                ts.append(("BACKGROUND", (1, r), (1, r), ROW_DARK))
        general_tbl.setStyle(TableStyle(ts))
        story.append(general_tbl)
        story.append(Spacer(1, 10))

        # ── 3. Staff table ────────────────────────────────────────────────────────
        staff_section_header = [[self._P("Equipa Técnica", style_label)]]
        staff_header_tbl = Table(staff_section_header, colWidths=[TABLE_W])
        staff_header_tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), HEADER_BG),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(staff_header_tbl)

        staff_col_w = [TABLE_W * 0.45, TABLE_W * 0.30, TABLE_W * 0.25]
        staff_header_row = [
            self._P("Nome", style_label),
            self._P("Função", style_label),
            self._P("Contacto", style_label),
        ]
        staff_rows = [staff_header_row]

        for member in data.staff_team or []:
            staff_rows.append(
                [
                    self._P(getattr(member, "name", "-"), style_normal),
                    self._P(getattr(member, "role", "-"), style_normal),
                    self._P(getattr(member, "contact", "-"), style_normal),
                ]
            )

        # Always show at least 3 empty rows when no staff data
        if len(staff_rows) == 1:
            for _ in range(3):
                staff_rows.append(["", "", ""])

        staff_tbl = Table(staff_rows, colWidths=staff_col_w)
        ts = self._base_ts() + [("BACKGROUND", (0, 0), (-1, 0), COL_LABEL)]
        for r in range(1, len(staff_rows)):
            if r % 2 == 0:
                ts.append(("BACKGROUND", (0, r), (-1, r), ROW_DARK))
        staff_tbl.setStyle(TableStyle(ts))
        story.append(staff_tbl)
        story.append(Spacer(1, 10))

        # ── 4. Lineup table ───────────────────────────────────────────────────────
        lineup_section_header = [[self._P("Convocatória", style_label)]]
        lineup_header_tbl = Table(lineup_section_header, colWidths=[TABLE_W])
        lineup_header_tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), HEADER_BG),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(lineup_header_tbl)

        lineup_col_w = [
            TABLE_W * 0.08,
            TABLE_W * 0.42,
            TABLE_W * 0.22,
            TABLE_W * 0.28,
        ]
        lineup_header_row = [
            self._P("#", style_label),
            self._P("Nome Completo", style_label),
            self._P("Nº Mec.", style_label),
            self._P("Presença", style_label),
        ]
        lineup_rows = [lineup_header_row]

        for lineup in data.lineup or []:
            athlete = lineup.player if hasattr(lineup, "player") else None
            full_name = (
                athlete.full_name
                if athlete and hasattr(athlete, "full_name")
                else "N/A"
            )
            student_number = (
                str(athlete.student_number)
                if athlete
                and hasattr(athlete, "student_number")
                and athlete.student_number
                else "-"
            )
            jersey_number = (
                str(lineup.jersey_number)
                if hasattr(lineup, "jersey_number") and lineup.jersey_number is not None
                else "-"
            )
            lineup_rows.append(
                [
                    self._P(jersey_number, style_center),
                    self._P(full_name, style_normal),
                    self._P(student_number, style_center),
                    self._P("", style_center),  # presence checkbox column (empty)
                ]
            )

        if len(lineup_rows) == 1:
            lineup_rows.append(
                [self._P("Sem convocatória registada", style_normal), "", "", ""]
            )

        lineup_tbl = Table(lineup_rows, colWidths=lineup_col_w)
        ts = self._base_ts() + [("BACKGROUND", (0, 0), (-1, 0), COL_LABEL)]
        for r in range(1, len(lineup_rows)):
            if r % 2 == 0:
                ts.append(("BACKGROUND", (0, r), (-1, r), ROW_DARK))
        lineup_tbl.setStyle(TableStyle(ts))
        story.append(lineup_tbl)

        # ── BUILD PDF ─────────────────────────────────────────────────────────────
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN,
        )
        doc.build(story)

        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes


# Create a singleton instance
document_generation_service = DocumentGenerationService()
