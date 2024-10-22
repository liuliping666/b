import json
from src.program.utils import *




def llp_eval(filename):
    correct = 0
    wrong = 0
    correct0 = 0
    wrong0 = 0
    correct1 = 0
    wrong1 = 0
    correct2 = 0
    wrong2 = 0
    correct3 = 0
    wrong3 = 0
    correct4 = 0
    wrong4 = 0
    correct5 = 0
    wrong5 = 0
    correct6 = 0
    wrong6 = 0
    correct7 = 0
    wrong7 = 0
    correct8 = 0
    wrong8 = 0
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            entry = json.loads(line.strip())
            gt = entry.get('gt')
            best_pred = entry.get('best_pred')
            pred = entry.get('pred')

            itr_list = entry.get('itr_list')
            itr_result=entry.get('pred')

            itr_result0=pred[0]
            itr_result1 = itr_result[1]
            itr_result2 = itr_result[2]
            itr_result3 = itr_result[3]
            itr_result4 = itr_result[4]
            itr_result5 = itr_result[5]
            itr_result6 = itr_result[6]
            itr_result7 = itr_result[7]
            itr_result8 = itr_result[8]




            # 定义新的 itr_result
            # 读取 jsonl 文件

            is_correct = finqa_equal(best_pred, gt)
            is_correct0 = finqa_equal(itr_result0, gt)
            is_correct1 = finqa_equal(itr_result1, gt)
            is_correct2 = finqa_equal(itr_result2, gt)
            is_correct3 = finqa_equal(itr_result3, gt)
            is_correct4 = finqa_equal(itr_result4, gt)
            is_correct5 = finqa_equal(itr_result5, gt)
            is_correct6 = finqa_equal(itr_result6, gt)
            is_correct7 = finqa_equal(itr_result7, gt)
            is_correct8 = finqa_equal(itr_result8, gt)
            if is_correct:
                correct += 1
            else:
                wrong += 1
            if is_correct0:
                correct0 += 1
            else:
                wrong0 += 1
            if is_correct1:
                correct1 += 1
            else:
                wrong1 += 1
            if is_correct2:
                correct2 += 1
            else:
                wrong2 += 1
            if is_correct3:
                correct3 += 1
            else:
                wrong3 += 1
            if is_correct4:
                correct4 += 1
            else:
                wrong4 += 1
            if is_correct5:
                correct5 += 1
            else:
                wrong5 += 1
            if is_correct6:
                correct6 += 1
            else:
                wrong6 += 1
            if is_correct7:
                correct7 += 1
            else:
                wrong7 += 1
            if is_correct8:
                correct8 += 1
            else:
                wrong8 += 1

            # if gt == pred:
            #     correct += 1
            # else:
            #     wrong += 1


            # 输出结果
        print("改进方法：")
        # print(f"正确 (correct): {correct0}")
        # print(f"错误 (incorrect): {wrong0}")
        # print(correct0 / (correct0 + wrong0))
        # print("---------------------------------------")
        # print("迭代方法1：")
        # print(f"正确 (correct): {correct1}")
        # print(f"错误 (incorrect): {wrong1}")
        # print(correct1 / (correct1 + wrong1))
        # print("---------------------------------------")
        # print("迭代方法2：")
        # print(f"正确 (correct): {correct2}")
        # print(f"错误 (incorrect): {wrong2}")
        # print(correct2 / (correct2 + wrong2))
        # print("---------------------------------------")
        # print("迭代方法3：")
        # print(f"正确 (correct): {correct3}")
        # print(f"错误 (incorrect): {wrong3}")
        # print(correct3 / (correct3 + wrong3))
        # print("---------------------------------------")
        # print("迭代方法：")
        # print(f"正确 (correct): {correct}")
        # print(f"错误 (incorrect): {wrong}")
        # print(correct / (correct + wrong))
        # print("---------------------------------------")
        print([correct0 / (correct0 + wrong0), correct1 / (correct1 + wrong1), correct2 / (correct2 + wrong2),
               correct3 / (correct3 + wrong3),correct4 / (correct4 + wrong4), correct5 / (correct5 + wrong5), correct6 / (correct6 + wrong6),
               correct7 / (correct7 + wrong7), correct8 / (correct8 + wrong8)])


def critic_result(filename):
    correct = 0
    wrong = 0
    correct0 = 0
    wrong0 = 0
    correct1 = 0
    wrong1 = 0
    correct2 = 0
    wrong2 = 0
    correct3 = 0
    wrong3 = 0
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            entry = json.loads(line.strip())
            gt = entry.get('gt')
            pred = entry.get('pred')[-1]
            pred0 = entry.get('pred')[0]
            pred1 = entry.get('pred')[1]
            pred2 = entry.get('pred')[2]
            pred3 = entry.get('pred')[3]
            # 定义新的 itr_result
            # 读取 jsonl 文件

            is_correct = finqa_equal(pred, gt)
            is_correct0 = finqa_equal(pred0, gt)
            is_correct1 = finqa_equal(pred1, gt)
            is_correct2 = finqa_equal(pred2, gt)
            is_correct3 = finqa_equal(pred3, gt)
            if is_correct:
                correct += 1
            else:
                wrong += 1
            if is_correct0:
                correct0 += 1
            else:
                wrong0 += 1
            if is_correct1:
                correct1 += 1
            else:
                wrong1 += 1
            if is_correct2:
                correct2 += 1
            else:
                wrong2 += 1
            if is_correct3:
                correct3 += 1
            else:
                wrong3 += 1


        print("原始方法：")
        # print(f"正确 (correct): {correct0}")
        # print(f"错误 (incorrect): {wrong0}")
        # print(correct0 / (correct0 + wrong0))
        # print("---------------------------------------")
        # print("原始方法1：")
        # print(f"正确 (correct): {correct1}")
        # print(f"错误 (incorrect): {wrong1}")
        # print(correct1 / (correct1 + wrong1))
        # print("---------------------------------------")
        # print("原始方法2：")
        # print(f"正确 (correct): {correct2}")
        # print(f"错误 (incorrect): {wrong2}")
        # print(correct2 / (correct2 + wrong2))
        # print("---------------------------------------")
        # print("原始方法3：")
        # print(f"正确 (correct): {correct3}")
        # print(f"错误 (incorrect): {wrong3}")
        # print(correct3 / (correct3 + wrong3))
        # print("---------------------------------------")
        # print("原始方法：")
        # print(f"正确 (correct): {correct}")
        # print(f"错误 (incorrect): {wrong}")
        # print(correct / (correct + wrong))
        # print("---------------------------------------")
        print([correct0 / (correct0 + wrong0),correct1 / (correct1 + wrong1),correct2 / (correct2 + wrong2),correct3 / (correct3 + wrong3),correct / (correct + wrong)])

# 读取JSON文件内容
filename1='C:/Users/16549/PycharmProjects/CRITIC_1/src/program/outputs/gpt-3.5-turbo-instruct/gsm8k/0-200/test_critic_200.jsonl'
filename2='C:/Users/16549/PycharmProjects/CRITIC_1/src/program/outputs/gpt-3.5-turbo-instruct/gsm8k/llp_correct.jsonl'
llp_eval(filename2)
critic_result(filename1)


