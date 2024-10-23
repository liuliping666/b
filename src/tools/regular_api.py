import string
import random
import re
import time
import json
from collections import Counter

def extract_cot_answer(cot):
    if not cot:
        return ""

    # get answer
    cot = cot.strip(" ")
    cot = cot.split("<|endoftext|>")[0]  # text-davinci-003
    TEMPLATE = "answer is: "
    if TEMPLATE not in cot:
        return ""

    start_idx = cot.rfind(TEMPLATE) + len(TEMPLATE)
    end_idx = -1 if cot.endswith(".") else len(cot)
    ans_span = cot[start_idx: end_idx].strip()

    return ans_span