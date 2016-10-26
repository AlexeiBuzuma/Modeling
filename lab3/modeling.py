#!/usr/bin/env python3

import logging
import argparse
from steps.buffer import Buffer
from steps.channel import Channel
from steps.generator import Generator
from steps.base import TaskReceiver
from collections import Counter
from prettytable import PrettyTable
import numpy as np

logging.basicConfig(level=logging.ERROR)


# /-----------> Generator
# | /---------> Channal Pi1
# | | /-------> Buffer
# | | | /-----> Channel Pi2
# | | | |
# 0 0 0 0

STATES = [
    "0000",  # P1
    "1000",  # P2
    "0100",  # P3
    "1001",  # P4
    "1100",  # P5
    "0101",  # P6
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


def _parse_args():
    parser = argparse.ArgumentParser(description='Modeling')

    parser.add_argument("--count", dest="count", type=int, default=200000, help="Number of iterations")
    parser.add_argument("--pi1", dest="pi1", type=float, default=0.4)  #, required=True)
    parser.add_argument("--pi2", dest="pi2", type=float, default=0.8)

    return parser.parse_args()


def _build_chain(pi1, pi2):

    task_receiver = TaskReceiver([])

    channel2 = Channel([task_receiver, ], pi2, 'pi2')
    buffer = Buffer([channel2, ])
    channel1 = Channel([buffer, ], pi1, 'pi1')
    generator = Generator([channel1, ])

    return [generator, channel1, buffer, channel2], task_receiver


def calculate_theoretical_probability(p1, p2):

    n1 = 1 - p1
    n2 = 1 - p2

    matrix = np.array([
        [1,  1,  1,  1,  1,     1,   1,     1,       1,     1,     1,     1,  1,       1,    1, ],
        [1, -1,  0,  0,  0,     0,   0,     0,       0,     0,     0,     0,  0,       0,    0, ],
        [0,  1, -1, n2,  0,     0,   0,     0,       0,     0,     0,     0,  0,       0,    0, ],
        [0,  0, n1, -1,  0, n1*n2,   0,     0,       0,     0,     0,     0,  0,       0,    0, ],
        [0,  0, p1,  0, -1, p1*n2,   0,     0,       0,     0,     0,     0,  0,       0,    0, ],
        [0,  0,  0, p2, n1,    -1,  n2, n1*n2,   n1*n2,     0,    n1,     0,  0,       0,    0, ],
        [0,  0,  0,  0,  0, n1*p2,  -1,     0,       0, n1*n2,     0,     0,  0,       0,    0, ],
        [0,  0,  0,  0,  0, p1*p2,   0,    -1,       0, p1*n2,     0,     0,  0,       0,    0, ],
        [0,  0,  0,  0,  0,     0,   0, p1*p2, p1*p2-1,     0,     0, p1*n2,  0,   p1*n2,    0, ],
        [0,  0,  0,  0,  0,     0,  p2, n1*p2,   n1*p2,    -1,     0, n1*n2, n2,   n1*n2,   n2, ],
        [0,  0,  0,  0,  p1,    0,   0, p1*n2,   p1*n2,     0,  p1-1,     0,  0,       0,    0, ],
        [0,  0,  0,  0,  0,     0,   0,     0,       0, p1*p2,     0,    -1,  0,       0,    0, ],
        [0,  0,  0,  0,  0,     0,   0,     0,       0, n1*p2,     0,     0, -1,       0,    0, ],
        [0,  0,  0,  0,  0,     0,   0,     0,       0,     0,     0, p1*p2,  0, p1*p2-1,    0, ],
        [0,  0,  0,  0,  0,     0,   0,     0,       0,     0,     0, n1*p2, p2,   n1*p2, p2-1, ],
    ])


    b = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    return np.linalg.solve(matrix, b)


def main_loop():
    args = _parse_args()

    steps, task_receiver = _build_chain(args.pi1, args.pi2)

    reversed_steps = steps[:]
    reversed_steps.reverse()

    counter = Counter()
    count = args.count

    buffer_index = 2
    buffer_length = 0

    while count:
        logging.debug("Start of loop")

        for step in reversed_steps:
            step.tick()

        state = "".join(str(step.current_state) for step in steps)
        counter.update([state, ])

        if steps[buffer_index].current_state:
            buffer_length += 1

        logging.debug(state)
        count -= 1
        logging.debug("End of loop\n\n")

    from pprint import pprint
    pprint(dict(counter))
    field_names = ["State", "Count", "Theoretical Probability", "Results of Experiment"]
    table = PrettyTable(field_names)

    theoretical_probability = calculate_theoretical_probability(args.pi1, args.pi2)

    for index, state in enumerate(STATES):
        line = list()
        line.append(state)
        line.append(counter.get(state, 0))
        line.append(theoretical_probability[index])
        line.append(counter.get(state, 0) / args.count)

        table.add_row(line)

    print(table)

    theoretical_buffer_length = sum(theoretical_probability[index]
                                    for index, state in enumerate(STATES) if state[buffer_index] == "1")

    table = PrettyTable(["Name ", "Theoretical", "Experiment"])

    table.add_row(["Average lifetime   (Wc)", "", task_receiver.get_average_lifetime()])
    table.add_row(["Buffer length     (Lоч)", theoretical_buffer_length, buffer_length / args.count])
    table.add_row(["Absolute bandwidth  (A)", "", task_receiver.task_count / args.count])

    print(table)


if __name__ == '__main__':
    main_loop()