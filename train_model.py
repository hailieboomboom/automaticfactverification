"""Trains a model.
"""

from typing import Tuple, List, Set

import numpy as np
from sklearn.svm import SVC
from allennlp.predictors.predictor import Predictor

from json_processor import read_json_file
from evidence_evaluator import check_claim

def get_train_data(train_filename: str, correctness_predictor: Predictor,
                   stop_words: Set[str]) -> Tuple[List[List[float]], List[str]]:
    """Retrieves training dataset.
    Parameters:
    -- train_filename: str
    ---- The name of the JSON file containing the training dataset.
    -- correctness_predictor: Predictor
    ---- A predictor for text entailment.
    -- stop_words: Set[str]
    ---- A set of stop words to be used for filtering documents.
    Return value: Tuple[List[List[float]], List[str]]
    -- The training dataset, consists of:
    ---- A list of 2D-vector probabilities.
    ---- A list of target labels.
    """
    train_data = read_json_file(train_filename)
    probabilities = []
    labels = []
    data_len = len(train_data)
    for case_item in train_data.values():
        case_probs, case_labels = check_claim(case_item["claim"], case_item["evidence"],
                                              case_item["label"], correctness_predictor, stop_words)
        probabilities.extend(case_probs)
        labels.extend(case_labels)
    return (probabilities, labels)

def train_SVC_model(train_filename: str, correctness_predictor: Predictor, stop_words: Set[str]) -> SVC:
    """Trains a SVC model.
    Parameters:
    -- train_filename: str
    ---- The name of the JSON file containing the training dataset.
    -- correctness_predictor: Predictor
    ---- A predictor for text entailment.
    -- stop_words: Set[str]
    ---- A set of stop words to be used for filtering documents.
    Return value: SVC
    -- The trained SVC model.
    """
    probabilities, labels = get_train_data(train_filename, correctness_predictor, stop_words)
    prob_array = np.array(probabilities)
    my_SVC = SVC(gamma="scale")
    my_SVC.fit(prob_array, labels)
    return my_SVC