import abc


class Task:
    def __init__(self):
        self.age = 0


class Step(metaclass=abc.ABCMeta):

    def __init__(self, receiver_list):
        self._receiver_list = receiver_list

    @abc.abstractproperty
    def current_state(self):
        pass

    @abc.abstractmethod
    def tick(self):
        pass


class TaskReceiver(Step):
    total_lifetime = 0
    task_count = 0

    def set_task(self, task):
        self.total_lifetime += task.age
        self.task_count += 1

    def is_ready_to_accept_task(self):
        return True

    def get_average_lifetime(self):
        return self.total_lifetime / self.task_count

    def tick(self):
        pass

    @property
    def current_state(self):
        return 0
