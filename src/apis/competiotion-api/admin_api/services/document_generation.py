from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .enricher_service import MatchCompletedDTO

# ── Colours matching the team sheet style ──────────────────────────────
HEADER_BG = colors.HexColor("#1F4E79")  # dark blue title bar
ROW_DARK = colors.HexColor("#D6E4F0")  # light-blue alternating rows
COL_LABEL = colors.HexColor("#2E75B6")  # medium-blue label cells
WHITE = colors.white
BLACK = colors.black


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

    def generate_match_report(self, match: MatchCompletedDTO) -> bytes:
        """Generate a PDF report for a match

        Args:
            match: MatchCompletedDTO with enriched participant data

        Returns:
            bytes: PDF file content
        """
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

            # Players sub-table
            players = team.players if team and team.players else []
            player_header_row = [
                self._P("#", style_label),
                self._P("Nome", style_label),
                self._P("Curso", style_label),
                self._P("Nº Estudante", style_label),
            ]
            player_rows = [player_header_row]
            for idx, player in enumerate(players, start=1):
                course_name = (
                    player.course.abbreviation
                    if player.course and player.course.abbreviation
                    else "-"
                )
                player_rows.append(
                    [
                        self._P(str(idx), style_center),
                        self._P(player.full_name or "N/A", style_normal),
                        self._P(course_name, style_center),
                        self._P(player.student_number or "-", style_center),
                    ]
                )

            if len(player_rows) == 1:
                # No players registered
                player_rows.append(
                    [self._P("Sem jogadores registados", style_normal), "", "", ""]
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

        # Empty space for notes
        notes_body = [[""], [""], [""], [""]]
        notes_body_tbl = Table(
            notes_body, colWidths=[TABLE_W], rowHeights=[15 * mm] * 4
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


# Create a singleton instance
document_generation_service = DocumentGenerationService()
