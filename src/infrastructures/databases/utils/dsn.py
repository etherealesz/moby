def build_dsn(
    provider: str,
    driver: str,
    user: str,
    password: str,
    host: str,
    port: int,
    db_name: str,
    ssl_mode: str | None = None,
) -> str:
    """
    Builds a PostgreSQL DSN (Data Source Name) string.

    Args:
        provider (str): The database provider (e.g., "postgresql").
        driver (str): The database driver (e.g., "psycopg").
        user (str): The database user.
        password (str): The database password.
        host (str): The database host.
        port (int): The database port.
        database (str): The database name.

    Returns:
        str: The constructed DSN string.
    """

    dsn = f"{provider}+{driver}://{user}:{password}@{host}:{port}/{db_name}"
    if ssl_mode:
        dsn += f"?sslmode={ssl_mode}"

    return dsn
