#!/usr/bin/env python3

import logging
import argparse
from steps.buffer import Buffer
from steps.channel import Channel
from steps.generator import Generator
from collections import Counter
from prettytable import PrettyTable

logging.basicConfig(level = logging.WARNING)

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
    parser.add_argument("--pi1", dest="pi1", type=float, default=0.75)  #, required=True)
    parser.add_argument("--pi2", dest="pi2", type=float, default=0.6)

    return parser.parse_args()


def _build_chain(pi1, pi2):

    channel1 = Channel([], pi1, 'pi1')
    channel2 = Channel([], pi2, 'pi2')

    buffer = Buffer([channel1, channel2])

    generator = Generator([buffer, ])

    return generator, buffer, [channel1, channel2]


def calculate_theoretical_probability():
    import numpy as np

    pi1 = 0.75
    pi2 = 0.6

    _pi1 = 1 - pi1
    _pi2 = 1 - pi2

    matrix = np.array([
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, -1, _pi1, 0, _pi1 * _pi2, 0, 0, 0, 0, 0],
        [0, 1, -1, _pi1, 0, _pi2, _pi1 * _pi2, _pi1 * _pi2, 0, 0],
        [0, 0, pi1, -1, pi1 * _pi2, 0, 0, 0, 0, 0],
        [0, 0, 0, pi1, -1, pi2, pi1 * pi2, 0, _pi1 * _pi2, _pi1 * _pi2],
        [0, 0, 0, 0, _pi1 * pi2, -1, 0, 0, 0, 0],
        [0, 0, 0, 0, pi1 * pi2, 0, -1, _pi1 * pi2 + _pi2 * pi1, 0, 0],
        [0, 0, 0, 0, 0, 0, pi1 * pi2, -1, _pi1 * pi2 + _pi2 * pi1, _pi1 * pi2 + _pi2 * pi1],
        [0, 0, 0, 0, 0, 0, 0, pi1 * pi2, -1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, pi1 * pi2, -1 + pi1 * pi2]
    ])

    b = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    return np.linalg.solve(matrix, b)


def main_loop():
    args = _parse_args()

    generator, buffer, channels = _build_chain(args.pi1, args.pi2)
    counter = Counter()
    count = args.count

    while count:
        logging.debug("Start of loop")
        for channel in channels:
            channel.tick()

        buffer.tick()
        generator.tick()

        state = "{}{}{}{}".format(generator.current_state, buffer.current_state(),
                                  channels[0].current_state, channels[1].current_state)
        counter.update({state: 1})
        logging.debug(state)
        count -= 1
        logging.debug("End of loop\n\n")

    field_names = ["State", "Count", "Theoretical Probability", "Results of Experiment"]
    table = PrettyTable(field_names)

    theoretical_probability = calculate_theoretical_probability()

    for index, state in enumerate(STATES):
        line = list()
        line.append(state)
        line.append(counter.get(state, 0))
        line.append(theoretical_probability[index])
        line.append(counter.get(state, 0) / args.count)

        table.add_row(line)

    print(table)


if __name__ == '__main__':
    main_loop()