from typing import Any, Callable, Dict, Mapping, Type, TypeVar

import httpx

from infrastructures.http.client_hooks import retry_hook

DEFAULT_TIMEOUT = httpx.Timeout(10.0)
DEFAULT_RETRIES = 3

T = TypeVar("T", bound=httpx.AsyncClient)


def create_http_client(
    class_: Type[T],
    *,
    base_url: str,
    timeout: httpx.Timeout = DEFAULT_TIMEOUT,
    follows_redirects: bool = False,
    headers: Mapping[str, str] | None = None,
    params: Mapping[str, str] | None = None,
    cookies: Dict[str, str] | None = None,
    event_hooks: Mapping[str, list[Callable[..., Any]]] | None = None,
    retries: int = DEFAULT_RETRIES,
    **kwargs,
) -> T:
    """
    Create and configure an HTTPX AsyncClient with custom settings.

    Args:
        base_url (str): The base URL for the HTTP client.
        timeout (httpx.Timeout, optional): Timeout settings for the client. Defaults to DEFAULT_TIMEOUT.
        follows_redirects (bool, optional): Whether to follow redirects. Defaults to False.
        headers (Mapping[str, str], optional): Default headers for the client. Defaults to None
        params (Mapping[str, str], optional): Default query parameters for the client. Defaults to None.
        cookies (Dict[str, str], optional): Default cookies for the client. Defaults to None
        event_hooks (Mapping[str, list[Callable[..., Any]]], optional): Event hooks for the client. Defaults to None.
        retries (int, optional): Number of retry attempts for failed requests. Defaults to DEFAULT_RETRIES.
        **kwargs: Additional keyword arguments for the HTTPX AsyncClient.

    Returns:
        httpx.AsyncClient: Configured HTTPX AsyncClient instance.
    """

    client = class_(
        base_url=base_url,
        timeout=timeout,
        headers=headers,
        params=params,
        cookies=cookies,
        follow_redirects=follows_redirects,
        event_hooks=event_hooks,
        **kwargs,
    )

    hooks: Mapping[str, list[Callable[..., Any]]] = {
        "request": [],
        "response": [lambda response: retry_hook(response, retries)],
    }
    if event_hooks:
        for key, hook_list in event_hooks.items():
            hooks[key].extend(hook_list)

    client.event_hooks = hooks

    return client
