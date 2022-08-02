from libmultilabel.nn.data_utils import load_datasets, load_or_build_label, \
                                        load_or_build_text_dict, get_dataset_loader
from libmultilabel.nn.nn_utils import init_device, init_model, init_trainer, set_seed
from transformers import AutoTokenizer

# Step 0. Setup device.
set_seed(1337)
device = init_device()  # use gpu by default

# Step 1. Load data from text files.
datasets = load_datasets(
        'data/EUR-Lex-57k/train.txt',
        'data/EUR-Lex-57k/test.txt',
        'data/EUR-Lex-57k/val.txt',
        tokenize_text=False,
        )
classes = load_or_build_label(datasets, include_test_labels=True)

# Step 2. Initialize a model.
network_config = {
    'dropout': 0.1,
    'lm_weight': 'bert-base-uncased',
    'lm_window': 512,
    'attention_type': 'singlehead',
}
model = init_model(model_name='BERTAttention',
                   network_config=network_config,
                   classes=classes,
                   init_weight=None,
                   word_dict=None,
                   learning_rate=0.00005,
                   optimizer='adamw',
                   weight_decay=0.001,
                   monitor_metrics=['Micro-F1', 'Macro-F1', 'P@1', 'P@3', 'P@5']
                   )

# Step 3. Initialize a trainer.
trainer = init_trainer(checkpoint_dir='runs/EUR-Lex-57k-BERTAttention-example',
                       epochs=15,
                       val_metric='P@5')

# Step 4. Create data loaders.
loaders = dict()
tokenizer = AutoTokenizer.from_pretrained(network_config['lm_weight'], use_fast=True)
for split in ['train', 'val', 'test']:
    loaders[split] = get_dataset_loader(data=datasets[split],
                                        word_dict=None,
                                        classes=classes,
                                        device=device,
                                        max_seq_length=512,
                                        batch_size=8,
                                        shuffle=True if split == 'train' else False,
                                        tokenizer=tokenizer)

# Step 5-1. Train a model from scratch.
trainer.fit(model, loaders['train'], loaders['val'])

# Step 5-2. Test the model.
trainer.test(model, test_dataloaders=loaders['test'])
