from __future__ import annotations

import numpy as np
import tensorflow as tf
from typing import Any, Final
from clang.cindex import Cursor

FEATURES_AMNT: Final[int] = 512  # 1024
KIND_AMNT: Final[int] = 700
BINARY_FLAGS: Final[int] = 16
SPELLING_FEATURES: Final[int] = 100
DYNAMIC_FLAGS: Final[int] = 2

class EncodeWeights:
    input2features: tf.Tensor  # FEATURES_AMNT x (KIND_AMNT + BINARY_FLAGS + SPELLING_FEATURES)
    children2features: tf.Tensor  # FEATURES_AMNT x FEATURES_SIZE
    # passing: tf.Tensor # FEATURES_AMNT x FEATURES_SIZE


class DecodeWeights:
    # in order to decode unknown node, first we need to predict its kind (which dependes on the parents kind)
    features2child_kind: tf.Tensor  # (FEATURES_AMNT + 1) x KIND_AMNT predict kind of particular child

    features2children: tf.Tensor  #
    features2sibling: tf.Tensor
    # features2spelling: tf.Tensor # FEATURES_AMNT x KIND_AMNT
    # features2binary_flags: tf.Tensor # FEATURES_AMNT x KIND_AMNT


# all learnable weights
class Weights:
    encode: dict[int, EncodeWeights]  # each kind has its own encoding weight
    decode: dict[int, DecodeWeights]  # each kind has its own decoding weight
    unknownFeatures: tf.Tensor  # single instance of tf.Tensor dexcribing any unknown node


class AstNode:
    # kind: int
    level: int
    order: int

    def __init__(self, level: int, order: int):
        '''
        :param id: identifier of the node
        :param level: level from the root
        '''
        self.level = level
        self.order = order

    def dynamic_flags(self) -> tf.Tensor():
        dynamic_flags = np.zeros(shape=(DYNAMIC_FLAGS), dtype=np.float32)
        dynamic_flags[0] = self.level / 20.0
        dynamic_flags[1] = self.order / 20.0
        return tf.constant(dynamic_flags)

    # def features(self, weights: Weights) -> tf.Tensor:
    #     pass

    def encode(self, weights: Weights) -> tf.Tensor:
        pass


# Node which needs to be predicted
class UnknownNode(AstNode):
    truth : KnownNode | None = None
    predicted : KnownNode | None = None

    def __init__(self, level: int, order: int, ground_truth : KnownNode = None):
        super().__init__(level, order)
        self.truth = ground_truth

    def predict(self, kind: int, order: int, weights: Weights, parent: KnownNode):
        features : tf.Tensor = tf.nn.relu(tf.matmul(weights.decode[parent.kind].features2children))
        if order > 0:
            sibling_features: tf.Tensor = tf.zeros(FEATURES_AMNT, dtype=tf.float32)
            for i in range(order-1):
                sibling_features += tf.nn.relu(tf.matmul(weights.decode[parent.children[i].kind].features2sibling, parent.children[i].features()))

            features += sibling_features/float(order)

        self.predicted = KnownNode(parent.level + 1, order, features=features)


    def encode(self, weights: Weights) -> tf.Tensor:
        return weights.unknownFeatures


# Node which is already exists/known
class KnownNode(AstNode):
    kind: int
    spelling: str
    location: Any
    children: list[AstNode] | None = None

    def __init__(self, level: int, order: int, cursor: Cursor | None = None, features: tf.Tensor | None = None):

        '''

        :param id: identifier of the node
        :param level: level from the root
        :param order: order within siblings
        :param cursor: AST cursor
        '''

        super().__init__(level, order)
        self.kind = cursor.kind.value
        self.children: list[AstNode] = []

        assert cursor is not None or features is not None, "cursor or features must be provided"

        self.location = cursor.location
        self.features : tf.Tensor | None = None

        kind_logits = np.zeros(KIND_AMNT, dtype=np.float32)
        kind_logits[self.kind] = 1.0
        tf_kind_logit = tf.constant(value=kind_logits, shape=(KIND_AMNT), dtype=tf.float32)
        tf_binary_flags = tf.constant(value=self.binary_flags(cursor), shape=(BINARY_FLAGS), dtype=tf.float32)
        tf_spelling_features = tf.constant(value=self.spelling_features(cursor.spelling), shape=(SPELLING_FEATURES), dtype=tf.float32)
        self.tf_input_features: tf.Tensor = tf.concat([tf_kind_logit, tf_binary_flags, tf_spelling_features], axis=0)

    @staticmethod
    def binary_flags(cursor: Cursor) -> np.ndarray:
        binary_flags = np.zeros(shape=(BINARY_FLAGS), dtype=np.float32)
        binary_flags[0] = cursor.is_definition()
        binary_flags[1] = cursor.is_const_method()
        binary_flags[2] = cursor.is_converting_constructor()
        binary_flags[3] = cursor.is_copy_constructor()
        binary_flags[4] = cursor.is_default_constructor()
        binary_flags[5] = cursor.is_move_constructor()
        binary_flags[6] = cursor.is_default_method()
        binary_flags[7] = cursor.is_deleted_method()
        binary_flags[8] = cursor.is_copy_assignment_operator_method()
        binary_flags[9] = cursor.is_move_assignment_operator_method()
        binary_flags[10] = cursor.is_mutable_field()
        binary_flags[11] = cursor.is_pure_virtual_method()
        binary_flags[12] = cursor.is_static_method()
        binary_flags[13] = cursor.is_virtual_method()
        binary_flags[14] = cursor.is_abstract_record()
        binary_flags[15] = cursor.is_scoped_enum()
        return binary_flags

    @staticmethod
    def spelling_features(spelling: str) -> np.ndarray:
        spelling_features = np.zeros(shape=(SPELLING_FEATURES), dtype=np.float32)
        for i in range(min(SPELLING_FEATURES, len(spelling))):
            # stupid conversion of the string into float array
            spelling_features[i] = (float(ord(spelling[i])) - 127.) / 128

        return spelling_features

    def add_child(self, node: AstNode):
        self.children.append(node)


    def encode(self, weights: Weights) -> tf.Tensor:
        if self.features is not None:
            return self.features

        self.features = tf.nn.relu(tf.matmul(weights.encode[self.kind].input2features, self.tf_input_features))

        if self.children is not None and len(self.children) > 0:
            # now we have "averaging" of all children node outputs, however
            # ToDo: we plan to make in CNN-like manner
            children_features: tf.Tensor = tf.zeros(FEATURES_AMNT, dtype=tf.float32)
            for child in self.children:
                children_features += tf.nn.relu(tf.matmul(child.encode(weights), weights.encode[self.kind].children2features))
            children_features /= len(self.children)

            self.features += tf.nn.relu(children_features)

        return self.features

    def predict(self, child_num: int, weights: Weights):
        assert child_num < len(self.children)
        assert isinstance(self.children[child_num], UnknownNode)
        child_kind : tf.int64 = tf.math.argmax(tf.matmul(weights.decode[self.kind].features2child_kind, self.features))
        #self.children[child_num] =

    @staticmethod
    def decode(features: tf.Tensor) -> AstNode:

        pass
