import os
import numpy as np
import tensorflow as tf
from dante_by_word.text_processing import prettify_text, special_tokens

def generate_text(model, special_tokens, vocab_size, word2idx, idx2word, seq_length, start_string, temperature=1.0):
    text = start_string
    generated_text = ''
    prediction = ''
    model.reset_states()
    i = 0
    while prediction != special_tokens['END_OF_CANTO'] \
            and generated_text.count(special_tokens['END_OF_VERSO']) < 151:
#            and generated_text.count(special_tokens['END_OF_TERZINA']) < 50 \
        
        sequence = [ word2idx[w] for w in text.split()[-seq_length:] ]
        sequence = tf.keras.preprocessing.sequence.pad_sequences([sequence], maxlen=seq_length)
        x = np.array(sequence, dtype='int64')

        prediction = model.predict(x, verbose=0)

        prediction = tf.squeeze(prediction, 0)[-1]
        
        prediction = prediction / temperature
        prediction = prediction.numpy()
        index = np.random.choice(len(prediction), size=1, p=prediction)[0]

#        index = np.argmax(prediction)

        prediction = idx2word[index]
        generated_text += " "+prediction
        text += " "+prediction

#        print(prediction, end=' ', flush=True)
        print(prettify_text(prediction, special_tokens), end=' ', flush=True)
        i+=1        
    print('\n')        
    return generated_text


