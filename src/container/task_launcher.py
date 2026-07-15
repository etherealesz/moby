from injector import Binder, Module, singleton

from infrastructures.task_launcher.base import TaskLauncher


class CTaskLauncherModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(TaskLauncher, to=TaskLauncher, scope=singleton)
