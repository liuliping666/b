import os
import json
import time
import pprint
import requests
import openai

os.environ['OPENAI_API_KEY'] = "zk-08507a246a7f1fc844185def5ae9ef2b"
os.environ['OPENAI_API_BASE'] = "https://flag.smarttrot.com/v1/"

# os.environ['OPENAI_API_KEY']="sk-ZdGNwCsoe0HhUnK6A9A29c42EdF4415e9a4c2b2495EaAa18"
# os.environ['OPENAI_API_BASE']="https://api.xiamoai.top/v1"


openai.api_key = os.environ["OPENAI_API_KEY"]
openai.api_base = os.environ['OPENAI_API_BASE']


# openai.api_key = os.environ["OPENAI_API_KEY"]


def llm(prompt, model, temperature=0, stop=None, logprobs=None, n=1, max_tokens=512, verbose=False):
    for trial in range(3):
        if trial > 0:
            time.sleep(trial * 2)
        try:
            # set parameters
            parameters = {
                "prompt": prompt,
                "model": model,
                "max_tokens": max_tokens,
                "stop": stop,
                "temperature": temperature,
                "n": n,
                "logprobs": logprobs
            }
            parameters.update({"prompt": prompt})
            resp = openai.Completion.create(**parameters)
            if verbose:
                print(resp)
            text = resp.choices[0].text
            assert len(text) > 0
        except BaseException as e:
            print(">" * 20, "LLMs error", e)
            resp = None
        if resp is not None:
            break
    return resp


def _test_llm():
    model = "davinci-002"

    prompt = "Q: American Callan Pinckney’s eponymously named system became a best-selling (1980s-2000s) book/video franchise in what genre?"
    prompt += "A: "
    llm(prompt, model, stop="\n", max_tokens=20, verbose=True)


if __name__ == "__main__":
    _test_llm()
