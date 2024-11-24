import json
import os
from datetime import datetime
from tqdm import tqdm
import argparse
from collections import Counter
from distutils.util import strtobool
import openai
import sys
from time import time

from src.datasets.dataset_loader import DatasetLoader
from src.utils import load_prompt, set_seed, load_jsonl
from src.tools.interpreter_api import safe_execute, extract_code_block
from src.GSM8K.utils import *



openai.api_key = ""
openai.api_base = ""


class DualStream:
    def __init__(self, file_path):
        self.terminal = sys.stdout
        self.file = open(file_path, 'w', encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.file.write(message)
        self.flush()

    def flush(self):
        self.terminal.flush()
        self.file.flush()

    def close(self):
        self.file.close()

    def __enter__(self):
        sys.stdout = self
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self.terminal
        self.file.close()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="gsm8k", type=str)
    parser.add_argument("--model", default="gpt-4-0613", type=str)
    parser.add_argument("--prompt_type", default="pot", type=str)
    parser.add_argument("--critic_type", default="critic", type=str)
    parser.add_argument("--split", default="test", type=str)
    parser.add_argument("--num_test_sample", default=-1, type=int)  # -1 for full data
    parser.add_argument("--seed", default=0, type=int)
    parser.add_argument("--start", default=1, type=int)
    parser.add_argument("--end", default=-1, type=int)
    parser.add_argument("--max_iter", default=4, type=int)
    parser.add_argument("--temperature", default=0.2, type=float)
    parser.add_argument("--use_tool", type=strtobool, default=True)
    args = parser.parse_args()
    return args


def call_gpt3_5(messages, model, temperature):
    completion = openai.ChatCompletion.create(
        model=model,
        messages= messages,
        temperature=temperature,
        max_tokens=1000,
    )
    result = completion.choices[0].message['content'].strip()
    token_usage = completion.usage['total_tokens']
    print(token_usage)

    return result,token_usage


def critic(args):
    prompt = load_prompt(args.data, args.critic_type)

    print("%" * 30, "Critic", "%" * 30)
    now = datetime.now()
    dt_string = now.strftime("%m-%d_%H-%M")
    init_file = ""
    out_file = f'outputs/{args.model}/{args.data}/{args.split}_{args.critic_type}_{args.num_test_sample}_t{args.temperature}_seed{args.seed}_s{args.start}_e{args.end}_{dt_string}.jsonl'
    with DualStream(f'outputs/{args.model}/{args.data}/print/critic_{args.max_iter}_{args.start}-{args.end}.txt'):
        writer = open(out_file, 'w')

        for idx, sample in enumerate(load_jsonl(init_file)):
            if idx < args.start or (args.end != -1 and idx >= args.end):
                continue
            print("\n\n" + "=" * 30, "Idx", idx, "=" * 30)

            sample = {**{'idx': idx}, **sample}
            token = []

            for itr in range(1, args.max_iter + 1):
                token_sum = 0
                if itr == 1:
                    print("Is initial program correct:", sample['gt'] == sample['pred'])
                    sample['pred'] = [sample['pred']]
                    sample['report'] = [sample['report']]
                print("\n" + "-" * 20, "iteration", itr, "-" * 20)


                base_idx = itr - 1
                while base_idx > 0 and sample['pred'][base_idx] is None:
                    base_idx -= 1
                print("Correct based on iter:", base_idx)
                previous_code = remove_comment(sample['code'][base_idx])


                context = f"Question: {sample['question']}\n"
                context += f"{previous_code}\n"
                if args.use_tool:
                    context += f"Execution: {sample['report'][base_idx]}\n"
                    context += f"Output: {floatify_ans(sample['pred'][base_idx])}\n"
                context += "\nWhat's the problem with the above code?\n\n"
                prompt_critic = prompt + context
                print(context, end="")

                messages = [{"role": "system",
                             "content": "You are a mathematics and programming expert. Given previous responses, including a question, a python code solution and the output of this code, you should carefully evaluate these responses and provide detailed feedback."},
                            {"role": "user", "content": prompt_critic}]
                result, token_idx = call_gpt3_5(messages, model=args.model, temperature=args.temperature)
                token_sum += token_idx

                context_reflect = result if result else ""

                if context_reflect and context_reflect[-1] != "\n":
                    context_reflect += "\n"

                user_reflect_prompt=context + context_reflect
                print("-"*30)
                print(user_reflect_prompt, end="")

                sys_reflect_prompt = (
                    f"You are a mathematics and programming expert. Based on evaluation feedback including a question, a python code solution, the output of this code, and the code evaluation, you should generate a better code based on the feedback."
                    f"Your response should follow the format below:"
                    f"Here's a better code:\n"
                    f"```python\n"
                )


                messages = [{"role": "system", "content": sys_reflect_prompt},
                            {"role": "user", "content": user_reflect_prompt}]
                result,token_idx = call_gpt3_5(messages, model=args.model, temperature=args.temperature)
                token_sum += token_idx
                token.append(token_sum)


                code = result.strip() if result else ""
                code = extract_code_block(code)
                code = code.replace("```python", "").replace("```", "").replace("```Python", "").strip()
                pred, report = safe_execute(code)
                pred = floatify_ans(pred)


                corrected = True
                print("{}\n".format(code))
                print("Execution:", report)
                print("Output: answer =", pred)


                if code.strip() == sample['code'][base_idx].strip(): 
                    corrected = False
                    code = sample['code'][base_idx]
                    report = sample['report'][base_idx]
                    pred = sample['pred'][base_idx]

    
                sample['code'].append(code)
                sample['report'].append(report)
                sample['pred'].append(pred)
                is_correct = finqa_equal(pred, sample['gt'])



                print("Gold Answer:", sample['gt'])
                print("Corrected:", "Yes" if corrected else "No")
                print("Is correct:", is_correct)




            sample['token'] = token
            writer.write(json.dumps(sample) + '\n')
            writer.flush()

        writer.close()


if __name__ == "__main__":
    args = parse_args()
    set_seed((args.seed))
    critic(args)
