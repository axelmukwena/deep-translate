# Author: Axel Mukwena
# Opened Datetime: 13 January 2022, 13h00
# Few breaks and other stuff in between
# Completed Datetime: 14 January 2022, 05h30

# ------------------------------------------------------------------------

import spacy
import re
import warnings
import number_words

# ------------------ IGNORE WARNINGS ------------------
# UserWarning: User provided device_type of 'cuda', but CUDA is not available. Disabling
#   warnings.warn('User provided device_type of \'cuda\', but CUDA is not available. Disabling')
# Pytorch related...
warnings.filterwarnings("ignore", category=UserWarning)


# ------------------ OUTPUTS ------------------
# print out, yey! 😆
def outputs(formatted):
    print("Output:")
    for item in formatted:
        [print(i) for i in item]
        print()


# ------------------ POST-PROCESSING ------------------
# now we just organize and format content for output
# We also need to maintain original test format as input
# as per requirements, with help of history
# Also, skip values manually parsed but not validated
# by pre-trained model
def postprocess(extracted_text, history, numbers):
    formatted = []
    count = 0
    for number in numbers:
        for extracted in extracted_text:
            if number[0] in extracted:
                count += 1
                text = number[1]
                for phrase in history:
                    if phrase[1] in text:
                        text = text.replace(phrase[1], phrase[0])
                formatted.append([f'#{count}:', text, number[0]])
    return formatted


# ------------------ PRE-TRAINED MODEL VALIDATION ------------------
# We already have the answers from previous function,
# We just need more validation that the extracted data belongs to the
# financial entity

# Load English tokenizer, tagger, parser and NER
# Included in requirements, `python -m spacy download en_core_web_trf`, 460.2 MB
# tfr => transformer, spaCy also have other
# CPU based models which I didn't find that robust and
# produce terrible results/biases
# References, https://spacy.io/models/en
def extraction(text):
    nlp = spacy.load("en_core_web_trf")
    doc = nlp(text)  # Process text
    
    # Analyze text syntax
    extracted_text = [entity.text for entity in doc.ents if entity.label_ == 'MONEY']
    return extracted_text


# ------------------ INPUT MANUAL SOLUTION BACK INTO TEXT ------------------
# replace the original text with digits => RMB 2,000,000
# most models are biased towards numeric data for finance, hence
# will aid in validation
def convert_words_to_numbers(text, numbers):
    for item in numbers:
        number, number_word = item
        text = text.replace(number_word, number)
    return text


# ------------------ TEXT PREPROCESSOR ------------------
# Store the original word/phrase and create new phrase version with
# replaced dashes "-" by spaces. For example, "online-based"
# and "online based" have completely different binary representations, hence we
# only need one representation
# Also, add space between alphanumeric and non-alphanumeric characters,
# and remove any double spaces
def preprocess(text):
    words = text.split()
    clean_text = text.replace("-", ' ')
    clean_text = re.sub(r'([\W])', r' \1 ', clean_text)
    clean_text = re.sub(r'\s{2,}', ' ', clean_text)
    
    history = [
        [phrase, phrase.replace("-", " ")] for phrase in words if '-' in phrase
    ]
    
    return clean_text, history


# ------------------ USER INPUT ------------------
# Function to get user input
def get_input():
    print("\nInput:")
    text = input()
    
    # Ensure user entered something using loop
    while not text:
        print("\nPlease input text:")
        text = input()
    
    print()  # empty line for readability
    return text


# ------------------ MAIN ------------------
# driver function
def main():
    text = get_input()  # Handles user input
    clean_text, history = preprocess(text)  # preprocessing
    
    # converting the number word forms to numeric forms
    numbers = number_words.to_numeric(clean_text)
    
    # insert the digits into the positions of the word forms
    numbers_text = convert_words_to_numbers(clean_text, numbers)
    
    # With aid of pre-trained model, verify that data extracted is monetary related
    extracted_text = extraction(numbers_text)
    
    # Format results for specified output
    formatted = postprocess(extracted_text, history, numbers)
    outputs(formatted)  # output


# ------------------ INIT ------------------
# Initialise the script
if __name__ == '__main__':
    main()
