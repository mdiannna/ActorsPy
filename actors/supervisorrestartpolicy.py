###############################
# Supervisor Restart Policy
###############################

from .actors import Actor, States, Work
from .workersupervisor import WorkerSupervisor


class SupervisorRestartPolicy():
    def restart(self, supervisor):
        workers_children = []

        while(not supervisor.workers.empty()):
            worker = supervisor.workers.get()
            new_worker = worker.get_name()
            worker.stop()

            workers_children.append(new_worker)

        supervisor_name = supervisor.get_name()
        directory = supervisor.get_directory()
        supervisor.stop()


        new_supervisor = WorkerSupervisor(supervisor_name, directory, workers_array=workers_children)
        new_supervisor.start()
        return new_supervisor


