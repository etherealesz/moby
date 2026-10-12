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
    dsn = f"{provider}+{driver}://{user}:{password}@{host}:{port}/{db_name}"
    if ssl_mode:
        dsn += f"?sslmode={ssl_mode}"

    return dsn
