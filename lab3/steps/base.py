import abc


class Step(metaclass=abc.ABCMeta):

    def __init__(self, receiver_list):
        self._receiver_list = receiver_list

    @abc.abstractproperty
    def current_state(self):
        pass

    @abc.abstractmethod
    def tick(self):
        pass