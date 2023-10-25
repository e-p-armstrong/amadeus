# Augmental Dataset and Model Training Code

This repository contains the code used to generate the Augmental dataset, as well as the model training code to finetune models on it. The dataset stands out due to its innovative approach of utilizing AI to enhance human-written scripts from visual novels, bridging the gap between purely synthetic data and manual data curation.

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Data Generation](#data-generation)
4. [Model Training](#model-training)
5. [Acknowledgements](#acknowledgements)
6. [References and Useful Links](#references-and-useful-links)

## Introduction
The Augmental dataset is a novel multiturn dataset containing 7.86k replies spread across about 480 different conversations among 7 distinct characters. This dataset was crafted by refining and enhancing the script of the visual novel Steins;Gate using GPT-4. The dataset prioritizes quality, longer responses, and retaining the human-like essence of the conversation while benefitting from the capabilities of GPT-4.

## Prerequisites

### Dataset Source
The dataset is generated from the `.scx.txt` files of Steins;Gate. It's essential to have a legal copy of Steins;Gate to extract the required files. Please ensure you have the rights to use the text from the visual novel for your purposes.

### Tools
- [sc3tools](https://github.com/CommitteeOfZero/sc3tools) for extracting `.scx.txt` files from Steins;Gate.

## Data Generation

### Extraction and Preprocessing
1. Extract the `.scx.txt` files from Steins;Gate using [sc3tools](https://github.com/CommitteeOfZero/sc3tools).
2. Merge the extracted `.scx.txt` files into a single text file.

### Processing with Notebook
1. Open the `processing_refactor.ipynb` notebook.
2. Before running the notebook, ensure you've toggled the `dataset_has_been_manually_edited` flag at the top:
   - Set to `True` if working with the original dataset. If this is true, it (shouldn't) make any OAI calls and will leave any gaps in the dataset alone.
   - Set to `False` if you're generating new data.
3. Run the notebook to process the raw text file. The output will be the Augmental dataset, ready for model training.

## Model Training
The training code for finetuning models on the Augmental dataset is contained in `train.py`. 

### Usage
Use the processing_refactor notebook how you would normally use a notebook. Cells that run OpenAI will skip generations that have already been saved to files in the ./annotated_convs, ./scenarios, and ./anchors directories.
!!DO NOT DELETE FILES IN THOSE DIRECTORIES UNLESS YOU WANT PAINFUL ERRORS!!
```bash
python train.py
```

### Acknowledgements
This dataset is an evolution of the dataset that was used to train MythoMakise, a model that achieved notable recognition. The current model, trained on the Augmental dataset, promises even higher quality interactions and versatility.
See the note on the Augmental Dataset HF page for legal considerations. TLDR: if the legal holders of the Steins;Gate IP tell me to take this down I will without a second thought.

## References and Useful Links and Self-promotional Links
- [Reddit Post](https://www.reddit.com/r/AI/comments/abc123) introducing the dataset.
- [Model Card](https://github.com/e-p-armstrong/amadeus/blob/main/model_card.md) detailing the specifics and innovations behind the model.
- [Ko-fi Support Link](https://ko-fi.com/heralax)
- [Essay on Substack](https://promptingweekly.substack.com/p/human-sourced-ai-augmented-a-promising) discussing the rationale behind the dataset.

Feedback, suggestions, and contributions are always welcome! 
