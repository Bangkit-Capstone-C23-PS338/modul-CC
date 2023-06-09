from transformers import TFBertForSequenceClassification
import tensorflow as tf
from transformers import BertTokenizer

# Load the model
model = TFBertForSequenceClassification.from_pretrained("model/nnmodel")
tokenizer = BertTokenizer.from_pretrained('indobenchmark/indobert-base-p1')

def predict_string(input):
    # Tokenize the input texts
    inputs = tokenizer(input, padding=True, truncation=True, return_tensors='tf')

    # Make the prediction
    outputs = model(inputs)

    # Get the predicted probabilities for each class
    probabilities = tf.nn.softmax(outputs.logits, axis=1).numpy()

    # Get the predicted labels
    predicted_labels = tf.argmax(probabilities, axis=1).numpy()
    
    return probabilities[0][1]

text_list = ["kamu goblok banget tolol", "you are so clever", "aku senang bertemu denganmu", "kemarin, saya menemukan botol kaca"]

for i in text_list:
    proba = predict_string(i)
    print(proba)