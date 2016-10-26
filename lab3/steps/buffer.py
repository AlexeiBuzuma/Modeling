from .base import Step
import logging

EMPTY = 0
FILLED = 1

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)


class Buffer(Step):
    def __init__(self, receiver_list):
        super().__init__(receiver_list)
        self._current_state = EMPTY
        self._task = None

    @property
    def current_state(self):
        return self._current_state

    def tick(self):
        if self._current_state == FILLED:
            self._task.age += 1
            for receiver in self._receiver_list:
                if receiver.is_ready_to_accept_task():
                    receiver.set_task(self._task)
                    self._task = None
                    self._current_state = EMPTY

                    return

    def set_task(self, task):
        for receiver in self._receiver_list:
            if receiver.is_ready_to_accept_task():
                logging.debug("Pass task throw buffer")
                receiver.set_task(task)
                return

        if self._current_state == EMPTY:
            logging.debug("Set task to buffer")
            self._task = task
            self._current_state = FILLED
            return

        raise Exception("Can't set task")

    def is_ready_to_accept_task(self):
        if self._current_state == EMPTY:
            return True

        for receiver in self._receiver_list:
            if receiver.is_ready_to_accept_task():
                return True

        return False