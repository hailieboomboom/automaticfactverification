"""The entry point of the program.
However, due to the high computing resource required for file indexing,
the script `build_index.py` needs to be run before running this script.
"""

import nltk

from nltk.corpus import stopwords
from sklearn.svm import SVC
from allennlp.predictors.predictor import Predictor

from train_model import train_SVC_model
from run_model import run_SVC_model

TRAIN_FILE = "train.json"
DEV_FILE = "devset.json"
DEV_RESULT_FILE = "devset-result.json"
TEST_FILE = "test-unlabelled.json"
TEST_RESULT_FILE = "test-labelled.json"

TE_PATH = "https://s3-us-west-2.amazonaws.com/allennlp/models/decomposable-attention-elmo-2018.02.19.tar.gz"
correctness_predictor = Predictor.from_path(TE_PATH)

nltk.download("stopwords")
stop_words = set(stopwords.words())

# train
SVC_model = train_SVC_model(TRAIN_FILE, correctness_predictor, stop_words)

# development
run_SVC_model(SVC_model, DEV_FILE, DEV_RESULT_FILE, correctness_predictor, stop_words)

# test
run_SVC_model(SVC_model, TEST_FILE, TEST_RESULT_FILE, correctness_predictor, stop_words)