# PartPrompt

This repository contains the code and data for the paper: Parse Trees Guided LLM Prompt Compression.

## Experiments

To reproduce the experiments from the paper:

1. Install packages

   ```
   pip install nltk
   pip install collections
   pip install transformers
   ```

2. Download [Llama-7B](https://huggingface.co/meta-llama/Llama-2-7b)  model from [HuggingFace](https://huggingface.co/)

3. Choose a dataset. For BBCnews, it's like this

   ```
   python -u main.py BBCnews 0.2,0.3,0.5 1.0,1.0,0.7,4.0,0.0,100.0 1
   ```

## Citation

If you find this repository helpful or use our method in your research, please consider citing our paper:

```
@article{mao2024partprompt,
  title={Parse Trees Guided LLM Prompt Compression},
  author={Mao, Wenhao and Hou, Chengbin and Zhang, Tianyu and Lin, Xinyu and Tang, Ke and Lv, Hairong},
  journal={arXiv preprint arXiv:2409.15395},
  year={2024}
}
```

## License

This project is licensed under the [MIT License](LICENSE).
