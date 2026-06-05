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
            # print("Executed queries:")
            # for query in connection.queries[initial_query_count:final_query_count]:
            #     print(query['sql'])
        return result

    return wrapper
