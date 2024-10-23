<h1 align="center">
Instruct-of-Reflection: Enhancing Large Language Models Iterative Reflection Capabilities via Dynamic-Meta Instruction
<br>

</h1>

<div align="center">

![](https://img.shields.io/badge/Task-Mathematical%20Reasoning-orange)
![](https://img.shields.io/badge/Task-Commonsense%20Reasoning-yellow)
<br>

</div>

<!-- set larger font size for the following text-->
<p style="font-size:1.05rem">
We conducted a comprehensive analysis of the iterative reflection performance of LLMs. The empirical evidence suggests that the performances of these reflection methods are unsatisfactory, primarily due to the limitations of static iterative reflection, which leads to redundant, drift, and stubborn issues. 
<br>
</p>

<p align="center">
    <img src="./images/framework.png" width="700">
</p>

To mitigate this, we propose Instruct-of-Reflection (IoRT), a dynamic iterative reflection framework that integrates abstract reasoning into the reflection,  generating adaptive instruction to regulate the iterative reflection. 

## Setup

We recommend the use of conda environments:

```sh
conda create --name iort python=3.8
conda activate iort
pip install -r requirements.txt
```

## 🚀 Quick Start

We provide example bash scripts for each task as follows:



### Mathematical Reasoning
GSM8K:
- Meta: `python -m src.meta-thinker`
- Refresh: `python -m src.GSM8K.inference`
- IoRT: `python -m src.GSM8K.iort`
- Evaluation: `python -m src.GSM8K.eval`

SVAMP:
- Refresh: `python -m src.SAVMP.inference`
- IoRT: `python -m src.SVAMP.iort`
- Evaluation: `python -m src.GSM8K.eval`
  
### Commonsense Reasoning
- Meta: `python -m src.meta-thinker`
- Inference: `python -m src.StrategyQA.inference`
- IoRT: `python -m src.StrategyQA.iort`
- Evaluation: `python -m src.StrategyQA.eval`

