import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

from dante_by_word.data_preparation import build_vocab
from dante_by_word.text_processing import clean_comedy, prettify_text, special_tokens
from dante_by_word.generate_dante import generate_text
from utils import save_vocab, load_vocab


working_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dante_by_word')

divine_comedy_file = os.path.join(os.path.dirname(working_dir), "divina_commedia", "divina_commedia_accent_UTF-8.txt") 


with open(divine_comedy_file,"r") as f:
    divine_comedy = f.read()

divine_comedy = clean_comedy(divine_comedy, special_tokens)

vocab, idx2word, word2idx = build_vocab(divine_comedy)

# Path where the vocab is saved
logs_dir = os.path.join(working_dir, 'logs')
os.makedirs(logs_dir, exist_ok = True) 
vocab_file = os.path.join(logs_dir, 'vocab.json')

vocab, idx2word, word2idx = load_vocab(vocab_file)

# Length of the vocabulary
vocab_size = len(vocab)


# Path where the model is saved
models_dir = os.path.join(working_dir, 'models')
os.makedirs(models_dir, exist_ok = True) 
model_file = os.path.join(models_dir, "dante_by_word_model.h5")

model = tf.keras.models.load_model(model_file)

SEQ_LENGTH = model.get_layer('embedding').output.shape[1]
EMBEDDING_DIM = model.get_layer('embedding').output.shape[2]
for l in model.layers:
    if l.name == 'first_lstm':
        RNN_TYPE = '2lstm'
        break
    if l.name == 'last_lstm':
        RNN_TYPE = 'lstm' 
        break
    if l.name == 'first_gru':
        RNN_TYPE = '2gru' 
        break
    if l.name == 'last_gru':
        RNN_TYPE = 'gru' 
        break
if 'lstm' in RNN_TYPE:
    RNN_UNITS = model.get_layer('last_lstm').output.shape[-1]
if 'gru' in RNN_TYPE:
    RNN_UNITS = model.get_layer('last_gru').output.shape[-1]

model.summary()

model_filename = 'model_by_word_seq{}_emb{}_{}{}'.format(SEQ_LENGTH, EMBEDDING_DIM, RNN_TYPE, RNN_UNITS)

print("\nMODEL: {}\n".format(model_filename))

os.makedirs(os.path.join(logs_dir, model_filename), exist_ok = True) 

output_file = os.path.join(logs_dir, model_filename, "output.txt")
raw_output_file = os.path.join(logs_dir, model_filename, "raw_output.txt")


divine_comedy = divine_comedy.split()

# index_eoc = divine_comedy.index(special_tokens['END_OF_CANTO']) + 1
indexes = [i for i, x in enumerate(divine_comedy) if x == special_tokens['END_OF_CANTO'] and i > SEQ_LENGTH]
index_eoc = np.random.choice(indexes) + 1
start_idx = max(0, index_eoc - SEQ_LENGTH)
start_string = ' '.join(divine_comedy[start_idx:index_eoc])

#print(start_string)

generated_text = generate_text(model, special_tokens, vocab_size, word2idx, idx2word, SEQ_LENGTH, start_string, temperature=1.0)

#print(prettify_text(generated_text, special_tokens))

with open(output_file,"w") as f:
    f.write(prettify_text(generated_text, special_tokens))

with open(raw_output_file,"w") as f:
    f.write(generated_text)