import json
import os
from datetime import datetime
from time import sleep
from tqdm import tqdm
import argparse
from collections import Counter
from distutils.util import strtobool
import openai
from src.llms.api import llm
from src.datasets.dataset_loader import DatasetLoader
from src.utils import load_prompt, set_seed, load_jsonl
from src.tools.interpreter_api import safe_execute,extract_code_block
from src.GSM8K.utils import *
import sys
from time import time


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
    parser.add_argument("--start", default=0, type=int)
    parser.add_argument("--end", default=-1, type=int)
    parser.add_argument("--max_iter", default=4, type=int)
    parser.add_argument("--temperature", default=0.2, type=float)
    parser.add_argument("--use_tool", type=strtobool, default=True)
    args = parser.parse_args()
    return args

def compare_codes(meta_thought, question, code1, answer1, code2,  answer2,args):
    compare_prompt = (
        f"The outputs from the two codes are different. Evaluate the following two Python code snippets based on the given question, output of the code and meta thought, and recommend which code is better to solve this question and explain why."
        f"**Question:**\n{question}\n\n"
        f"**Meta_thought:**\n{meta_thought}\n\n"
        f"**Code 1:**\n```python\n{code1}\n```\n\n"
        f"**Output 1:** {floatify_ans(answer1)}\n\n"
        f"**Code 2:**\n```python\n{code2}\n```\n\n"
        f"**Output 2:** {floatify_ans(answer2)}\n\n"
        f"**Instructions:**\n\n"
        f"Respond with 'Better Code: Code 1' or 'Better Code: Code 2', followed by your explanation."
    )

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "system",
             "content": "You are a mathematics and programming expert."},
            {"role": "user", "content": compare_prompt}
        ],
        max_tokens=1000,
        temperature=args.temperature
    )

    print("-"*30)
    print(compare_prompt)
    print("-"*30)
    result = completion.choices[0].message['content'].strip()
    token_usage = completion.usage['total_tokens']
    print("token", token_usage)
    print(f"Model Response: {result}") 
    print("-"*30)
    better_code = "Code 2" if "Better Code: Code 2" in result else "Code 1"

    return better_code, token_usage



def decide_next_step(meta_thought, question, code1, answer1, code2, answer2, args):
    prompt = (
        f"The outputs from the two codes are the same. Please evaluate the following two Python code snippets based on the question, output of the code meta thought and output. Decide whether to refresh a new solution or to stop."
        f"**Question:**\n{question}\n\n"
        f"**Meta_thought:**\n{meta_thought}\n\n"
        f"**Code 1:**\n```python\n{code1}\n```\n\n"
        f"**Output 1:** {floatify_ans(answer1)}\n\n"
        f"**Code 2:**\n```python\n{code2}\n```\n\n"
        f"**Output 2:** {floatify_ans(answer2)}\n\n"
        f"**Instructions:**\n"
        f"Please respond with '**Refresh**' or '**End Iteration**', followed by your explanation."

    )

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "system",
             "content": "You are a mathematics and programming expert."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=args.temperature
    )

    result = completion.choices[0].message['content'].strip()
    token_usage = completion.usage['total_tokens']
    print("="*15,"Teacher stop or iteration decision","="*15)
    print(result)
    print("token", token_usage)
    next_step = "Refresh" if "**Refresh**" in result else "End Iteration"
    return next_step, token_usage

def call_gpt3_5(messages, model, temperature):
    completion = openai.ChatCompletion.create(
        model = model,
        messages = messages,
        temperature = temperature,
        max_tokens=1000,
    )
    result = completion.choices[0].message['content'].strip()
    token_usage = completion.usage['total_tokens']
    return result,token_usage


def critic_iter(sample, previous_report,previous_code,previous_answer, args):
    # load prompt
    prompt = load_prompt(args.data, args.critic_type)
    context = f"Question: {sample['question']}\n"
    previous_code = remove_comment(previous_code)
    context += f"{previous_code}\n"
    if args.use_tool:
        context += f"Execution: {previous_report}\n"
        context += f"Output: {floatify_ans(previous_answer)}\n"
    context += "\nWhat's the problem with the above code?\n\n"
    prompt_critic = prompt + context


    messages = [{"role": "system",
             "content":"You are a mathematics and programming expert. Given previous responses, including a question, a python code solution and the output of this code, you should carefully evaluate these responses and provide detailed feedback."},
        {"role": "user", "content": prompt_critic}]
    context_reflect,token1 = call_gpt3_5(messages, model=args.model, temperature=args.temperature)
    context_reflect = context_reflect if context_reflect else ""

    if context_reflect and context_reflect[-1] != "\n":
        context_reflect += "\n"

    user_reflect_prompt = context + context_reflect
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
    result,token2 = call_gpt3_5(messages, model=args.model, temperature=args.temperature)

    token_sum=token1+token2
    revised_code = result.strip() if result else ""
    revised_code = extract_code_block(revised_code)
    revised_code = revised_code.replace("```python", "").replace("```", "").replace("```Python", "").strip()
    revised_pred, revised_report= safe_execute(revised_code)
    revised_pred = floatify_ans(revised_pred)

    print("Here's a better code:")
    print("{}\n```".format(revised_code))
    print("Output:", revised_pred)
    print("token",token_sum)
    return revised_code,revised_report,revised_pred,token_sum


def refresh_code(question,args):
    demo_prompt = load_prompt(args.data, args.prompt_type)
    # construct prompt
    full_prompt = demo_prompt + f'Question: {question}' + '\n'
    full_prompt += '# Python code, return answer' + '\n'
    # call GPT-3.5
    messages = [{"role": "user", "content": full_prompt}]
    result,token_usage = call_gpt3_5(messages, model=args.model, temperature=args.temperature)
    # parse result
    ans, report = safe_execute(result)
    prediction = floatify_ans(ans)



    return result, prediction,token_usage


def critic(args):

    print("%" * 30, "Critic", "%" * 30)

    now = datetime.now()
    dt_string = now.strftime("%m-%d_%H-%M")
    init_file = f''
    out_file = f''

    with DualStream(''):
        writer = open(out_file, 'w')
        for idx, sample in enumerate(load_jsonl(init_file)):
            if idx < args.start or (args.end != -1 and idx >= args.end):
                continue
            sample['idx'] = sample['idx']
            print("\n\n" + "=" * 30, "Idx", sample['idx'], "=" * 30)

            sample = {**sample}
            sample['code'] = sample['code'][0] if isinstance(sample['code'], list) else str(sample['code'])
            sample['pred'] = sample['pred'][0] if isinstance(sample['pred'], list) else sample['pred']
            sample['report'] = sample['report'][0] if isinstance(sample['report'], list) else sample['report']
            best_pred = sample['pred']
            sample['pred'] = [best_pred]
            sample['report'] = [sample['report']]
            sample['code'] = [remove_comment(sample['code'])]
            sample['best_code'] = sample['code'][0]
            sample['best_report'] = sample['report'][0]
            sample['best_pred'] = sample['pred'][0]
            best_idx = 0
            temp_idx = 0
            token = []
            api = []

              # Initialize the iteration list
            action = ['inital_response']
            iteration = 0

            itr_id = [0]
            itr_result = [sample['best_pred']]
            itr_report = [sample['best_report']]
            new_itr_id = [temp_idx]
            while iteration < args.max_iter:
                if iteration == 0 or not finqa_equal(revised_pred, itr_base_pred):
                    iteration += 1
                    token_sum = 0
                    api_sum = 0
                    print("\n" + "-" * 20, "iteration", iteration, "-" * 20)
                    print("Correct based on iter:", best_idx)

                    itr_base_code = sample['best_code']
                    itr_base_report = sample['best_report']
                    itr_base_pred = sample['best_pred']

                    revised_code, revised_report, revised_pred,token_idx = critic_iter(sample, sample['best_code'],sample['best_report'], sample['best_pred'],args)
                    api_sum += 1
                    token_sum += token_idx
                    action.append('reflect')
                    sample['code'].append(revised_code)
                    sample['report'].append(revised_report)
                    sample['pred'].append(revised_pred)

                print("%"*15,"Compare Code","%"*15)
                print("Code 1:")
                print(itr_base_code)
                print("Code 2:")
                print(revised_code)
                print("Report 1:", itr_base_report)
                print("Report 2:", revised_report)
                print(f"Gold answer: {sample['gt']}")
                print("pred 1:", itr_base_pred)
                print("pred 2:", revised_pred)

                # Compare answers
                if not finqa_equal(revised_pred, itr_base_pred):
                    # Compare COTs and decide the better one
                    better_code,token_idx = compare_codes(sample['meta_thought'],sample['question'],itr_base_code,  itr_base_pred, revised_code,  revised_pred,args)
                    print(f"Better COT after comparison: {better_code}")

                    token_sum += token_idx
                    api_sum += 1
                    if better_code == "Code 2":
                        best_idx = iteration
                        temp_idx = iteration
                        sample['best_code'] = revised_code
                        sample['best_report'] = revised_report
                        sample['best_pred'] = revised_pred
                        print(f"Iteration {iteration} has better code. Updating the best code.")
                        itr_id.append(best_idx)  # Update the iteration list with the best iteration index so far
                        new_itr_id.append(temp_idx)
                        itr_result.append(sample['best_pred'])

                        itr_report.append(sample['best_report'])

                    else:
                        itr_id.append(best_idx)
                        new_itr_id.append(temp_idx)
                        itr_result.append(sample['best_pred'])

                        itr_report.append(sample['best_report'])
                        print(f"Iteration {iteration} does not improve the code. Keeping the best code.")
                else:
                    best_idx = iteration
                    temp_code = revised_code
                    temp_pred = revised_pred
                    temp_report = revised_report
                    itr_result.append(revised_pred)

                    itr_id.append(best_idx)
                    itr_report.append(revised_report)
                    new_itr_id.append(temp_idx)

                    if iteration + 1 <= args.max_iter:
                        decision,token_idx = decide_next_step(sample['meta_thought'],sample['question'], itr_base_code, itr_base_pred,revised_code, revised_pred, args)
                        api_sum += 1
                        api.append(api_sum)
                        token_sum += token_idx
                        token.append(token_sum)
                        if decision == "Refresh":
                            print("Decision: Refreshing a new COT.")
                            # Refresh a new COT
                            iteration += 1
                            token_sum = 0
                            api_sum = 0
                            print("\n" + "-" * 20, "iteration", iteration, "-" * 20)
                            revised_code,revised_report,revised_pred,token_idx = refresh_code(sample['question'], args)
                            token_sum += token_idx
                            api_sum += 1
                            action.append('Refresh')
                            print(revised_code)
                            print("Execution:",revised_report)
                            print("Output: answer =",revised_pred)
                            sample['code'].append(revised_code)
                            sample['report'].append(revised_report)
                            sample['pred'].append(revised_pred)

                            itr_base_pred = temp_pred
                            itr_base_code = temp_code
                            itr_base_report = temp_report
                            if not finqa_equal(revised_pred, itr_base_pred):
                                # Compare Codes and decide the better one
                                print("%"*15,"Compare Code","%"*15)
                                print("Code 1:")
                                print(itr_base_code)
                                print("Code 2:")
                                print(revised_code)
                                print("Report 1:", itr_base_report)
                                print("Report 2:", revised_report)
                                print(f"Gold answer: {sample['gt']}")
                                print("pred 1:", itr_base_pred)
                                print("pred 2:", revised_pred)

                                better_cot,token_idx = compare_codes(sample['meta_thought'],sample['question'],itr_base_code, itr_base_pred,revised_code,revised_pred,args)
                                api_sum += 1
                                api.append(api_sum)
                                token_sum += token_idx
                                token.append(token_sum)
                                print(f"Better COT after comparison: {better_cot}")

                                if better_cot == "COT 2":
                                    best_idx = iteration
                                    temp_idx = iteration
                                    sample['best_cot'] = revised_code
                                    sample['best_pred'] = revised_pred
                                    sample['best_report'] = revised_report
                                    print(f"Iteration {iteration} has better COT. Updating the best COT.")
                                    itr_id.append(best_idx)  # Update the iteration list with the best iteration index so far
                                    new_itr_id.append(temp_idx)
                                    itr_result.append(sample['best_pred'])
                                    itr_report.append(sample['best_report'])

                                else:
                                    itr_id.append(best_idx)
                                    new_itr_id.append(temp_idx)
                                    itr_result.append(sample['best_pred'])
                                    itr_report.append(sample['best_report'])
                                    print(f"Iteration {iteration} does not improve the COT. Keeping the best COT.")

                            elif iteration == args.max_iter:
                                best_idx = iteration
                                itr_id.append(best_idx)
                                new_itr_id.append(temp_idx)
                                itr_result.append(sample['best_pred'])
                                itr_report.append(sample['best_report'])
                                token.append(token_sum)
                                api.append(api_sum)



                        else:
                            print("Decision: Ending iteration with current best COT.")
                            break

            sample['iteration_id'] = itr_id
            sample['new_itr_id'] = new_itr_id
            sample['iteration_answer'] = itr_result
            sample['itr_report'] = itr_report
            sample['action'] = action
            sample['token'] = token
            sample['api'] = api

            writer.write(json.dumps(sample) + '\n')
            writer.flush()

        writer.close()

if __name__ == "__main__":
    args = parse_args()
    set_seed(args.seed)
    critic(args)
