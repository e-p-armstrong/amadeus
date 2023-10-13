from datasets import Dataset
import os
import torch
import torch.nn as nn
import datasets
from datasets import Dataset
import bitsandbytes as bb
from transformers import AutoTokenizer, LlamaForCausalLM, TrainingArguments, BitsAndBytesConfig
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM
import json
from peft import LoraConfig, get_peft_model
import transformers
from make_card_alichat import make_card_alichat
from make_card_bullets import make_card_bullets
import json
import random

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def parse_json_file(json_file_path):
    # Initialize an empty list to store the reformatted dictionaries
    reformatted_list = []
    
    # Read the JSON file
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    # Iterate through each dictionary in the list
    for entry in data:
        # Initialize an empty list to store the parsed 'history' field
        parsed_history = []
        
        # Split the 'history' string by the newline character to get each line
        lines = entry['history'].split('\n')
        
        # Iterate through each line to parse the speaker and the line
        for line in lines:
            if ': ' in line:  # Checking if the line actually contains dialogue
                speaker, dialogue = line.split(': ', 1)  # Split at the first occurrence of ': '
                parsed_history.append((speaker, dialogue))
        
        # Create a new dictionary with the parsed 'history' field
        new_entry = {
            'history': parsed_history,
            'completion': entry['completion'],
            'scenario': entry['scenario']
        }
        
        # Append the new dictionary to the reformatted list
        reformatted_list.append(new_entry)
    
    return reformatted_list


json_file_path = "final_dataset.json"
reformatted_data = parse_json_file(json_file_path)

print(reformatted_data[0])


# New dataset code:
def format_chat_history(chat_history):
    return '\n'.join([f'### Response:\n#### Kurisu: {line}' if speaker == "Kurisu" else f'### Instruction:\n#### {speaker}: {line}' for speaker, line in chat_history])

card_dataset = []

for ex in reformatted_data: # make a version of the dataset with the first card
    card_dataset.append(make_card_alichat(ex["scenario"], format_chat_history(ex["history"]), ex["completion"]))
    
for ex in reformatted_data: # make a version with the second, so that the model doesn't learn to predict correctly when given only a very specific type of card (experiment)
    card_dataset.append(make_card_bullets(ex["scenario"], format_chat_history(ex["history"]), ex["completion"]))

# Load dataset and convert to Huggingface Dataset Dict
dataset = Dataset.from_list(card_dataset)

print(dataset,"\n\n\n")

# Sort datasets by length so that if longer examples cause memory issues, it'll happen first, and we can fix it without wasting time
# dataset = dataset.map(lambda example: {"text": example["text"], "length": len(example["text"])})
# dataset = dataset.sort("length", reverse=True)

tokenizer = AutoTokenizer.from_pretrained("Undi95/ReMM-Mistral-13B", max_length=4000, padding_side="right")
# tokenizer.add_special_tokens({"pad_token": "[PAD]"}) # Note, do not do this, it will break the embedding and cause a hard-to-fix error

tokenizer.pad_token_id = tokenizer.eos_token_id

# add eos token to training data
dataset = dataset.map(lambda example: {"text": example["text"] + tokenizer.eos_token})

dataset = dataset.train_test_split(test_size=0.05)

print(dataset)

print(dataset["train"][0]["text"])


# don't forget pip install -U git+https://github.com/lvwerra/trl

# Model time!

# Sillytavern response template: "### Response (2 paragraphs, engaging, natural, authentic, descriptive, creative):
#### Kurisu:"
response_template = [2277,
 29937,
 13291,
 313,
 29906,
 14880,
 29879,
 29892,
 3033,
 6751,
 29892,
 5613,
 29892,
 15585,
 29892,
 29037,
 573,
 29892,
 907,
 1230,
 1125,
 13,
 4136,
 9742,
 28311,
 29901]

# print("\n\n\n====================\n\n\n")
# print(type(response_template), response_template)
# print("\n\n\n====================\n\n\n")
# uncoment this and the thing in the sfttrainer to do completion only
# This is the only problem besides OOM, which will be solved by using vast.ai

# No prompt dropout this time, because I want to vary only one thing at a time
collator = DataCollatorForCompletionOnlyLM(
    # instruction_template="You are an expert roleplaying model", # If I have a response template I don't think I *need* this part. Probably.
    response_template=response_template, 
    tokenizer=tokenizer, 
    mlm=False
    )

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    llm_int8_enable_fp32_cpu_offloat=True,
    bnb_4bit_compute_dtype=torch.float16,
)

base_model = LlamaForCausalLM.from_pretrained(
    "Undi95/ReMM-Mistral-13B",
    quantization_config=quantization_config,
    device_map="auto",
    trust_remote_code=True,
    force_download=True, 
    resume_download=False
    )

lora_config = LoraConfig(
    r=64,
    lora_alpha=16,
    target_modules=["q_proj","k_proj","v_proj","o_proj", "gate_proj", "up_proj", "down_proj"
                    # "rotary_emb" # idk what this even is, so I'm hesitant to LoRA it. Try it later?
                    ],
    lora_dropout=0.05,
    bias="none", 
    task_type="CAUSAL_LM",# the weird index issue was solved by correctly specifying the task type in CAPS
)

model = get_peft_model(base_model, lora_config)
model.print_trainable_parameters()

model.enable_input_require_grads() # sometimes prevents an error for some reason
# model.gradient_checkpointing_enable()

training_args = TrainingArguments(
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=32,
    gradient_checkpointing=True,
    learning_rate=1e-4,
    num_train_epochs=2,
    save_strategy="epoch",
    # save_steps=len(reformatted_data), # save every time we go through the dataset once, not through the dataset 2x
    logging_steps=1,
    fp16=True,
    output_dir="outputs",
    per_device_train_batch_size=2,
)

trainer = SFTTrainer( 
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    tokenizer=tokenizer,
    # data_collator=transformers.DataCollatorForLanguageModeling(tokenizer,mlm=False),#
    data_collator=collator, 
    max_seq_length=4000,
    dataset_text_field="text",
)

trainer.train()
trainer.save_model("MistralMakise-13b-")