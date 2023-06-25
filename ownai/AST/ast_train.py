#!/usr/bin/env python3

import sys
from pathlib import Path
from AST.ast_node import Weights, CursorNode
from AST.ast_parser import parse_cpp_tree
import tensorflow as tf


def main(argv):
    if len(argv) < 2:
        print(f"usage: {argv[0]} /path/to/filename.cpp [weights.json]")
        exit(0)

    filename_cpp = Path(argv[1])  # ToDo: must be a directory with cpp files in it
    if not filename_cpp.exists():
        print(f"file '{argv[1]}' does not exist")
        exit(1)
    filename_weights = Path("weights.json")
    if len(argv) > 2:
        filename_weights = Path(argv[2])

    if filename_weights.exists():
        weights = Weights.load(filename_weights)
    else:
        print(f"Weights file '{str(filename_weights)}' does not exist - creating new weights!")
        weights = Weights()

    tree: CursorNode = parse_cpp_tree(str(filename_cpp))

    forward_pass: tf.Tensor = tree.encode(weights)
    prediction_errors = tree.perturbe(0.15, weights, forward_pass)
    # Find gradients
    print(prediction_errors)


if __name__ == "__main__":
    main(sys.argv)
