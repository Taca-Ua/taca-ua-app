from .course_routes import router as course_router
from .modality_routes import router as modality_router
from .modality_type_routes import router as modality_type_router
from .nucleo_routes import router as nucleo_router
from .regulation_routes import router as regulation_router
from .seasons_routes import router as seasons_router
from .staff_routes import router as staff_router
from .student_routes import router as student_router
from .team_routes import router as team_router

__all__ = [
    "course_router",
    "modality_router",
    "modality_type_router",
    "nucleo_router",
    "staff_router",
    "student_router",
    "team_router",
    "regulation_router",
    "seasons_router",
]
