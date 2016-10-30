import abc
from steps.base import TaskReceiver


STATES = [
    "0000",
    "1000",
    "0010",
    "1010",
    "0011",
    "1001",
    "1011",
    "0111",
    "1111",
    "2111",
]


GENERATOR_INDEX = 0
BUFFER_INDEX = 1
CHANHEL_PI1_INDEX = 2
CHANNEL_PI2_INDEX = 3


class Checker(metaclass=abc.ABCMeta):
    def __init__(self, pi1, pi2, count):
        self._pi1 = pi1
        self._pi2 = pi2
        self._count = count

    @abc.abstractproperty
    def checker_name(self):
        pass

    @abc.abstractmethod
    def check(self, chain):
        pass

    @abc.abstractmethod
    def get_experimental_results(self):
        pass

    @abc.abstractmethod
    def get_theoretical_results(self, theoretical_probability):
        pass


class AbsoluteBandwidthChecker(Checker):

    @property
    def checker_name(self):
        return "Absolute bandwidth  (A)"

    def check(self, chain):
        pass

    def get_theoretical_results(self, theoretical_probability):

        theoretical_bandwidth = 0

        for index, state in enumerate(STATES):
            if state[CHANHEL_PI1_INDEX] == "1":
                theoretical_bandwidth += theoretical_probability[index] * (1 - self._pi1)

            if state[CHANNEL_PI2_INDEX] == "1":
                theoretical_bandwidth += theoretical_probability[index] * (1 - self._pi2)

        return theoretical_bandwidth

    def get_experimental_results(self):
        return TaskReceiver.task_count / self._count


class AverageLifetimeChecker(Checker):

    @property
    def checker_name(self):
        return "Average lifetime   (Wc)"

    def check(self, **kwargs):
        pass

    def get_theoretical_results(self, theoretical_probability):
        return "None"

    def get_experimental_results(self):
        return TaskReceiver.get_average_lifetime()


class BufferLengthChecker(Checker):
    buffer_length = 0

    @property
    def checker_name(self):
        return "Buffer length     (Lоч)"

    def check(self, chain):
        if chain[BUFFER_INDEX].current_state != 0:
            self.buffer_length += 1

    def get_experimental_results(self):
        return self.buffer_length / self._count

    def get_theoretical_results(self, theoretical_probability):
        return sum(theoretical_probability[index]
                   for index, state in enumerate(STATES)
                   if state[BUFFER_INDEX] == "1")


class LockedProbabilityChecker(Checker):

    locked_state_counter = 0

    @property
    def checker_name(self):
        return "Locked Probability   Pбл"

    def check(self, chain):
        for step in chain:
            if step.current_state == 2:
                LockedProbabilityChecker.locked_state_counter += 1

    def get_theoretical_results(self, theoretical_probability):
        locked_probability = 0
        locked_state = "2"

        for index, state in enumerate(STATES):
            locked_probability += state.count(locked_state) * theoretical_probability[index]

        return locked_probability

    def get_experimental_results(self):
        return LockedProbabilityChecker.locked_state_counter / self._count
