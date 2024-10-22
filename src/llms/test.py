import pandas
import os, sys
import openai
from tenacity import (retry, stop_after_attempt, wait_random_exponential)
import tiktoken
import csv
# f1 = open('C:\\Users\\16549\\Desktop\\图谱项目\\图谱输出\\移动通信\\移动通信二三级目录.csv', 'w',newline='', encoding='utf-8')
# csv_writer = csv.writer(f1)


os.environ['OPENAI_API_KEY']="zk-08507a246a7f1fc844185def5ae9ef2b"
os.environ['OPENAI_API_BASE']="https://flag.smarttrot.com/v1/"
# os.environ['OPENAI_API_KEY']="sk-ZdGNwCsoe0HhUnK6A9A29c42EdF4415e9a4c2b2495EaAa18"
# os.environ['OPENAI_API_BASE']="https://api.xiamoai.top/v1"


openai.api_key = os.environ["OPENAI_API_KEY"]
openai.api_base=os.environ['OPENAI_API_BASE']

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(7))
def completion_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)

def ask_chat(system_content,line):
    response = completion_with_backoff(
        # model="text-davinci-003",
        model="gpt-3.5-turbo",
        # model="gpt-3.5-turbo-16k-0613",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": line},
        ],
        top_p=0.1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response

#只抽描述
system_content = '''
As a Communication Assistant, Your task is to give an English name of the knowledge points.
Be vigilant for any meaningless or irrelevant content.
Your output will be an English name of the knowledge points.
The input I provide you is a Chinese course knowledge point,you need to give a more official description of this knowledge point,
preferably Baidu Encyclopedia or Wikipedia description.
your output is a Chinese description of this Chinese knowledge point.The output is all Chinese sentences.
The output sentences should be as concise and concise as possible
                '''
# # 只抽描述
# system_content = '''
# As a Communication Assistant, The input I provide you is a Chinese course knowledge point,
# you need to give the chinese prior knowledge points of this knowledge point I provide you,
# The so-called prior knowledge point is the knowledge point that needs to be mastered in advance before learning the knowledge point I provide you.
# Only list the prior knowledge points, do not explain these knowledge points
# Because there may be several prior knowledge points ,Use commas to link all prior points together to form a sentence.
# Your output is a chinese sentence composed of prior knowledge points.
# Be vigilant for any meaningless or irrelevant content.

                # '''

# system_content = '''
# As a Communication Assistant, Your task is to give an English name of the knowledge points.
# Be vigilant for any meaningless or irrelevant content.
# Your output will be an English name of the knowledge points.
# The input I provide you is a Chinese course knowledge point,your output is an English name of this Chinese knowledge point.
# user_content = ""
# '''

with open('C:\\Users\\16549\\Desktop\\图谱项目\\图谱输出\\移动通信\\移动通信原理与系统.csv', 'r',encoding='utf-8') as f:
    reader = csv.reader(f)
    for i in reader:
        #id = (i[0])
        kg_name = (i[0])
        # kg1=(i[1])
        # kg2=(i[2])
        # height=(i[3])
        en = (i[1])
        ranker = (i[2])
        start_name = (i[4])
        start_id = (i[3])
        tp=(i[5])
        level = (i[6])
        response = ask_chat(system_content,kg_name)
        #completion = response['choices'][0]["message"]["content"]
        print(kg_name)
        print(response)
        #print(completion)
        # csv_writer.writerow([kg_name, en, ranker, start_name, start_id, tp,level, completion])
        #csv_writer.writerow([kg_name,kg1,kg2,height,completion])