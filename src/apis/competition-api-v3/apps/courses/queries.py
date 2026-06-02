from django.db.models import QuerySet

from .models import Course


def list_courses() -> QuerySet[Course]:
    return Course.objects.all()


def get_course(course_id: str) -> QuerySet[Course]:
    return Course.objects.filter(id=course_id)
