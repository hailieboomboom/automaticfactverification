"""Retrieves information from indexed documents.
"""

import os.path
import re
from hashlib import sha1
from typing import List, Tuple, Set, Dict
from collections import defaultdict

INDEX_FOLDER = "docname-index"
DOC_FOLDER = "indexed-docs"
ENCODING = "utf-8"

def sha1_hash(target: str) -> str:
    """Calculates the SHA-1 hash value of a string as a hexadecimal string.
    Parameter:
    -- target: str
    ---- The string whose hash value is going to be calculated.
    Return value: str
    -- The hexadecimal hash value of the target string.
    """
    return sha1(bytes(target, ENCODING)).hexdigest()

def search_word(word: str) -> List[str]:
    """Searches all documents name containing the search word.
    ParametersL
    -- word: str
    ---- The search word. It should not contain any space.
    Return value: List[str]
    -- The list of all matching document names.
    """
    word_hash = sha1_hash(word.lower())
    path = INDEX_FOLDER
    doc_name_list = []
    for hash_digit in word_hash:
        path += "\\" + hash_digit
        if os.path.isdir(path):
            continue
        elif os.path.isfile(path + ".txt"):
            with open(path + ".txt", "r", encoding=ENCODING) as file_obj:
                word_found = False
                for line in file_obj:
                    line = line.strip()
                    line_items = line.split()
                    line_len = len(line_items)
                    if word_found:
                        if line_len == 1:
                            doc_name_list.append(line_items[0])
                        else:
                            break
                    else:
                        if line_len == 2 and line_items[0] == word.lower():
                            word_found = True
            break
        else:
            return []
    return doc_name_list

def get_words(doc_name: str) -> List[str]:
    """Obtains all words in a document name.
    Parameters:
    -- doc_name: str
    ---- The document name.
    Return value: List[str]
    -- The list of all words in the document name.
    """
    short_name = re.sub(r"\(.*\)", "", doc_name).strip("_")
    words = short_name.split("_")
    return list(map(str.lower, words))

def get_valid_names(words: List[str], name_list: List[Tuple[str, List[str]]]) -> Set[Tuple[str, List[str]]]:
    """Filters all valid document names from a sentence.
    Parameters:
    -- words: List[str]
    ---- The list of word in the claim sentence.
    -- name_list: List[Tuple[str, List[str]]]
    ---- The list of document names and their words.
    Return value: Set[Tuple[str, List[str]]]
    -- The set of all valid document names and their words.
    """
    valid_names = set()
    for (name, word_list) in name_list:
        if words[:len(word_list)] == word_list:
            valid_names.add((name, tuple(word_list)))
    return valid_names

def absorb_doc_names(doc_names: Set[Tuple[str, List[str]]]) -> Set[str]:
    """Removes the document names which appear to be a substring of other document names.
    Parameter: Set[Tuple[str, List[str]]]
    -- The set of document names and their words.
    Return value: Set[str]
    -- The set of real document names.
    """
    name_dict = defaultdict(set)
    for (name, word_list) in doc_names:
        name_dict[word_list].add(name)
    
    words_set = set(map(lambda word_list: " ".join(word_list), name_dict.keys()))
    new_set = set()
    while words_set:
        is_valid = True
        words = words_set.pop()
        for remain_words in words_set | new_set:
            if words in remain_words:
                is_valid = False
                break
        if is_valid:
            new_set.add(words)
    
    result = set()
    for words in new_set:
        word_list = words.split()
        result |= name_dict[tuple(word_list)]
    return result

def search_sentence(sentence: str, stop_words: Set[str]) -> List[str]:
    """Searches for all document names in a sentence.
    Parameters:
    -- sentence: str
    ---- The sentence to be searched.
    -- stop_words: Set[str]
    ---- The set of stop words.
    Return value: List[str]
    -- The list of matching document names.
    """
    words = re.split(r"\W+", sentence)
    words = list(filter(bool, words))

    doc_names = {}
    ne_doc_names = {}
    for word in words:
        if word and word not in stop_words:
            target_dict = doc_names if word[0].islower() else ne_doc_names
            word = word.lower()
            if word not in target_dict:
                target_dict[word] = [(name, get_words(name)) for name in search_word(word)]
    
    lower_words = list(map(str.lower, words))
    result = set()
    ne_found = False
    for i in range(len(words)):
        target_dict = doc_names if words[i][0].islower() else ne_doc_names
        is_ne = target_dict is ne_doc_names
        if not ne_found and is_ne:
            ne_found = True
            result.clear()
        if ne_found == is_ne and lower_words[i] in target_dict:
            result |= get_valid_names(lower_words[i:], target_dict[lower_words[i]])
    return list(absorb_doc_names(result))

def get_doc_content(doc_name: str) -> List[Tuple[int, str]]:
    """Retrieves all sentences of a document.
    Parameter:
    -- doc_name: str
    ---- The name of the document whose sentences are going to be retrieved.
    Return value: List[Tuple[int, str]]
    -- The sentences of the document.
    """
    name_hash = sha1_hash(doc_name)
    path = DOC_FOLDER
    doc_content = []
    for hash_digit in name_hash:
        path += "\\" + hash_digit
        if os.path.isdir(path):
            continue
        elif os.path.isfile(path + ".txt"):
            with open(path + ".txt", "r", encoding=ENCODING) as file_obj:
                name_found = False
                for line in file_obj:
                    line = line.strip()
                    if name_found:
                        space_index = line.find(" ")
                        if space_index != -1:
                            sent_no = int(line[:space_index])
                            sentence = line[space_index + 1:]
                            doc_content.append((sent_no, sentence))
                        else:
                            break
                    else:
                        if line == doc_name:
                            name_found = True
            break
        else:
            return []
    return doc_content

if __name__ == '__main__':
    print(search_sentence("Soul Food", set()))