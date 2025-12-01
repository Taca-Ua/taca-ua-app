"""
Serializers for Competition API (Admin API)
All serializers follow the API_ENDPOINTS.md specification
"""

from rest_framework import serializers

# ================== 1. User Management (RF1) ==================


class NucleoAdminListSerializer(serializers.Serializer):
    """Serializer for listing nucleo administrators"""

    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField()
    email = serializers.EmailField()
    course_id = serializers.IntegerField()
    full_name = serializers.CharField(required=False, allow_blank=True)


class NucleoAdminCreateSerializer(serializers.Serializer):
    """Serializer for creating nucleo administrator"""

    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    course_id = serializers.IntegerField(required=True)
    full_name = serializers.CharField(required=False, allow_blank=True)


class NucleoAdminUpdateSerializer(serializers.Serializer):
    """Serializer for updating nucleo administrator"""

    course_id = serializers.IntegerField(required=False)
    full_name = serializers.CharField(required=False, allow_blank=True)


# ================== 2. Course Management (RF2) ==================


class CourseListSerializer(serializers.Serializer):
    """Serializer for listing courses"""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    short_code = serializers.CharField()
    color = serializers.CharField(required=False, allow_blank=True)


class CourseCreateSerializer(serializers.Serializer):
    """Serializer for creating a course"""

    name = serializers.CharField(required=True)
    short_code = serializers.CharField(required=True)
    color = serializers.CharField(required=False, allow_blank=True)


class CourseUpdateSerializer(serializers.Serializer):
    """Serializer for updating a course"""

    name = serializers.CharField(required=False)
    short_code = serializers.CharField(required=False)
    color = serializers.CharField(required=False, allow_blank=True)


# ================== 3. Regulation Management (RF2.3) ==================


class RegulationListSerializer(serializers.Serializer):
    """Serializer for listing regulations"""

    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    modality_id = serializers.IntegerField(required=False, allow_null=True)
    file_url = serializers.URLField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class RegulationCreateSerializer(serializers.Serializer):
    """Serializer for uploading a regulation"""

    file = serializers.FileField(required=True)
    title = serializers.CharField(required=True)
    modality_id = serializers.IntegerField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True)


class RegulationUpdateSerializer(serializers.Serializer):
    """Serializer for updating regulation metadata"""

    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    modality_id = serializers.IntegerField(required=False, allow_null=True)


# ================== 4. Modality Management (RF3) ==================


class ModalityListSerializer(serializers.Serializer):
    """Serializer for listing modalities"""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    type = serializers.ChoiceField(choices=["coletiva", "individual", "mista"])
    scoring_schema = serializers.JSONField(required=False, allow_null=True)


class ModalityCreateSerializer(serializers.Serializer):
    """Serializer for creating a modality"""

    name = serializers.CharField(required=True)
    type = serializers.ChoiceField(
        choices=["coletiva", "individual", "mista"], required=True
    )
    scoring_schema = serializers.JSONField(required=False, allow_null=True)


class ModalityUpdateSerializer(serializers.Serializer):
    """Serializer for updating a modality"""

    name = serializers.CharField(required=False)
    type = serializers.ChoiceField(
        choices=["coletiva", "individual", "mista"], required=False
    )
    scoring_schema = serializers.JSONField(required=False, allow_null=True)


# ================== 5. Tournament Management (RF3) ==================


class TournamentListSerializer(serializers.Serializer):
    """Serializer for listing tournaments"""

    id = serializers.IntegerField(read_only=True)
    modality_id = serializers.IntegerField()
    name = serializers.CharField()
    season_id = serializers.IntegerField()
    rules = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(
        choices=["draft", "active", "finished"], read_only=True
    )
    start_date = serializers.DateTimeField(required=False, allow_null=True)
    teams = serializers.ListField(child=serializers.IntegerField(), required=False)


class TournamentCreateSerializer(serializers.Serializer):
    """Serializer for creating a tournament"""

    modality_id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)
    season_id = serializers.IntegerField(required=True)
    rules = serializers.CharField(required=False, allow_blank=True)
    teams = serializers.ListField(child=serializers.IntegerField(), required=False)
    start_date = serializers.DateTimeField(required=False, allow_null=True)


class TournamentUpdateSerializer(serializers.Serializer):
    """Serializer for updating a tournament"""

    name = serializers.CharField(required=False)
    rules = serializers.CharField(required=False, allow_blank=True)
    teams = serializers.ListField(child=serializers.IntegerField(), required=False)
    start_date = serializers.DateTimeField(required=False, allow_null=True)


# ================== 6. Team Management (RF4) ==================


class TeamListSerializer(serializers.Serializer):
    """Serializer for listing teams"""

    id = serializers.IntegerField(read_only=True)
    modality_id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    name = serializers.CharField(required=False, allow_blank=True)
    players = serializers.ListField(child=serializers.IntegerField(), required=False)


class TeamCreateSerializer(serializers.Serializer):
    """Serializer for creating a team"""

    modality_id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=False, allow_blank=True)
    players = serializers.ListField(child=serializers.IntegerField(), required=False)


class TeamUpdateSerializer(serializers.Serializer):
    """Serializer for updating a team"""

    name = serializers.CharField(required=False, allow_blank=True)
    players_add = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    players_remove = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )


# ================== 7. Student Management (RF4) ==================


class StudentListSerializer(serializers.Serializer):
    """Serializer for listing students"""

    id = serializers.IntegerField(read_only=True)
    course_id = serializers.IntegerField()
    full_name = serializers.CharField()
    student_number = serializers.CharField()
    email = serializers.EmailField(required=False, allow_blank=True)
    is_member = serializers.BooleanField(default=False)


class StudentCreateSerializer(serializers.Serializer):
    """Serializer for creating a student"""

    full_name = serializers.CharField(required=True)
    student_number = serializers.CharField(required=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    is_member = serializers.BooleanField(required=False, default=False)


class StudentUpdateSerializer(serializers.Serializer):
    """Serializer for updating a student"""

    full_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False, allow_blank=True)
    is_member = serializers.BooleanField(required=False)


# ================== 8. Match Management (RF7) ==================


class MatchListSerializer(serializers.Serializer):
    """Serializer for listing matches"""

    id = serializers.IntegerField(read_only=True)
    tournament_id = serializers.IntegerField()
    team_home_id = serializers.IntegerField()
    team_away_id = serializers.IntegerField()
    location = serializers.CharField()
    start_time = serializers.DateTimeField()
    status = serializers.ChoiceField(choices=["scheduled", "finished"], read_only=True)
    home_score = serializers.IntegerField(required=False, allow_null=True)
    away_score = serializers.IntegerField(required=False, allow_null=True)


class MatchCreateSerializer(serializers.Serializer):
    """Serializer for creating a match"""

    tournament_id = serializers.IntegerField(required=True)
    team_home_id = serializers.IntegerField(required=True)
    team_away_id = serializers.IntegerField(required=True)
    location = serializers.CharField(required=True)
    start_time = serializers.DateTimeField(required=True)


class MatchUpdateSerializer(serializers.Serializer):
    """Serializer for updating a match"""

    location = serializers.CharField(required=False)
    start_time = serializers.DateTimeField(required=False)
    team_home_id = serializers.IntegerField(required=False)
    team_away_id = serializers.IntegerField(required=False)


class MatchResultSerializer(serializers.Serializer):
    """Serializer for registering match result"""

    home_score = serializers.IntegerField(required=True)
    away_score = serializers.IntegerField(required=True)


class PlayerLineupSerializer(serializers.Serializer):
    """Serializer for player in lineup"""

    player_id = serializers.IntegerField(required=True)
    jersey_number = serializers.IntegerField(required=True)


class MatchLineupSerializer(serializers.Serializer):
    """Serializer for assigning players to match"""

    team_id = serializers.IntegerField(required=True)
    players = PlayerLineupSerializer(many=True, required=True)


class MatchCommentSerializer(serializers.Serializer):
    """Serializer for adding match comments"""

    message = serializers.CharField(required=True)


# ================== 9. Season Management (RF2.4) ==================


class SeasonListSerializer(serializers.Serializer):
    """Serializer for listing seasons"""

    id = serializers.IntegerField(read_only=True)
    year = serializers.IntegerField()
    status = serializers.ChoiceField(
        choices=["draft", "active", "finished"], read_only=True
    )


class SeasonCreateSerializer(serializers.Serializer):
    """Serializer for creating a season"""

    year = serializers.IntegerField(required=True)
