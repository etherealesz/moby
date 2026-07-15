import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


async def retry_hook(response: httpx.Response, retries: int):
    """
    A hook to retry HTTP requests on failure using tenacity.

    Args:
        response (httpx.Response): The HTTP response object.
        retries (int): Number of retry attempts.

    Returns:
        httpx.Response: The HTTP response object after retries.
    """

    @retry(
        retry=retry_if_exception_type(httpx.HTTPError),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
        stop=stop_after_attempt(retries),
        reraise=True,
    )
    async def _retry():
        response.raise_for_status()
        return response

    return await _retry()
