from __future__ import annotations

import numpy as np
import tensorflow as tf
from typing import Any, Final
from clang.cindex import Cursor, Token
import json

FEATURES_AMNT: Final[int] = 512  # 1024
CURSOR_KIND_AMNT: Final[int] = 700
CURSOR_KIND_EMB: Final[int] = 10
TOKEN_KIND_AMNT: Final[int] = 700
TOKEN_KIND_EMB: Final[int] = 10
BINARY_FLAGS: Final[int] = 16
SPELLING_FEATURES: Final[int] = 100
DYNAMIC_FLAGS: Final[int] = 2

class EncodeWeights:
    input2features: tf.Variable  # FEATURES_AMNT x (KIND_AMNT + BINARY_FLAGS + SPELLING_FEATURES)
    children2features: tf.Variable  # FEATURES_AMNT x FEATURES_SIZE

    def __init__(self):
        # shape1 = [FEATURES_AMNT, KIND_AMNT + BINARY_FLAGS + SPELLING_FEATURES]
        # self.input2features = tf.Variable(initial_value=tf.random.normal(shape=shape1), shape=shape1, validate_shape=True, trainable=True)
        # shape2 = [FEATURES_AMNT, FEATURES_AMNT]
        # self.children2features = tf.Variable(initial_value=tf.random.normal(shape=shape2), shape=shape2, validate_shape=True, trainable=True)
        pass

class DecodeWeights:
    # in order to decode unknown node, first we need to predict its kind (which dependes on the parents kind)
    features2child_kind: tf.Variable  # (FEATURES_AMNT + 1) x KIND_AMNT predict kind of particular child

    features2children: tf.Variable  #
    features2sibling: tf.Variable
    # features2spelling: tf.Tensor # FEATURES_AMNT x KIND_AMNT
    # features2binary_flags: tf.Tensor # FEATURES_AMNT x KIND_AMNT

    def __init__(self):
        # shape1 = [FEATURES_AMNT + 1, KIND_AMNT]
        # self.features2child_kind = tf.Variable(initial_value=tf.random.normal(shape=shape1), shape=shape1, validate_shape=True, trainable=True)
        pass



# all learnable weights
class Weights:
    _encode: dict[int, EncodeWeights]  # each kind has its own encoding weight
    _decode: dict[int, DecodeWeights]  # each kind has its own decoding weight
    _unknown: tf.Variable | None = None # single instance of tf.Tensor describing any unknown node

    def encode(self, kind : int) -> EncodeWeights:
        if kind not in self._encode:
            self._encode[kind] = EncodeWeights()
        return self._encode[kind]

    def decode(self, kind : int) -> DecodeWeights:
        if kind not in self._decode:
            self._decode[kind] = DecodeWeights()
        return self._decode[kind]

    def unknown(self) -> tf.Variable:
        if self._unknown is None:
            self._unknown = tf.Variable(trainable=True, shape=(FEATURES_AMNT))
        return self._unknown

    def save(self, json_filename):
        with open(json_filename, "w") as write_file:
            weights_dict = {"encode": self._encode,
                         "decode": self._decode,
                         "unknown": self._unknown,
                         }
            json.dump(weights_dict, write_file, indent=4)

    @staticmethod
    def load(json_filename):
        with open(json_filename, "r") as read_file:
            weights_dict = json.load(read_file)
            weights = Weights()
            weights._encode=weights_dict["encode"]
            weights._decode=weights_dict["decode"]
            weights._unknown=weights_dict["unknown"]
            return weights


class Location:
    file: str
    line: int
    column: int

    def __init__(self, location : Any = None):
        if location is not None:
            self.file = location.file
            self.column = location.column
            self.line = location.line


class AstNode:
    level: int
    order: int
    kind: int | None = None
    spelling: str | None = None
    location: Location | None = None
    features : tf.Tensor | None = None

    def __init__(self, level: int, order: int, kind: int | None = None, spelling: str | None = None, location : Location | None = None):
        '''
        :param id: identifier of the node
        :param level: level from the root
        '''

        self.level = level #
        self.order = order
        self.kind = kind
        self.spelling = spelling
        self.location = location

    # def dynamic_flags(self) -> tf.Tensor():
    #     dynamic_flags = np.zeros(shape=(DYNAMIC_FLAGS), dtype=np.float32)
    #     dynamic_flags[0] = self.level / 20.0
    #     dynamic_flags[1] = self.order / 20.0
    #     return tf.constant(dynamic_flags)

    # def features(self, weights: Weights) -> tf.Tensor:
    #     pass

    def encode(self, weights: Weights) -> tf.Tensor:
        pass

    def print(self, prev_location: Location | None = None) -> Location:
        pass

# # Node which needs to be predicted
# class UnknownNode(AstNode):
#     truth : AstNode | None = None
#     predicted : AstNode | None = None
#
#     def __init__(self, level: int, order: int, ground_truth : AstNode = None):
#         super().__init__(level, order)
#         self.truth = ground_truth
#
#     def predict(self, kind: int, order: int, weights: Weights, parent: AstNode):
#         features : tf.Tensor = tf.nn.relu(tf.matmul(weights.decode[parent.kind].features2children), parent.features())
#         if order > 0:
#             sibling_features: tf.Tensor = tf.zeros(FEATURES_AMNT, dtype=tf.float32)
#             for i in range(order-1):
#                 sibling_features += tf.nn.relu(tf.matmul(weights.decode[parent.children[i].kind].features2sibling, parent.children[i].features()))
#
#             features += sibling_features/tf.float32(order)
#
#         self.predicted = AstNode(parent.level + 1, order, features=features)
#
#
#     def encode(self, weights: Weights) -> tf.Variable:
#         return weights.unknown()


# Node Corresponds to an Ast Cursor aka Branch-of-a-tree
class CursorNode(AstNode):
    children: list[AstNode] | None = None

    def __init__(self, level: int, order: int, cursor: Cursor | None = None, features: tf.Tensor | None = None):
        '''
        :param id: identifier of the node
        :param level: level from the root
        :param order: order within siblings
        :param cursor: AST Cursor
        '''
        assert cursor is not None or features is not None, "either `cursor` or `features` must be provided"

        super().__init__(level, order, kind=cursor.kind.value, spelling=cursor.spelling, location=Location(cursor.location))
        self.children: list[AstNode] = []



        # kind_embeddings = np.zeros(CURSOR_KIND_EMB, dtype=np.float32)
        # #kind_embeddings[self.kind] = 1.0
        # tf_kind_logit = tf.constant(value=kind_embeddings, shape=(CURSOR_KIND_EMB), dtype=tf.float32)
        # tf_binary_flags = tf.constant(value=self.binary_flags(cursor), shape=(BINARY_FLAGS), dtype=tf.float32)
        # tf_spelling_features = tf.constant(value=self.spelling_features(cursor.spelling), shape=(SPELLING_FEATURES), dtype=tf.float32)
        # self.tf_input_features: tf.Tensor = tf.concat([tf_kind_logit, tf_binary_flags, tf_spelling_features], axis=0)

    # @staticmethod
    # def binary_flags(cursor: Cursor) -> np.ndarray:
    #     binary_flags = np.zeros(shape=(BINARY_FLAGS), dtype=np.float32)
    #     binary_flags[0] = cursor.is_definition()
    #     binary_flags[1] = cursor.is_const_method()
    #     binary_flags[2] = cursor.is_converting_constructor()
    #     binary_flags[3] = cursor.is_copy_constructor()
    #     binary_flags[4] = cursor.is_default_constructor()
    #     binary_flags[5] = cursor.is_move_constructor()
    #     binary_flags[6] = cursor.is_default_method()
    #     binary_flags[7] = cursor.is_deleted_method()
    #     binary_flags[8] = cursor.is_copy_assignment_operator_method()
    #     binary_flags[9] = cursor.is_move_assignment_operator_method()
    #     binary_flags[10] = cursor.is_mutable_field()
    #     binary_flags[11] = cursor.is_pure_virtual_method()
    #     binary_flags[12] = cursor.is_static_method()
    #     binary_flags[13] = cursor.is_virtual_method()
    #     binary_flags[14] = cursor.is_abstract_record()
    #     binary_flags[15] = cursor.is_scoped_enum()
    #     return binary_flags
    #
    # @staticmethod
    # def spelling_features(spelling: str) -> np.ndarray:
    #     spelling_features = np.zeros(shape=(SPELLING_FEATURES), dtype=np.float32)
    #     for i in range(min(SPELLING_FEATURES, len(spelling))):
    #         # stupid conversion of the string into float array
    #         spelling_features[i] = (float(ord(spelling[i])) - 127.) / 128
    #
    #     return spelling_features

    def add_child(self, node: AstNode | None):
        if node is not None:
            self.children.append(node)

    def print(self, prev_location: Location | None = None) -> Location:
        location = self.location
        # Cursor does not print anything itself
        for child in self.children:
            location = child.print(location)
        return location

    # def encode(self, weights: Weights) -> tf.Tensor:
    #     if self.features is not None:
    #         return self.features
    #
    #     self.features = tf.nn.relu(tf.matmul(weights.encode[self.kind].input2features, self.tf_input_features))
    #
    #     if self.children is not None and len(self.children) > 0:
    #         # now we have "averaging" of all children node outputs, however
    #         # ToDo: we plan to make in CNN-like manner
    #         children_features: tf.Tensor = tf.zeros(FEATURES_AMNT, dtype=tf.float32)
    #         for child in self.children:
    #             children_features += tf.nn.relu(tf.matmul(child.encode(weights), weights.encode[self.kind].children2features))
    #         children_features /= len(self.children)
    #
    #         self.features += tf.nn.relu(children_features)
    #
    #     return self.features
    #
    # def predict(self, child_num: int, weights: Weights):
    #     assert child_num < len(self.children)
    #     assert isinstance(self.children[child_num], UnknownNode)
    #     #child_kind : tf.int64 = tf.math.argmax(tf.matmul(weights.decode[self.kind].features2child_kind, self.features))
    #     #self.children[child_num] =
    #
    # @staticmethod
    # def decode(features: tf.Tensor) -> AstNode:
    #     pass



# Node Corresponds to an Ast Token aka Leaf-of-a-tree
class TokenNode(AstNode):

    def __init__(self, level: int, order: int, token: Token | None = None, features: tf.Tensor | None = None):
        '''
        :param id: identifier of the node
        :param level: level from the root
        :param order: order within siblings
        :param token: AST Token
        '''
        assert token is not None or features is not None, "either `token` or `features` must be provided"
        super().__init__(level, order, kind=token.kind.value, spelling=token.spelling, location=Location(token.location))


    def print(self, prev_location: Location | None = None) -> Location:
        if prev_location is None:
            prev_location = self.location

        if prev_location.file != self.location.file:
            prev_location = self.location

        while(self.location.line > prev_location.line):
            print()
            prev_location.line += 1
            prev_location.column = 0

        while(self.location.column > prev_location.column):
            print(" ")
            prev_location.column += 1

        print(self.spelling, end="")

        location = prev_location
        location.column += len(self.spelling)

        return location




