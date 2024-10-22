import os
import time
import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential

# 设置环境变量
os.environ['OPENAI_API_KEY'] = "sk-ZdGNwCsoe0HhUnK6A9A29c42EdF4415e9a4c2b2495EaAa18"
os.environ['OPENAI_API_BASE'] = "https://api.xiamoai.top/v1"


# os.environ['OPENAI_API_KEY']="zk-08507a246a7f1fc844185def5ae9ef2b"
# os.environ['OPENAI_API_BASE']="https://flag.smarttrot.com/v1/"
# # 设置OpenAI API
openai.api_key = os.environ["OPENAI_API_KEY"]
openai.api_base = os.environ['OPENAI_API_BASE']


# 定义重试机制



# 定义调用API的函数
def llm(prompt, model, temperature=0.4, stop=None, logprobs=None, n=1, max_tokens=512):
    parameters = {
        "prompt": prompt,
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "n": n,
        "stop": stop,
        "logprobs": logprobs
    }

    # 调用API
    resp = completion_with_backoff(**parameters)
    return resp


# 测试函数
def test_llm():
    model = "davinci-002"
    prompt = "American Callan Pinckney’s eponymously named system became a best-selling (1980s-2000s) book/video franchise in what genre?"

    response = llm(prompt, model, stop="\n", max_tokens=20)
    print(response)


# 主程序入口
if __name__ == "__main__":
    test_llm()
