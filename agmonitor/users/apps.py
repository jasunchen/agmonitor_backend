from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "agmonitor.users"
    verbose_name = _("Users")

    def ready(self):
        print("Scheduler is running")
        from opt.utility.scheduler import start
        start()
        try:
            import agmonitor.users.signals  # noqa F401
        except ImportError:
            pass
