<h1 align="center">

## Setup

We recommend the use of conda environments:

```sh
conda create --name iort python=3.8
conda activate iort
pip install -r requirements.txt
```

##  Quick Start

We provide example bash scripts for each task as follows:



### Mathematical Reasoning
GSM8K:
- Meta: `python -m src.meta-thinker`
- Refresh: `python -m src.GSM8K.inference`
- IoRT: `python -m src.GSM8K.iort`
- Evaluation: `python -m src.GSM8K.eval`

SVAMP:
- Meta: `python -m src.meta-thinker`
- Refresh: `python -m src.SAVMP.inference`
- IoRT: `python -m src.SVAMP.iort`
- Evaluation: `python -m src.GSM8K.eval`
  
### Commonsense Reasoning
- Meta: `python -m src.meta-thinker`
- Inference: `python -m src.StrategyQA.inference`
- IoRT: `python -m src.StrategyQA.iort`
- Evaluation: `python -m src.StrategyQA.eval`

