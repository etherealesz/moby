import asyncio

from core.exceptions.network import RequestCancelledError


class RequestCancelledMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Shared queue for the request messages
        queue = asyncio.Queue()

        # Task function that listens for disconnect events and cancels the
        # handler task if a disconnect is detected.
        async def message_poller(sentinel, handler_task):
            nonlocal queue
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    handler_task.cancel()
                    return sentinel

                await queue.put(message)

        # Create two main tasks, the handler task that processes the request
        # and the message poller that listens for disconnect events.
        # This approach allows the handler to be cancelled immediately when
        # a disconnect is detected, without waiting for the handler to check
        # for cancellation.
        # This approach has a catch, the CPU usage expected to be higher
        # because the message poller is need to be running in every request.
        sentinel = object()
        task = self.app(scope, queue.get, send)
        handler_task = asyncio.create_task(task)
        asyncio.create_task(message_poller(sentinel, handler_task))

        try:
            return await handler_task
        except asyncio.CancelledError:
            # Raise a custom exception to indicate that the request was cancelled,
            # otherwise, a RuntimeError("No response returned.") will be raised
            # when the handler task is cancelled.
            raise RequestCancelledError
