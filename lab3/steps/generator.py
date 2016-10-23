from .base import Step
import logging

EMPTY = 0
FILLED = 1
LOCKED = 2


logging.basicConfig(level = logging.DEBUG)


class Generator(Step):
    def __init__(self, receiver_list):
        super().__init__(receiver_list)
        self._current_state = EMPTY

    @property
    def current_state(self):
        return self._current_state

    def tick(self):
        if self._current_state == EMPTY:
            self._current_state = FILLED
            return

        for receiver in self._receiver_list:
            if receiver.is_ready_to_accept_task():
                receiver.set_task()
                self._current_state = EMPTY
                return

        self._current_state = LOCKED
