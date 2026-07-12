from apps.courses.models import Course
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from shared.file_storage.minio_service import MinioService

from .models import Athlete

course_file_storage = MinioService("courses-proofs")
payment_file_storage = MinioService("payment-proofs")


@transaction.atomic
def create_athlete(
    name: str,
    student_number: str,
    course_id: str,
    course_proof_file: UploadedFile = None,
    payment_proof_file: UploadedFile = None,
) -> Athlete:

    if course_proof_file:
        # save the course proof file to Minio
        course_proof_file_path = course_file_storage.upload_file(course_proof_file)

    if payment_proof_file:
        # save the payment proof file to Minio
        try:
            payment_proof_file_path = payment_file_storage.upload_file(
                payment_proof_file
            )
        except Exception as e:
            # if there's an error while uploading the payment proof file, delete the course proof file if it was uploaded
            if course_proof_file:
                course_file_storage.delete_file(course_proof_file_path)
            raise e

    # create the athlete instance
    athlete = Athlete.objects.create(
        name=name,
        student_number=student_number,
        course_id=course_id,
        course_proof_file_url=course_proof_file_path if course_proof_file else None,
        payment_proof_file_url=payment_proof_file_path if payment_proof_file else None,
        is_member=payment_proof_file
        is not None,  # Set is_member to True if payment proof file is provided
    )

    return athlete


@transaction.atomic
def update_athlete(
    athlete_id: str,
    name: str = None,
    student_number: str = None,
    course_id: str = None,
    is_member: bool = None,
    course_proof_file: UploadedFile = None,
    course_proof_deleted: bool = False,
    payment_proof_file: UploadedFile = None,
    payment_proof_deleted: bool = False,
) -> Athlete:
    athlete = Athlete.objects.get(id=athlete_id)

    if name is not None:
        athlete.name = name
    if student_number is not None:
        athlete.student_number = student_number
    if course_id is not None:
        course = Course.objects.get(id=course_id)
        athlete.course = course
    if is_member is not None:
        athlete.is_member = is_member

    # Handle course proof file
    if course_proof_deleted:
        if athlete.course_proof_file_url:
            course_file_storage.delete_file(athlete.course_proof_file_url)
            athlete.course_proof_file_url = None
    elif course_proof_file:
        # If a new course proof file is provided, delete the old one and upload the new one
        if athlete.course_proof_file_url:
            course_file_storage.update_file(
                athlete.course_proof_file_url,
                course_proof_file,
            )
        else:
            athlete.course_proof_file_url = course_file_storage.upload_file(
                course_proof_file
            )

    # Handle payment proof file
    if payment_proof_deleted:
        if athlete.payment_proof_file_url:
            payment_file_storage.delete_file(athlete.payment_proof_file_url)
            athlete.payment_proof_file_url = None
    elif payment_proof_file:
        # If a new payment proof file is provided, delete the old one and upload the new one
        if athlete.payment_proof_file_url:
            payment_file_storage.update_file(
                athlete.payment_proof_file_url,
                payment_proof_file,
            )
        else:
            athlete.payment_proof_file_url = payment_file_storage.upload_file(
                payment_proof_file
            )

    athlete.save()

    return athlete


@transaction.atomic
def delete_athlete(athlete_id: str) -> None:
    athlete = Athlete.objects.get(id=athlete_id)

    # delete the athlete after emitting the event
    athlete.delete()


@transaction.atomic
def sync_athletes_membership_status(athlete_numbers: list[str]) -> None:
    """Update the membership status of athletes based on their student numbers."""

    # set all athletes to not members first
    Athlete.objects.update(is_member=False)

    # then set the specified athletes to members
    Athlete.objects.filter(student_number__in=athlete_numbers).update(is_member=True)
