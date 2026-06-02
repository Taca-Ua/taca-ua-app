from django.db.models import QuerySet

from .models import Course


def list_courses() -> QuerySet[Course]:
    return Course.objects.all()


def get_course(course_id: str) -> QuerySet[Course]:

    course_stmt = Course.objects.filter(id=course_id)
    if not course_stmt.exists():
        raise Course.DoesNotExist(f"Course with id {course_id} does not exist.")

    return course_stmt
