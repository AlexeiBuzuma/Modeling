from .base import Step
from random import uniform
import logging

EMPTY = 0
TASK_PROCESSING = 1
LOCKED = 2

logging.basicConfig(level=logging.ERROR)


class Channel(Step):
    def __init__(self, receiver_list, probability, name):
        super().__init__(receiver_list)

        self.name = name
        self._current_state = EMPTY
        self._probability = probability
        self._task = None

    def is_ready_to_accept_task(self):
        return self._current_state == EMPTY

    def set_task(self, task):
        if not self.is_ready_to_accept_task():
            raise Exception("Task already processing")

        self._current_state = TASK_PROCESSING
        self._task = task

    def tick(self):
        if self._current_state == EMPTY:
            return

        self._task.age += 1

        if self._current_state == LOCKED:
            for receiver in self._receiver_list:
                if receiver.is_ready_to_accept_task():
                    receiver.set_task(self._task)
                    self._task = None
                    self._current_state = EMPTY
                    return

        number = uniform(0, 1)
        if number >= self._probability:
            # self._current_state = EMPTY

            logging.debug("Channel '{}[{}]' executed with number {}".format(self.name, self._probability, number))

            for receiver in self._receiver_list:
                if receiver.is_ready_to_accept_task():
                    receiver.set_task(self._task)
                    self._task = None
                    self._current_state = EMPTY
                    return

            if self._receiver_list:
                self._current_state = LOCKED
                logging.debug("Channel '{}[{}]' locked with number {}".format(self.name, self._probability, number))

        logging.debug("Channel '{}[{}]' not executed with number {}".format(self.name, self._probability, number))

    @property
    def current_state(self):
        return self._current_state
