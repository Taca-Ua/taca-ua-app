from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .service import Match, matches_service

# ── Colours matching the team sheet style ──────────────────────────────
HEADER_BG = colors.HexColor("#1F4E79")  # dark blue title bar
ROW_DARK = colors.HexColor("#D6E4F0")  # light-blue alternating rows
COL_LABEL = colors.HexColor("#2E75B6")  # medium-blue label cells
WHITE = colors.white
BLACK = colors.black


class DocumentGenerationLackPermissitonError(Exception):
    """Custom exception for document generation errors"""

    pass


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

    def generate_match_report(self, match: Match) -> bytes:
        """Generate a PDF report for a match

        Args:
            match_id: The ID of the match to generate a report for

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

        # ── 3. Participants section (updated for new DTOs) ─────────────────────
        # All participants are now flat; no participant_type. We'll treat all as generic participants.
        participant_col_w = [
            TABLE_W * 0.45,
            TABLE_W * 0.15,
            TABLE_W * 0.05,
            TABLE_W * 0.25,
        ]
        participant_header = [
            self._P("Nome", style_label),
            self._P(
                "Pontuação" if match.participants[0].score is not None else "Posição",
                style_label,
            ),
        ]
        if match.lineups is None:
            participant_header.append(
                self._P("P", style_label)
            )  # empty header for presence column if no lineups

        participant_rows = [participant_header]
        for participant in match.participants:
            participant_rows.append(
                [
                    self._P(participant.name, style_normal),
                    (
                        self._P(
                            (
                                str(participant.score)
                                if participant.score is not None
                                else "-"
                            ),
                            style_center,
                        )
                        if participant.score is not None
                        else self._P(
                            (
                                str(participant.position)
                                if participant.position is not None
                                else "-"
                            ),
                            style_center,
                        )
                    ),
                ]
            )
            if match.lineups is None:
                participant_rows[-1].append(
                    self._P("", style_center)
                )  # empty cell for presence if no lineups
        participant_tbl = Table(participant_rows, colWidths=participant_col_w)
        ts = self._base_ts() + [("BACKGROUND", (0, 0), (-1, 0), COL_LABEL)]
        for r in range(1, len(participant_rows)):
            if r % 2 == 0:
                ts.append(("BACKGROUND", (0, r), (-1, r), ROW_DARK))
        participant_tbl.setStyle(TableStyle(ts))
        story.append(participant_tbl)
        story.append(Spacer(1, 8))

        # --- 3b. Lineups per participant (team or athlete) ----------------------
        lineup_col_w = [
            TABLE_W * 0.08,
            TABLE_W * 0.42,
            TABLE_W * 0.28,
            TABLE_W * 0.17,
            TABLE_W * 0.05,
        ]
        for lineup in match.lineups or []:
            # Find participant name for header
            participant = next(
                (p for p in match.participants if p.id == lineup.participant_id), None
            )
            participant_name = participant.name if participant else "Participante"
            # Header row
            lineup_header_data = [
                [self._P(f"Convocatória: {participant_name}", style_white_b)]
            ]
            lineup_header_tbl = Table(lineup_header_data, colWidths=[TABLE_W])
            lineup_header_tbl.setStyle(
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
            story.append(lineup_header_tbl)
            # Player table
            player_header_row = [
                self._P("#", style_label),
                self._P("Nome", style_label),
                self._P("Curso", style_label),
                self._P("Nº Estudante", style_label),
                self._P("P", style_label),  # presence checkbox column
            ]
            player_rows = [player_header_row]
            for idx, player in enumerate(lineup.lineup, start=1):
                player_rows.append(
                    [
                        self._P(
                            (
                                str(player.jersey_number)
                                if player.jersey_number is not None
                                else "-"
                            ),
                            style_center,
                        ),
                        self._P(player.player_name, style_normal),
                        self._P(
                            player.player_course if player.player_course else "-",
                            style_center,
                        ),
                        self._P(str(player.player_student_number), style_center),
                        self._P("", style_center),  # presence checkbox column (empty)
                    ]
                )
            if len(player_rows) == 1:
                player_rows.append(["", "", "", "", ""])
            players_tbl = Table(player_rows, colWidths=lineup_col_w)
            ts = self._base_ts() + [("BACKGROUND", (0, 0), (-1, 0), COL_LABEL)]
            for r in range(1, len(player_rows)):
                if r % 2 == 0:
                    ts.append(("BACKGROUND", (0, r), (-1, r), ROW_DARK))
            players_tbl.setStyle(TableStyle(ts))
            story.append(players_tbl)
            story.append(Spacer(1, 8))

            # Staff assignments for this participant
            if (
                match.staff_assignments
                and lineup.participant_id in match.staff_assignments
            ):
                staff_list = match.staff_assignments[lineup.participant_id]
                if staff_list:
                    staff_header_data = [
                        [self._P(f"Equipa Técnica: {participant_name}", style_white_b)]
                    ]
                    staff_header_tbl = Table(staff_header_data, colWidths=[TABLE_W])
                    staff_header_tbl.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, -1), HEADER_BG),
                                ("TOPPADDING", (0, 0), (-1, -1), 5),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                (
                                    "GRID",
                                    (0, 0),
                                    (-1, -1),
                                    0.5,
                                    colors.HexColor("#BDC3C7"),
                                ),
                            ]
                        )
                    )
                    story.append(staff_header_tbl)

                    staff_col_w = [TABLE_W * 0.7, TABLE_W * 0.3]
                    staff_header_row = [
                        self._P("Nome", style_label),
                        self._P("Função", style_label),
                    ]
                    staff_rows = [staff_header_row]
                    for staff in staff_list:
                        staff_rows.append(
                            [
                                self._P(staff.name, style_normal),
                                self._P(
                                    "", style_normal
                                ),  # empty cell for role/function manually filled in by user
                            ]
                        )
                    staff_tbl = Table(staff_rows, colWidths=staff_col_w)
                    ts = self._base_ts() + [("BACKGROUND", (0, 0), (-1, 0), COL_LABEL)]
                    for r in range(1, len(staff_rows)):
                        if r % 2 == 0:
                            ts.append(("BACKGROUND", (0, r), (-1, r), ROW_DARK))
                    staff_tbl.setStyle(TableStyle(ts))
                    story.append(staff_tbl)
                    story.append(Spacer(1, 8))
        if match.lineups is None:
            # If no lineups, add a note about that
            no_lineup_tbl = Table(
                [[self._P("Sem convocatórias registadas", style_normal)]],
                colWidths=[TABLE_W],
                rowHeights=[10 * mm],
            )
            no_lineup_tbl.setStyle(TableStyle(self._base_ts()))
            story.append(no_lineup_tbl)
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
            notes_body = [[""]]

        notes_body_tbl = Table(
            notes_body,
            colWidths=[TABLE_W],
            rowHeights=None if comments else [10 * mm],
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

    def generate_match_team_report(
        self, match_id: str, participant_id: str, admin_id: str = None
    ) -> bytes:
        """Generate a PDF report for a match and a specific participant (team or athlete)

        Raises:
            ValueError: If participant is not found in match or if no lineups are found for the participant
        """
        match: Match = matches_service.get_match(match_id, admin_id=admin_id)
        # Find the participant
        participant = next(
            (p for p in match.participants if p.id == participant_id), None
        )
        if not participant:
            raise ValueError("Participant not found in match")
        # Filter lineups for this participant
        participant_lineups = [
            lineup
            for lineup in match.lineups
            if lineup.participant_id == participant_id
        ]

        if all(pl.lineup is None for pl in participant_lineups):
            raise DocumentGenerationLackPermissitonError(
                "No lineups found for participant; cannot generate report"
            )

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
        title_data = [[self._P("Ficha de Participante", style_white_b)]]
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

        # ── 2. Participant info table ─────────────────────────────────────────────
        info_rows = [
            [self._P("ID do Jogo", style_label), self._P(str(match.id), style_bold)],
            [self._P("Nome", style_label), self._P(participant.name, style_bold)],
            [
                self._P("Pontuação", style_label),
                self._P(
                    str(participant.score) if participant.score is not None else "-",
                    style_bold,
                ),
            ],
            [
                self._P("Posição", style_label),
                self._P(
                    (
                        str(participant.position)
                        if participant.position is not None
                        else "-"
                    ),
                    style_bold,
                ),
            ],
        ]
        info_tbl = Table(info_rows, colWidths=[TABLE_W * 0.35, TABLE_W * 0.65])
        ts = self._base_ts() + [
            ("BACKGROUND", (0, r), (0, r), COL_LABEL) for r in range(len(info_rows))
        ]
        for r in range(len(info_rows)):
            if r % 2 == 1:
                ts.append(("BACKGROUND", (1, r), (1, r), ROW_DARK))
        info_tbl.setStyle(TableStyle(ts))
        story.append(info_tbl)
        story.append(Spacer(1, 10))

        # ── 3. Lineup table (if any) ─────────────────────────────────────────────
        if participant_lineups:
            for lineup in participant_lineups:
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
                    self._P("Curso", style_label),
                    self._P("Presença", style_label),
                ]
                lineup_rows = [lineup_header_row]
                for idx, player in enumerate(lineup.lineup, start=1):
                    lineup_rows.append(
                        [
                            self._P(
                                (
                                    str(player.jersey_number)
                                    if player.jersey_number is not None
                                    else "-"
                                ),
                                style_center,
                            ),
                            self._P(player.player_name, style_normal),
                            self._P(
                                player.player_course if player.player_course else "-",
                                style_center,
                            ),
                            self._P(
                                "", style_center
                            ),  # presence checkbox column (empty)
                        ]
                    )
                if len(lineup_rows) == 1:
                    lineup_rows.append(["", "", "", ""])
                lineup_tbl = Table(lineup_rows, colWidths=lineup_col_w)
                ts = self._base_ts() + [("BACKGROUND", (0, 0), (-1, 0), COL_LABEL)]
                for r in range(1, len(lineup_rows)):
                    if r % 2 == 0:
                        ts.append(("BACKGROUND", (0, r), (-1, r), ROW_DARK))
                lineup_tbl.setStyle(TableStyle(ts))
                story.append(lineup_tbl)
                story.append(Spacer(1, 10))

                # Staff assignments for this participant
                if (
                    match.staff_assignments
                    and participant_id in match.staff_assignments
                ):
                    staff_list = match.staff_assignments[participant_id]
                    if staff_list:
                        staff_section_header = [
                            [self._P("Equipa Técnica", style_label)]
                        ]
                        staff_header_tbl = Table(
                            staff_section_header, colWidths=[TABLE_W]
                        )
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

                        staff_col_w = [TABLE_W * 0.7, TABLE_W * 0.3]
                        staff_header_row = [
                            self._P("Nome", style_label),
                            self._P("Função", style_label),
                        ]
                        staff_rows = [staff_header_row]
                        for staff in staff_list:
                            staff_rows.append(
                                [
                                    self._P(staff.name, style_normal),
                                    self._P(
                                        "", style_normal
                                    ),  # empty cell for role/function manually filled in by user
                                ]
                            )
                        staff_tbl = Table(staff_rows, colWidths=staff_col_w)
                        ts = self._base_ts() + [
                            ("BACKGROUND", (0, 0), (-1, 0), COL_LABEL)
                        ]
                        for r in range(1, len(staff_rows)):
                            if r % 2 == 0:
                                ts.append(("BACKGROUND", (0, r), (-1, r), ROW_DARK))
                        staff_tbl.setStyle(TableStyle(ts))
                        story.append(staff_tbl)
                        story.append(Spacer(1, 10))

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
