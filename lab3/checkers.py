import abc
from steps.base import TaskReceiver

STATES = [
    "0000",  # P1
    "1000",  # P2
    "0100",  # P3
    "1001",  # P4
    "1100",  # P5
    "0101",  # P6
    # P7 skipped
    "1011",  # P8
    "1101",  # P9
    "2101",  # P10
    "0111",  # P11
    "2100",  # P12
    "1111",  # P13
    "1211",  # P14
    "2111",  # P15
    "2211",  # P16
]


GENERATOR_INDEX = 0
CHANHEL_PI1_INDEX = 1
BUFFER_INDEX = 2
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
            if state.endswith("1"):
                theoretical_bandwidth += theoretical_probability[index] * (1 - self._pi2)

        return theoretical_bandwidth

    def get_experimental_results(self):
        return TaskReceiver.task_count / self._count


class AverageNumberOfTasks(Checker):
    number_of_task = 0
    number_of_ticks = 0

    @property
    def checker_name(self):
        return "Average number of tasks "

    def check(self, chain):
        self.number_of_ticks += 1

        for step in chain:
            if step.current_state != 0:
                self.number_of_task += 1

    @classmethod
    def get_theoretical_results(self, theoretical_probability):
        average_number_of_tasks = 0
        for index, state in enumerate(STATES):
            average_number_of_tasks += (4 - state.count("0")) * theoretical_probability[index]

        return average_number_of_tasks

    def get_experimental_results(self):
        return self.number_of_task / self.number_of_ticks


class AverageLifetimeChecker(Checker):

    @property
    def checker_name(self):
        return "Average lifetime   (Wc)"

    def check(self, chain):
        pass

    @classmethod
    def get_theoretical_results(cls, theoretical_probability):
        intensity = 0
        for index, state in enumerate(STATES):
            if state[GENERATOR_INDEX] == "0":
                intensity += theoretical_probability[index]

        return AverageNumberOfTasks.get_theoretical_results(theoretical_probability) / intensity

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
