import torch
from transformers import BertTokenizer, BertModel
import numpy as np
import faiss
import openai
import argparse
import json
import os
from datetime import datetime
from src.utils import load_meta_examples


class SimilarityCalculator:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased')

    def get_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            embedding = outputs.last_hidden_state[:, 0, :]
        return embedding.numpy()

openai.api_key = ""
openai.api_base = ""

class VectorDatabase:
    def __init__(self):
        self.datasets = {}

    def add(self, dataset_name, question, meta_thought):
        if dataset_name not in self.datasets:
            self.datasets[dataset_name] = {
                'questions': [],
                'meta_thoughts': [],
                'embeddings': [],
                'index': faiss.IndexFlatL2(768)
            }
        embedding = similarity_calculator.get_embedding(question)
        self.datasets[dataset_name]['questions'].append(question)
        self.datasets[dataset_name]['meta_thoughts'].append(meta_thought)
        self.datasets[dataset_name]['embeddings'].append(embedding)
        self.datasets[dataset_name]['index'].add(embedding.astype(np.float32))

    def retrieve_similar(self, dataset_name, input_question, k):
        input_embedding = similarity_calculator.get_embedding(input_question)
        D, I = self.datasets[dataset_name]['index'].search(input_embedding.astype(np.float32), k)
        return [(self.datasets[dataset_name]['questions'][i], self.datasets[dataset_name]['meta_thoughts'][i]) for i in I[0]]


def generate_meta_thought(few_shots, input_question):
    prompt = (
        "You are a meta-thinker, skilled in abstract reasoning.\n"
        "Given a question, you should generate a meta-thought including the necessary knowledge, analytical methods, and fundamental strategies for solving the provided question.\n"
    )

    for i, (question, meta) in enumerate(few_shots):
        prompt += "Question {}: '{}' -> Meta Thought: '{}'\n".format(i + 1, question, meta)

    prompt += f"New Question: '{input_question}'\n"

    meta_thought = call_api(prompt)
    return meta_thought


def call_api(prompt,args):
    res = openai.ChatCompletion.create(
        model=args.model,
        messages=[{"role": 'user', "content": prompt}],
        max_tokens=1000,
        temperature=0.2,
        stop=["\n\n"]
    )
    result = res.choices[0].message['content'].strip()
    return result


def load_dataset(data_file):
    with open(data_file, 'r', encoding='utf-8') as f:
        dataset = [json.loads(line) for line in f]
    return dataset


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="gsm8k", type=str)
    parser.add_argument("--model", default="gpt-3.5-turbo-0613", type=str)
    parser.add_argument("--prompt_type", default="meta", type=str)
    parser.add_argument("--split", default="test", type=str)
    parser.add_argument("--num_test_sample", default=-1, type=int)  # -1 for full data
    parser.add_argument("--seed", default=0, type=int)
    parser.add_argument("--start", default=0, type=int)
    parser.add_argument("--end", default=-1, type=int)
    args = parser.parse_args()
    return args


def inference(args):
    global similarity_calculator
    similarity_calculator = SimilarityCalculator()

    global vector_db
    vector_db = VectorDatabase()

    FEW_SHOT_EXAMPLES = load_meta_examples(f'prompt/{args.data}/{args.prompt_type}.md')

    for dataset, examples in FEW_SHOT_EXAMPLES.items():
        for question, meta_thought in examples:
            vector_db.add(dataset, question, meta_thought)
    
    try:
       data_file = f"data/{args.data}/{args.split}.json"
    except:
        data_file = f"data/{args.data}/{args.split}.jsonl"

    if os.path.exists(data_file):
        print("Loading data from", data_file)
        dataset = load_dataset(data_file)
    else:
        raise NotImplementedError(f"Loading data from {args.data} source not implemented.")

    if args.num_test_sample > 0:
        dataset = dataset[:args.num_test_sample]
        
    try:
        filename = f'outputs/{args.model}/{args.data}/{args.split}_hsp.json'
        os.makedirs(f'outputs/{args.model}/{args.data}', exist_ok=True)
    except:
        filename = f'outputs/{args.model}/{args.data}/{args.split}_hsp.jsonl'
        os.makedirs(f'outputs/{args.model}/{args.data}', exist_ok=True)

    writer = open(filename, 'w')

    for idx, sample in enumerate(dataset):
        if idx < args.start or (args.end != -1 and idx >= args.end):
            continue

        if args.data == "gsm8k" or args.data == "strategy_qa":
            question = sample['question'].strip()
        elif args.data == "svamp":
            if sample["Body"][-1] != '.':
                question = sample["Body"] + '.' + ' ' + sample["question"]
            else:
                question = sample["Body"] + ' ' + sample["question"]
        else:
            raise ValueError(f"Unsupported dataset: {args.data}")
        
        context = f'Question: {question}' + '\n' + "Meta thought: "
        print(f"idx: {idx}")
        print(context, end="")
            
        
        if args.data == "gsm8k" or args.data == "svamp":
            k = 8
        elif args.data == "strategy_qa":
            k = 6
        else:
            raise ValueError(f"Unsupported dataset: {args.data}")

        similar_questions = vector_db.retrieve_similar(args.data, question, k)
        meta = generate_meta_thought(similar_questions, question)

        sample['meta_thought'] = meta

        print("Meta thought: ", meta)

        writer.write(json.dumps(sample) + '\n')
        writer.flush()
    writer.close()


if __name__ == "__main__":
    args = parse_args()
    inference(args)
