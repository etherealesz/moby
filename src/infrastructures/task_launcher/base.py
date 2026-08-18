import asyncio
from typing import Any, Callable, Coroutine, Set

from core.logger.factory import create_app_logger

logger = create_app_logger()


class TaskLauncher:
    def __init__(self):
        self._active_tasks: Set[asyncio.Task] = set()

    def fire_and_forget(
        self,
        coroutine: Coroutine[Any, Any, Any],
        on_task_completed: Callable[[Any], None] | None = None,
        on_task_failed: Callable[[Exception], None] | None = None,
    ) -> None:
        """
        Launches a coroutine as a fire-and-forget task.

        Args:
            coroutine (Coroutine[Any, Any, Any]): The coroutine(s) to be launched as fire-and-forget task.
            on_task_completed (Callable | None): An optional callback function to be called when the task is completed.
            on_task_failed (Callable[[Exception], None] | None): An optional callback function to be called when the task has failed with an exception.
        """

        task = asyncio.create_task(coroutine)
        self._active_tasks.add(task)
        task.add_done_callback(
            lambda t: self._handle_task_result(t, on_task_completed, on_task_failed)
        )

    def _handle_task_result(
        self,
        task: asyncio.Task,
        on_task_completed: Callable[[Any], None] | None = None,
        on_task_failed: Callable[[Exception], None] | None = None,
    ) -> None:
        """
        Handles the result of a completed task, logging any exceptions that occurred.

        Args:
            task (asyncio.Task): The completed task whose result is to be handled.
            on_task_completed (Callable | None): An optional callback function to be called when the task is completed.
            on_task_failed (Callable | None): An optional callback function to be called when the task has failed with an exception.
        """

        self._active_tasks.discard(task)

        try:
            result = task.result()
            if on_task_completed:
                on_task_completed(result)
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            if on_task_failed:
                on_task_failed(exc)
            else:
                logger.error(
                    "Fire-and-forget task raised an exception",
                    exc_info=True,
                    extra={"fn": task.get_name()},
                )

    async def wait_for_tasks_until_completed(self) -> None:
        """
        Waits for all active fire-and-forget tasks to complete.
        """

        if not self._active_tasks:
            return
        await asyncio.gather(*self._active_tasks, return_exceptions=True)
