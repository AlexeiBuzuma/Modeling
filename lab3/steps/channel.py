from .base import Step
from random import uniform
import logging

EMPTY = 0
TASK_PROCESSING = 1
LOCKED = 2

logging.basicConfig(level = logging.WARNING)

# logging.basicConfig(level = logging.DEBUG)


class Channel(Step):
    def __init__(self, receiver_list, probability, name):
        super().__init__(receiver_list)

        self.name = name
        self._current_state = EMPTY
        self._probability = probability

    def is_ready_to_accept_task(self):
        return self._current_state == EMPTY

    def set_task(self):
        if not self.is_ready_to_accept_task():
            raise Exception("Task already processing")

        self._current_state = TASK_PROCESSING

    def tick(self):
        if self._current_state == EMPTY:
            return

        number = uniform(0, 1)
        if number >= self._probability:
            # self._current_state = EMPTY

            logging.debug("Channel '{}[{}]' executed with number {}".format(self.name, self._probability, number))
            if not self._receiver_list:
                self._current_state = EMPTY
                return

            for receiver in self._receiver_list:
                if receiver.is_ready_to_accept_task():
                    receiver.set_task()
                    self._current_state = EMPTY
                    return

            if self._receiver_list:
                self._current_state = LOCKED
                logging.debug("Channel '{}[{}]' locked with number {}".format(self.name, self._probability, number))

        logging.debug("Channel '{}[{}]' not executed with number {}".format(self.name, self._probability, number))


    @property
    def current_state(self):
        return self._current_state
