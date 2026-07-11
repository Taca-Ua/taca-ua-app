import os

import filetype
from rest_framework import serializers


def count_queries(func):
    """Decorator to count the number of database queries executed during a function call."""

    def wrapper(*args, **kwargs):
        from django.db import connection

        initial_query_count = len(connection.queries)
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            raise e
        finally:
            final_query_count = len(connection.queries)
            print(
                f"Number of queries executed: {final_query_count - initial_query_count}"
            )
            print("Executed queries:")
            for query in connection.queries[initial_query_count:final_query_count]:
                print(query["sql"])
        return result

    return wrapper


def count_queries_context(show_sql: bool = True):
    """Context manager to count the number of database queries executed within a block of code."""

    from django.db import connection

    class QueryCounter:
        def __enter__(self):
            self.initial_query_count = len(connection.queries)

        def __exit__(self, exc_type, exc_val, exc_tb):
            final_query_count = len(connection.queries)
            print(
                f"Number of queries executed: {final_query_count - self.initial_query_count}"
            )
            if show_sql:
                print("Executed queries:")
                for query in connection.queries[
                    self.initial_query_count : final_query_count
                ]:
                    print(query["sql"])

    return QueryCounter()


class ExtensionSensitiveFileField(serializers.FileField):
    """
    A custom FileField that allows for case-insensitive file extension validation.
    """

    ALLOWED_EXTENSIONS = {
        ".pdf": "application/pdf",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
    }

    def __init__(self, *args, **kwargs):
        self.allowed_extensions = kwargs.pop("allowed_extensions", None)

        if any(
            ext not in self.ALLOWED_EXTENSIONS for ext in self.allowed_extensions or []
        ):
            raise ValueError(
                f"Allowed extensions must be one of {list(self.ALLOWED_EXTENSIONS.keys())}"
            )

        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        print(f"Validating file: {data.name}")

        # Call the parent method to handle the file upload
        file = super().to_internal_value(data)

        # Validate the file extension if allowed_extensions is provided
        if not self.allowed_extensions:
            return file

        extension = os.path.splitext(file.name)[1].lower()
        if extension not in self.allowed_extensions:
            raise serializers.ValidationError(f"Invalid file extension '{extension}'.")

        kind = filetype.guess(data.read(1024))
        data.seek(0)  # Reset the file pointer to the beginning after reading

        if kind is None:
            raise serializers.ValidationError(
                f"Could not determine the file type for extension '{extension}'."
            )

        if kind.mime != self.ALLOWED_EXTENSIONS[extension]:
            raise serializers.ValidationError(
                f"Invalid file type '{kind.mime}' for extension '{extension}'."
            )

        return file
