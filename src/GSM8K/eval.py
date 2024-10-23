
import json
from src.GSM8K.utils import *




filename1=""
filename2=""
filename3=""


def calculate_accuracy(jsonl_file):
    # Initialize counters for each iteration
    num_iterations = 0
    correct_counts = []
    total_counts = []

    with open(jsonl_file, 'r', encoding='utf-8') as file:
        for line in file:
            data = json.loads(line)
            answer = data['gt']
            iteration_answer = data['iteration_answer']
            while len(iteration_answer)<6:
                iteration_answer.append(iteration_answer[-1])

            if isinstance(answer,str):
                answer = float(answer.replace(",", ""))

            # Initialize counters for this specific file
            if num_iterations == 0:
                num_iterations = len(iteration_answer)
                correct_counts = [0] * num_iterations
                total_counts = [0] * num_iterations

            # Update counts
            for i, iter_answer in enumerate(iteration_answer):
                if iter_answer is None:
                    for j in range(i-1, -1, -1):
                        if iteration_answer[j] is not None:
                            iter_answer = iteration_answer[j]
                            break


                if iter_answer is not None:
                    if finqa_equal(iter_answer, answer):
                        correct_counts[i] += 1
                total_counts[i] += 1


    # Calculate accuracy for each iteration
    accuracies = []

    # Print correct counts and total number of predictions
    for i, count in enumerate(correct_counts):
        accuracy = count / total_counts[i]
        accuracies.append(accuracy)

    return accuracies

accuracies = calculate_accuracy(filename2)

print("IoRT",accuracies)
print("--------------------------------------------")



def calculate_accuracy_pred(jsonl_file):
    # Initialize counters for each iteration
    num_iterations = 0
    correct_counts = []
    total_counts = []

    with open(jsonl_file, 'r', encoding='utf-8') as file:
        for line in file:
            data = json.loads(line)
            answer = data['gt']
            iteration_answer = data['pred']
            if isinstance(answer,str):
                answer = float(answer.replace(",", ""))

            while len(iteration_answer)<6:
                iteration_answer.append(iteration_answer[-1])

            # Initialize counters for this specific file
            if num_iterations == 0:
                num_iterations = len(iteration_answer)
                correct_counts = [0] * num_iterations
                total_counts = [0] * num_iterations

            # Update correct counts
            for i, iter_answer in enumerate(iteration_answer):
                if iter_answer is None:
                    for j in range(i-1, -1, -1):
                        if iteration_answer[j] is not None:
                            iter_answer = iteration_answer[j]
                            break

                # Update counts if the answer is no longer null
                if iter_answer is not None:
                    if finqa_equal(iter_answer, answer):
                        correct_counts[i] += 1
                total_counts[i] += 1
    accuracies = []

    # Print correct counts and total number of predictions
    for i, count in enumerate(correct_counts):
        accuracy = count / total_counts[i]
        accuracies.append(accuracy)

    return accuracies


# Example usage
accuracies = calculate_accuracy_pred(filename3)
print("iort (w/o SC)",accuracies)


def calculate_accuracy_pot(jsonl_file):
    # Initialize counters for each iteration

    correct_counts = 0
    total_counts = 0
    with open(jsonl_file, 'r', encoding='utf-8') as file:
        for line in file:

            data = json.loads(line)
            answer = data['gt']
            idx=data['idx']
            # if isinstance(answer,str):
            #     answer = float(answer.replace(",", ""))

            iteration_answers = data['pred']

            # Initialize counters for this specific file

            if finqa_equal(iteration_answers, answer):
                correct_counts+= 1
                #print(idx)

            total_counts += 1
            idx+=1

        accuracy = correct_counts / total_counts
        print(correct_counts)
        print(total_counts)
    return accuracy

accuracies = calculate_accuracy_pot(filename3)
print(accuracies)