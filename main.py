# Author: Axel Mukwena
# Start Datetime: 13 January 2022, 13h00

import re
import spacy
import warnings
import constants as co

# UserWarning: User provided device_type of 'cuda', but CUDA is not available. Disabling
#   warnings.warn('User provided device_type of \'cuda\', but CUDA is not available. Disabling')
# Pytorch related...
warnings.filterwarnings("ignore", category=UserWarning)


# Function to get user input
def get_input():
    print("\nInput:")
    text = input()
    
    # Ensure user entered something
    while not text:
        print("\nPlease input text:")
        text = input()
    
    print()  # empty line for readability
    return text


def outputs(formatted):
    print("Output:")
    for item in formatted:
        [print(i) for i in item]
        print()
        

# Find all dashes "-" in text, save the original word/phrase
# and replace the dash with space. For example, "online-based"
# and "online based" have completely different binary representations
# Also, add space between punctuations and words, and remove any double spaces
def preprocess(text):
    words = text.split()
    clean_text = text.replace("-", ' ')
    clean_text = re.sub(r'([\W])', r' \1 ', clean_text)
    clean_text = re.sub(r'\s{2,}', ' ', clean_text)
    
    history = [
        [phrase, phrase.replace("-", " ")] for phrase in words if '-' in phrase
    ]
    
    return clean_text, history


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


def text_to_integer_helper(number, join_words):
    current_value, total_value = 0, 0
    for word in number:
        scale, increment = join_words[word.lower()]
        current_value = current_value * scale + increment
        if scale > 100:
            total_value += current_value
            current_value = 0
    whole = total_value + current_value
    return whole
    

def text_to_integer(text):
    join_words = {}
    
    if not join_words:
        join_words["and"] = (1, 0)
        join_words["cent"] = (1, 0)
        join_words["cents"] = (1, 0)
        for index, word in enumerate(co.units):
            join_words[word] = (1, index)
        
        for index, word in enumerate(co.tens):
            join_words[word] = (1, index * 10)
        
        for index, word in enumerate(co.scales):
            join_words[word] = (10 ** (index * 3 or 2), 0)
    
    words = text.split()
    
    number_words, numerals = [], []
    for index, word in enumerate(words):
        word = word.lower()
        if word not in join_words:
            while len(numerals) > 0:
                if numerals[0].lower() == "and":
                    numerals.pop(0)
                    continue
                number_words.append(numerals)
                numerals = []
                break
            continue
        numerals.append(words[index])
    
    numbers = []
    for number in number_words:
        
        limit = len(number)
        cents_value = ""
        separator = "."
        temp = [x.lower() for x in number]
        if "cent" in temp or "cents" in temp:
            cents = " ".join(number).lower().split("and")
            if len(cents) == 1:
                separator = ""
            cents = cents[len(cents) - 1].strip()
            cents = re.sub(r'(\s)cent\w+', r'\1', cents)
            cents = cents.split()
            limit -= len(cents) + 1
            cents_value = text_to_integer_helper(cents, join_words)
            if cents_value > 99:
                cents_value = round(cents_value / 10) * 10
            cents_value = f'{separator}{cents_value:02}'[:3]

        temp_number = number[:limit]
        whole = text_to_integer_helper(temp_number, join_words)

        if whole == 0:
            whole = f'{cents_value}'
        else:
            whole = f'{whole:,}{cents_value}'
        numbers.append([whole, " ".join(number)])
    
    # [print(number) for number in numbers]
    return numbers


def convert_words_to_numbers(text, numbers):
    for item in numbers:
        number, number_word = item
        text = text.replace(number_word, number)
    return text


def extraction(text):
    # Load English tokenizer, tagger, parser and NER
    # In terminal, `python -m spacy download en_core_web_trf`
    # References, https://spacy.io/models/en
    nlp = spacy.load("en_core_web_trf")
    doc = nlp(text)  # Process text
    
    # Analyze text syntax
    extracted_text = [entity.text for entity in doc.ents if entity.label_ == 'MONEY']
    return extracted_text


# Main driver function
def main():
    text = get_input()
    clean_text, history = preprocess(text)
    numbers = text_to_integer(clean_text)
    numbers_text = convert_words_to_numbers(clean_text, numbers)
    extracted_text = extraction(numbers_text)
    formatted = postprocess(extracted_text, history, numbers)
    outputs(formatted)


# Initialise
if __name__ == '__main__':
    main()
