from django.apps import AppConfig


class UcsbConfig(AppConfig):
    name = 'ucsb'

    def ready(self):
        print("Scheduler is running")
        from opt.utility.scheduler import opt_scheduler
        opt_scheduler()
        