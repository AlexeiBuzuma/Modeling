#!/usr/bin/env python3

import logging
import argparse
from steps.buffer import Buffer
from steps.channel import Channel
from steps.generator import Generator
from steps.base import TaskReceiver
from checkers import Checker, BufferLengthChecker, AbsoluteBandwidthChecker, AverageLifetimeChecker, LockedProbabilityChecker
from collections import Counter
from prettytable import PrettyTable
import numpy as np


logging.basicConfig(level=logging.ERROR)


# /-----------> Generator
# | /---------> Buffer
# | | /-------> Channel Pi1
# | | | /-----> Channel Pi2
# | | | |
# 0 0 0 0



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


def _parse_args():
    parser = argparse.ArgumentParser(description='Modeling')

    parser.add_argument("--count", dest="count", type=int, default=200000, help="Number of iterations")
    parser.add_argument("--pi1", dest="pi1", type=float, default=0.75)
    parser.add_argument("--pi2", dest="pi2", type=float, default=0.6)

    return parser.parse_args()


class Experiment:

    def __init__(self, pi1, pi2, count):
        self._count = count
        self._pi1 = pi1
        self._pi2 = pi2

        self._checkers = list()

        self.results = Counter()
        self.theoretical_results = self._calculate_theoretical_probability()

    def add_checker(self, checker):

        if issubclass(checker, Checker):
            raise AttributeError("Checker should be a subclass of 'Checker'.")

        if checker in self._checkers:
            raise AttributeError("Checker with name '{}' already exists".format(checker.checker_name))

        self._checkers.append(checker)

    def _build_chain(self):
        task_receiver = TaskReceiver([])

        channel2 = Channel([task_receiver, ], self._pi2, 'pi2')
        channel1 = Channel([task_receiver, ], self._pi1, 'pi1')

        buffer = Buffer([channel1, channel2, ])
        generator = Generator([buffer, ])

        return [generator, buffer, channel1, channel2], task_receiver

    def _calculate_theoretical_probability(self):

        pi1 = self._pi1
        pi2 = self._pi2

        _pi1 = 1 - pi1
        _pi2 = 1 - pi2

        matrix = np.array([
            [1,    1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1,   -1, _pi1, 0, _pi1 * _pi2, 0, 0, 0, 0, 0],
            [0,    1, -1, _pi1, 0, _pi2, _pi1 * _pi2, _pi1 * _pi2, 0, 0],
            [0,    0, pi1, -1, pi1 * _pi2, 0, 0, 0, 0, 0],
            [0,    0, 0, pi1, -1, pi2, pi1 * pi2, 0, _pi1 * _pi2, _pi1 * _pi2],
            [0, 0, 0, 0, _pi1 * pi2, -1, 0, 0, 0, 0],
            [0, 0, 0, 0, pi1 * pi2, 0, -1, _pi1 * pi2 + _pi2 * pi1, 0, 0],
            [0, 0, 0, 0, 0, 0, pi1 * pi2, -1, _pi1 * pi2 + _pi2 * pi1, _pi1 * pi2 + _pi2 * pi1],
            [0, 0, 0, 0, 0, 0, 0, pi1 * pi2, -1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, pi1 * pi2, -1 + pi1 * pi2]
        ])
        #
        # matrix = np.array([
        #     [1,  1,  1,  1,  1,     1,   1,     1,       1,     1,     1,     1,  1,       1,    1, ],  # P1
        #     [1, -1,  0,  0,  0,     0,   0,     0,       0,     0,     0,     0,  0,       0,    0, ],  # P2
        #     [0,  1, -1, n2,  0,     0,   0,     0,       0,     0,     0,     0,  0,       0,    0, ],  # P3
        #     [0,  0, n1, -1,  0, n1*n2,   0,     0,       0,     0,     0,     0,  0,       0,    0, ],  # P4
        #     [0,  0, p1,  0, -1, p1*n2,   0,     0,       0,     0,     0,     0,  0,       0,    0, ],  # P5
        #     [0,  0,  0, p2, n1,    -1,  n2, n1*n2,   n1*n2,     0,    n1,     0,  0,       0,    0, ],  # P6
        #     [0,  0,  0,  0,  0, n1*p2,  -1,     0,       0, n1*n2,     0,     0,  0,       0,    0, ],  # P8
        #     [0,  0,  0,  0,  0, p1*p2,   0,    -1,       0, p1*n2,     0,     0,  0,       0,    0, ],  # P9
        #     [0,  0,  0,  0,  0,     0,   0, p1*p2, p1*p2-1,     0,     0, p1*n2,  0,   p1*n2,    0, ],  # P10
        #     [0,  0,  0,  0,  0,     0,  p2, n1*p2,   n1*p2,    -1,     0, n1*n2, n2,   n1*n2,   n2, ],  # P11
        #     [0,  0,  0,  0,  p1,    0,   0, p1*n2,   p1*n2,     0,  p1-1,     0,  0,       0,    0, ],  # P12
        #     [0,  0,  0,  0,  0,     0,   0,     0,       0, p1*p2,     0,    -1,  0,       0,    0, ],  # P13
        #     [0,  0,  0,  0,  0,     0,   0,     0,       0, n1*p2,     0,     0, -1,       0,    0, ],  # P14
        #     [0,  0,  0,  0,  0,     0,   0,     0,       0,     0,     0, p1*p2,  0, p1*p2-1,    0, ],  # P15
        #     [0,  0,  0,  0,  0,     0,   0,     0,       0,     0,     0, n1*p2, p2,   n1*p2, p2-1, ],  # P16
        #     # P1 P2  P3  P4  P5     P6   P8     P9       P10    P11    P12   P13  P14     P15    P16
        # ])

        b = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ])
        return np.linalg.solve(matrix, b)

    def run(self):
        steps, task_receiver = self._build_chain()

        reversed_steps = steps[:]
        reversed_steps.reverse()

        count = self._count

        while count:
            logging.debug("Start of loop")

            for step in reversed_steps:
                step.tick()

            state = "".join(str(step.current_state) for step in steps)
            self.results.update([state, ])

            for checker in self._checkers:
                checker.check(steps)

            logging.debug(state)
            count -= 1
            logging.debug("End of loop\n\n")

        return dict(self.results)


def print_results_of_experiment(experiment, checkers):
    field_names = ["State", "Count", "Theoretical Probability", "Results of Experiment"]
    table = PrettyTable(field_names)

    theoretical_probability = experiment.theoretical_results

    for index, state in enumerate(STATES):
        line = list()
        line.append(state)
        line.append(experiment.results.get(state, 0))
        line.append(theoretical_probability[index])
        line.append(experiment.results.get(state, 0) / experiment._count)

        table.add_row(line)

    print(table)

    table = PrettyTable(["Name ", "Theoretical", "Experiment"])
    for checker in checkers:
        table.add_row([checker.checker_name,
                       checker.get_theoretical_results(experiment.theoretical_results),
                       checker.get_experimental_results()])

    print(table)


def main():
    args = _parse_args()

    # Create Checkers
    buffer_length_checker = BufferLengthChecker(args.pi1, args.pi2, args.count)
    bandwidth_checker = AbsoluteBandwidthChecker(args.pi1, args.pi2, args.count)
    average_lifetime_checker = AverageLifetimeChecker(args.pi1, args.pi2, args.count)
    locked_probability_checker = LockedProbabilityChecker(args.pi1, args.pi2, args.count)

    experiment = Experiment(args.pi1, args.pi2, args.count)
    experiment.add_checker(buffer_length_checker)
    # experiment.add_checker(bandwidth_checker)
    # experiment.add_checker(average_lifetime_checker)
    experiment.add_checker(locked_probability_checker)

    experiment.run()

    print_results_of_experiment(experiment, [buffer_length_checker, bandwidth_checker, average_lifetime_checker, locked_probability_checker])

if __name__ == '__main__':
    main()