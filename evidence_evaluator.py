"""Evaluates all possible evidences.
"""

from typing import Tuple, Dict, Iterable, Any, Optional, Set, List
from itertools import groupby

from allennlp.predictors.predictor import Predictor

from document_getter import search_sentence, get_doc_content

UNKNOWN_LABEL = "NOT ENOUGH INFO"

def get_evidence(doc_names: List[str]) -> Dict[str, List[Tuple[int, str]]]:
    """Obtains evidences of a list of documents.
    Parameter:
    -- doc_names: List[str]
    ---- The list of all document names.
    Return value: Dict[str, List[Tuple[int, str]]]
    -- All possible evidence.
    """
    evidence = {}
    for doc_name in doc_names:
        if doc_name not in evidence:
            doc_content = get_doc_content(doc_name)
            evidence[doc_name] = doc_content
    return evidence

def check_claim(claim: str, train_evidence: Set[Tuple[str, int]], label: str,
                correctness_predictor: Predictor, stop_words: Set[str]) -> Tuple[List[List[float]], List[str]]:
    print("Checking claim:", claim)
    doc_names = search_sentence(claim, stop_words)
    evidence = get_evidence(doc_names)

    probabilities = []
    labels = []

    for doc_name in evidence:
        print("Checking doc:", doc_name)
        sentences = evidence[doc_name]
        for (sent_no, sentence) in sentences:
            predict_result = correctness_predictor.predict(premise=sentence, hypothesis=claim)
            sent_probabilities = predict_result["label_probs"][:2]
            probabilities.append(sent_probabilities)

            original_doc_name = doc_name.replace("(", "-LRB-").replace(")", "-RRB-")
            if [original_doc_name, sent_no] in train_evidence:
                labels.append(label)
            else:
                labels.append(UNKNOWN_LABEL)

    return (probabilities, labels)