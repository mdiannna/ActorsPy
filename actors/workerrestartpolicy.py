from .actors import Actor, States, Work
from .worker import Worker

class WorkerRestartPolicy():
    def restart_worker(self, current_worker):
        name = current_worker.get_name()
        directory = current_worker.get_directory()

        worker_to_be_restarted = Worker(name, directory)
        worker_to_be_restarted.start()

        current_worker.stop()
        return worker_to_be_restarted
