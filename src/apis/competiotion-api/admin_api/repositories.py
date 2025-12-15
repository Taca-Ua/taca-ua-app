"""
Repository pattern for database operations
"""

from typing import List, Optional

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from .models import User


class UserRepository:
    """Repository for User model operations"""

    @staticmethod
    def create(
        username: str,
        email: str,
        password: str,
        role: str = "nucleo",
        course_id: Optional[int] = None,
        course_abbreviation: Optional[str] = None,
        full_name: Optional[str] = None,
    ) -> User:
        """
        Create a new user

        Args:
            username: Unique username
            email: User email
            password: Plain text password (will be hashed)
            role: User role ('nucleo' or 'geral')
            course_id: Course ID (required for nucleo admins)
            course_abbreviation: Course abbreviation
            full_name: Full name of the user

        Returns:
            Created User instance

        Raises:
            ValueError: If validation fails
        """
        if role == "nucleo" and not course_id:
            raise ValueError("course_id is required for nucleo administrators")

        if User.objects.filter(username=username).exists():
            raise ValueError("Username already exists")

        if User.objects.filter(email=email).exists():
            raise ValueError("Email already exists")

        user = User.objects.create(
            username=username,
            email=email,
            role=role,
            course_id=course_id,
            course_abbreviation=course_abbreviation,
            full_name=full_name or "",
        )
        user.set_password(password)
        user.save()

        return user

    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        """
        Get user by ID

        Args:
            user_id: User ID

        Returns:
            User instance or None if not found
        """
        try:
            return User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_by_username(username: str) -> Optional[User]:
        """
        Get user by username

        Args:
            username: Username

        Returns:
            User instance or None if not found
        """
        try:
            return User.objects.get(username=username)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        """
        Get user by email

        Args:
            email: User email

        Returns:
            User instance or None if not found
        """
        try:
            return User.objects.get(email=email)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_all() -> List[User]:
        """
        Get all users

        Returns:
            List of all User instances
        """
        return list(User.objects.all())

    @staticmethod
    def get_by_role(role: str) -> List[User]:
        """
        Get users by role

        Args:
            role: User role ('nucleo' or 'geral')

        Returns:
            List of User instances with the specified role
        """
        return list(User.objects.filter(role=role))

    @staticmethod
    def get_nucleo_admins() -> List[User]:
        """
        Get all nucleo administrators

        Returns:
            List of nucleo admin User instances
        """
        return UserRepository.get_by_role("nucleo")

    @staticmethod
    def get_geral_admins() -> List[User]:
        """
        Get all geral administrators

        Returns:
            List of geral admin User instances
        """
        return UserRepository.get_by_role("geral")

    @staticmethod
    @transaction.atomic
    def update(
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        full_name: Optional[str] = None,
        course_id: Optional[int] = None,
        course_abbreviation: Optional[str] = None,
    ) -> Optional[User]:
        """
        Update user

        Args:
            user_id: User ID
            username: New username (optional)
            email: New email (optional)
            password: New password (optional, will be hashed)
            full_name: New full name (optional)
            course_id: New course ID (optional)
            course_abbreviation: New course abbreviation (optional)

        Returns:
            Updated User instance or None if not found

        Raises:
            ValueError: If validation fails
        """
        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return None

        if username and username != user.username:
            if User.objects.filter(username=username).exists():
                raise ValueError("Username already exists")
            user.username = username

        if email and email != user.email:
            if User.objects.filter(email=email).exists():
                raise ValueError("Email already exists")
            user.email = email

        if password:
            user.set_password(password)

        if full_name is not None:
            user.full_name = full_name

        if course_id is not None:
            user.course_id = course_id

        if course_abbreviation is not None:
            user.course_abbreviation = course_abbreviation

        user.save()
        return user

    @staticmethod
    @transaction.atomic
    def delete(user_id: int) -> bool:
        """
        Delete user

        Args:
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return True
        except ObjectDoesNotExist:
            return False

    @staticmethod
    def exists(user_id: int) -> bool:
        """
        Check if user exists

        Args:
            user_id: User ID

        Returns:
            True if user exists, False otherwise
        """
        return User.objects.filter(id=user_id).exists()