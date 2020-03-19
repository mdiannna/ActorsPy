from .actors import Actor, States, Work
from .requestor import Requestor


class RequestorRestartPolicy():
    def restart_requestor(self, requestor):
        name = requestor.get_name()

        requestor_to_be_restarted = Requestor(name)
        requestor_to_be_restarted.start()
        requestor_to_be_restarted.supervisor = requestor.get_supervisor
        requestor_to_be_restarted.printer_actor = requestor.get_printer_actor
        
        requestor.stop()

        return requestor_to_be_restarted

