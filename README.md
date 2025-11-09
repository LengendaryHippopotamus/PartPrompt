# PartPrompt: Parse Trees Guided LLM Prompt Compression

This repository contains the code and data for the paper: [Parse Trees Guided LLM Prompt Compression](https://ieeexplore.ieee.org/document/11164467), accepted to **IEEE Transactions on Pattern Analysis and Machine Intelligence (TPAMI)**.

---

## 🧠 Overview

**PartPrompt** is a novel **selective prompt compression** method that leverages **linguistic parse trees** and **global hierarchical structure** to compress prompts for Large Language Models (LLMs). By transforming prompt compression into a **tree pruning problem**, PartPrompt effectively preserves key information while significantly reducing input length and computational cost.

### Why PartPrompt?

- 🚀 **Efficient Compression**: Reduces LLM inference cost and latency.
- 🌳 **Structure-Aware**: Incorporates syntactic and document-level structure.
- 🧩 **Coherence-Preserving**: Maintains prompt coherence and readability.
- 🌍 **Multi-Scenario Support**: Works across English, non-English, code, and long-context prompts.

## 🔥 Key Features

- **Parse Tree Guidance**: Uses syntactic parse trees to guide token selection.
- **Global Hierarchical Tree**: Models document structure (sentence → paragraph → section → document).
- **Root-ward & Leaf-ward Propagation**: Adjusts token importance based on writing logic.
- **Tokenizer Alignment**: Avoids fragmented tokens and improves coherence.
- **Efficient Entropy Approximation**: Speeds up computation without sacrificing performance.

## 📊 Performance Highlights

PartPrompt achieves **state-of-the-art performance** across:

- ✅ **8 diverse datasets** (e.g., BBCnews, arXiv, PeopleDaily, CodeNet, HotpotQA, GSM8K, RULER, LongBench)
- ✅ **Multiple compression ratios** (10%–90%)
- ✅ **Various LLMs** (Mixtral, Llama, Qwen, etc.)
- ✅ **Multiple metrics** (BLEU, ROUGE, BERTScore, discourse metrics)

---
## 🚀 Quick Start

To reproduce the experiments from the paper:

1. Install packages

```bash
pip install nltk transformers accelerate
```

2. Download [Llama-7B](https://huggingface.co/meta-llama/Llama-2-7b)  model (or other similar model) from [HuggingFace](https://huggingface.co/)

3. Choose a dataset. For BBCnews, it's like this

```bash
python -u main.py BBCnews 0.2,0.3,0.5 1.0,1.0,0.7,4.0,0.0,100.0 1
```

- `0.2,0.3,0.5`: Compression ratios
- `1.0,1.0,0.7,4.0,0.0,100.0`: Hyperparameters

## 📁 Dataset

We provide cleaned and re-crawled versions of:

- BBCnews
- arXiv
- PeopleDaily (Chinese)
- CodeNet (code prompts)

All datasets are included in this repository.

---

## Citation

If you find this repository helpful or use our method in your research, please consider citing our paper:

```bibtex
@article{mao2025parse,
  title={Parse trees guided LLM prompt compression},
  author={Mao, Wenhao and Hou, Chengbin and Zhang, Tianyu and Lin, Xinyu and Tang, Ke and Lv, Hairong},
  journal={IEEE Transactions on Pattern Analysis and Machine Intelligence},
  year={2025},
  publisher={IEEE}
}
```

## License

This project is licensed under the [MIT License](LICENSE).

## 🌐 Links

- [📄 Paper (IEEE Xplore)](https://ieeexplore.ieee.org/document/11164467)
- [📄 Paper (arXiv)](https://arxiv.org/abs/2409.15395)

