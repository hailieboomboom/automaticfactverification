"""Indexes Wikipedia documents and document names from the original text files.
This script should be placed in the same folder as `wiki-pages-text`.
"""

import os
import sys
import re
from hashlib import sha1
from typing import NewType, Dict, List, Tuple, Union, Set
from time import strftime
from traceback import print_exc

INPUT_FOLDER = "wiki-pages-text"
INDEX_FOLDER = "docname-index"
DOC_FOLDER = "indexed-docs"
ENCODING = "utf-8"
SEPARATOR = "\\" if sys.platform == "win32" else "/"
INPUT_FILE_COUNT = 109
START_FILE = 1
END_FILE = INPUT_FILE_COUNT
FOLDER_SIZE = 100
FILE_CAPACITY = 20000
SAFE_STRING = "xmcgcg"

# Type aliases indicating the data type
# -- NameDict: dictionaries of words, which map to document names containing these words
# -- IndexNode: nodes of the index tree of document names
# -- SentDict: dictionaries of document names, which map to the sentences in the documents
# -- DocNode: nodes of the index tree of the document sentences
NameDict = Dict[str, Union[Set[str], int]]
IndexNode = Dict[str, Union[NameDict, 'IndexNode']]
SentDict = Dict[str, Union[Dict[int, str], int]]
DocNode = Dict[str, Union[SentDict, 'DocNode']]

# Variables used for displaying indexing progress
word_count = 0
doc_count = 0
processed_word_count = 0
processed_doc_count = 0
word_count_1percent = 0
doc_count_1percent = 0

def transform_brackets(target: str) -> str:
    """Restores brackets in document strings.
    Parameter:
    -- target: str
    ---- The target string to be transformed.
    Return value: str
    -- The transformed string.
    """
    return target.replace("-LRB-", "(").replace("-RRB-", ")")

def sha1_hash(target: str) -> str:
    """Calculates the SHA-1 hash value of a string as a hexadecimal string.
    Parameter:
    -- target: str
    ---- The string whose hash value is going to be calculated.
    Return value: str
    -- The hexadecimal hash value of the target string.
    """
    return sha1(bytes(target, ENCODING)).hexdigest()

def get_input_pathname(file_index: int) -> str:
    """Obtains the name of the original Wikipedia text file from a file number.
    Parameter:
    -- file_index: int
    ---- The file number of the corresponding text file.
    Return value: str
    -- The name of the corresponding text file.
    """
    return f"{INPUT_FOLDER}{SEPARATOR}wiki-{file_index:03d}.txt"

def expand_indices(doc_name_dict: NameDict, start_index: int) -> Dict[str, NameDict]:
    """Expands the document name index tree if the leaf node storage reaches capacity.
    Creates child nodes and distributes the stored data.
    Parameters:
    -- doc_name_dict: NameDict
    ---- The dictionary of stored document names in the leaf node.
    -- start_index: int
    ---- The index of the digit in the hash value of the word, correspoding to the level of children.
    -- Return value: Dict[str, NameDict]:
    ---- The new node with all children created.
    """
    result = {}
    for (word, name_set) in doc_name_dict.items():
        hash_digit = sha1_hash(word)[start_index]
        if hash_digit not in result:
            result[hash_digit] = {SAFE_STRING: 0}
        result[hash_digit][word] = name_set
        result[hash_digit][SAFE_STRING] += len(name_set) + 1
    return result

def add_doc_name_word(doc_name: str, word: str, index_dict: IndexNode, start_index: int = 0) -> None:
    """Adds a pair of word and document name to the document name index tree.
    Parameters:
    -- doc_name: str
    ---- The document name to be added to the index tree.
    -- word: str
    ---- The word to be added to the index tree.
    -- index_node: IndexNode
    ---- The node of the index tree where the pair is going to be added.
    -- start_index: int
    ---- The index of the digit in the hash value of the word, correspoding to the current level.
    """
    word_hash = sha1_hash(word)
    hash_digit = word_hash[start_index]
    if hash_digit not in index_node:
        index_node[hash_digit] = {SAFE_STRING: 0}
    value = index_node[hash_digit]
    if SAFE_STRING in value:
        if word not in value:
            value[word] = set()
            global word_count
            word_count += 1
        value[word].add(doc_name)
        value[SAFE_STRING] += 1
        if value[SAFE_STRING] > FILE_CAPACITY >= len(value[word]) + 1:
            del value[SAFE_STRING]
            index_node[hash_digit] = expand_indices(value, start_index + 1)
    else:
        add_doc_name_word(doc_name, word, value, start_index + 1)

def add_doc_name(doc_name: str, index_node: IndexNode) -> None:
    """Adds all words in the document name and the document name itself to the index tree.
    Parameters:
    -- doc_name: str
    ---- The document name to be added to the index tree.
    -- index_node: IndexNode
    ---- The node of the index tree where the pairs are going to be added.
    """
    doc_name_words = map(str.lower, filter(bool, re.split(r"[_\W]+", doc_name)))
    for word in set(doc_name_words):
        add_doc_name_word(doc_name, word, index_node)

def expand_docs(sent_dict: SentDict, start_index: int) -> Dict[str, SentDict]:
    """Expands the document sentence index tree if the leaf node storage reaches capacity.
    Creates child nodes and distributes the stored data.
    Parameters:
    -- sent_dict: SentDict
    ---- The dictionary of stored sentences in the leaf node.
    -- start_index: int
    ---- The index of the digit in the hash value of the word, correspoding to the level of children.
    -- Return value: Dict[str, SentDict]:
    ---- The new node with all children created.
    """
    result = {}
    for (doc_name, doc_content) in sent_dict.items():
        hash_digit = sha1_hash(doc_name)[start_index]
        if hash_digit not in result:
            result[hash_digit] = {SAFE_STRING: 0}
        result[hash_digit][doc_name] = doc_content
        result[hash_digit][SAFE_STRING] += len(doc_content) + 1
    return result

def add_doc_content(doc_name: str, doc_content: Dict[int, str],
                    doc_node: DocNode, start_index: int = 0) -> None:
    """Adds a pair of document name and sentence list to the document name index tree.
    Parameters:
    -- doc_name: str
    ---- The document name to be added to the index tree.
    -- doc_content: Dict[int, str]
    ---- The sentences of the document to be added to the index tree.
    -- doc_node: DocNode
    ---- The node of the index tree where the pair is going to be added.
    -- start_index: int
    ---- The index of the digit in the hash value of the document name, correspoding to the current level.
    """
    name_hash = sha1_hash(doc_name)
    hash_digit = name_hash[start_index]
    if hash_digit not in doc_dict:
        doc_dict[hash_digit] = {SAFE_STRING: 0}
    value = doc_dict[hash_digit]
    if SAFE_STRING in value:
        global doc_count
        doc_count += 1
        value[doc_name] = doc_content
        dict_len = len(doc_content) + 1
        value[SAFE_STRING] += dict_len
        if value[SAFE_STRING] > FILE_CAPACITY >= dict_len:
            del value[SAFE_STRING]
            doc_dict[hash_digit] = expand_docs(value, start_index + 1)
    else:
        add_doc_content(doc_name, doc_content, value, start_index + 1)

def build_indices(index_node: IndexNode, index_folder: str = INDEX_FOLDER) -> None:
    """Creates index folders and files based on the document name index tree.
    Parameters:
    -- index_node: IndexNode
    ---- The node of the document name index tree.
    -- index_folder: str
    ---- The parent folder of all folders and files created by this function call.
    """
    for hash_digit in index_node:
        value = index_node[hash_digit]
        if SAFE_STRING in value:
            del value[SAFE_STRING]
            filename = f"{index_folder}{SEPARATOR}{hash_digit}.txt"
            with open(filename, "w", encoding=ENCODING) as file_obj:
                for word in value:
                    file_obj.write(f"{word} {len(value[word])}\n")
                    for doc_name in sorted(value[word]):
                        file_obj.write(doc_name + "\n")
                    global processed_word_count
                    processed_word_count += 1
                    if processed_word_count % word_count_1percent == 0:
                        percentage = processed_word_count // word_count_1percent
                        if 1 <= percentage <= 99:
                            print(f"{percentage}% indices built at {strftime('%H:%M:%S')}")
        else:
            folder = f"{index_folder}{SEPARATOR}{hash_digit}"
            os.mkdir(folder)
            build_indices(value, folder)
        value.clear()

def build_docs(doc_node: DocNode, doc_folder: str = DOC_FOLDER) -> None:
    """Creates index folders and files based on the document sentences index tree.
    Parameters:
    -- doc_node: DocNode
    ---- The node of the document sentences index tree.
    -- index_folder: str
    ---- The parent folder of all folders and files created by this function call.
    """
    for hash_digit in doc_node:
        value = doc_node[hash_digit]
        if SAFE_STRING in value:
            del value[SAFE_STRING]
            filename = f"{doc_folder}{SEPARATOR}{hash_digit}.txt"
            with open(filename, "w", encoding=ENCODING) as file_obj:
                for doc_name in value:
                    file_obj.write(doc_name + "\n")
                    for (sent_no, sentence) in sorted(value[doc_name].items()):
                        file_obj.write(f"{sent_no} {transform_brackets(sentence)}")
                    global processed_doc_count
                    processed_doc_count += 1
                    if processed_doc_count % doc_count_1percent == 0:
                        percentage = processed_doc_count // doc_count_1percent
                        if 1 <= percentage <= 99:
                            print(f"{percentage}% documents indexed at {strftime('%H:%M:%S')}")
        else:
            folder = f"{doc_folder}{SEPARATOR}{hash_digit}"
            os.mkdir(folder)
            build_docs(value, folder)
        value.clear()

def index_documents() -> None:
    """Indexes all Wikipedia documents from text files.
    """

    index_dict = {}
    doc_dict = {}
    current_doc = ""
    current_sents = {}

    first_round = True
    try:
        while True:
            for file_index in range(START_FILE, END_FILE + 1):
                if file_index % 10 == 1:
                    print(f"Start processing File {file_index} at {strftime('%H:%M:%S')}")
                with open(get_input_pathname(file_index), "r", encoding=ENCODING) as input_file_obj:
                    for line in input_file_obj:
                        line_list = line.split(" ")
                        doc_name = transform_brackets(line_list[0])
                        if doc_name != current_doc:
                            if current_doc:
                                if first_round:
                                    add_doc_name(current_doc, index_dict)
                                else:
                                    add_doc_content(current_doc, current_sents, doc_dict)
                            current_doc = doc_name
                            current_sents = {}
                        if not first_round:
                            sent_no_str = line_list[1]
                            if sent_no_str.isdigit():
                                sent_no = int(sent_no_str)
                                current_sents[sent_no] = " ".join(line_list[2:])
            if first_round:
                add_doc_name(current_doc, index_dict)
            else:
                add_doc_content(current_doc, current_sents, doc_dict)

            word_count_1percent = word_count // 100
            doc_count_1percent = doc_count // 100

            if first_round:
                print(f"Start building indices at {strftime('%H:%M:%S')}")
                os.mkdir(INDEX_FOLDER)
                build_indices(index_dict)
                index_dict.clear()
                first_round = False
            else:
                print(f"Start indexing documents at {strftime('%H:%M:%S')}")
                os.mkdir(DOC_FOLDER)
                build_docs(doc_dict)
                doc_dict.clear()
                break
            
        print("Complete!")
        print(f"{word_count} words and {doc_count} documents processed.")
    except Exception:
        print_exc()

if __name__ == '__main__':
    index_documents()
    os.system("pause")