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
            #     print(query["sql"])
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
