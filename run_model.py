"""Runs the trained model.
"""

from typing import Set

from sklearn.svm import SVC
from allennlp.predictors.predictor import Predictor

from document_getter import search_sentence
from json_processor import read_json_file, write_json_file
from evidence_evaluator import get_evidence

SUPPORT_LABEL = "SUPPORTS"
REFUTE_LABEL = "REFUTES"
UNKNOWN_LABEL = "NOT ENOUGH INFO"

def run_SVC_model(model: SVC, input_filename: str, output_filename: str,
                  correctness_predictor: Predictor, stop_words: Set[str]) -> None:
    """Runs the SVC model with given dataset.
    Parameters:
    -- model: SVC
    ---- The SVC model to be run.
    -- input_filename: str
    ---- The name of the JSON file containing the dataset.
    -- output_filename: str
    ---- The name of the JSON file storing the prediction results.
    -- correctness_predictor: Predictor
    ---- A predictor for text entailment.
    -- stop_words: Set[str]
    ---- A set of stop words to be used for filtering documents.
    """
    input_data = read_json_file(input_filename)
    output_data = {}
    for case_id in input_data:
        support_sents = set()
        refute_sents = set()
        case_item = input_data[case_id]
        claim = case_item["claim"]
        evidence = get_evidence(search_sentence(claim, stop_words))
        for doc_name in evidence:
            sentences = evidence[doc_name]
            for (sent_no, sentence) in sentences:
                predict_result = correctness_predictor.predict(premise=sentence, hypothesis=claim)
                sent_proabilities = predict_result["label_probs"][:2]
                predicted_label = model.predict([sent_proabilities])[0]
                if predicted_label == SUPPORT_LABEL:
                    support_sents.add([doc_name, sent_no])
                elif predicted_label == REFUTE_LABEL:
                    refute_sents.add([doc_name, sent_no])
        
        output_item = {"claim": claim}
        if not support_sents and not refute_sents:
            output_item["label"] = UNKNOWN_LABEL
            output_item["evidence"] = []
        elif len(support_sents) >= len(refute_sents):
            output_item["label"] = SUPPORT_LABEL
            output_item["evidence"] = list(support_sents)
        else:
            output_item["label"] = REFUTE_LABEL
            output_item["evidence"] = list(refute_sents)
        output_data[case_id] = output_item
    write_json_file(output_filename, output_data)
