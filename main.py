# Author: Axel Mukwena
# Start Datetime: 13 January 2022, 13h00
# Few breaks and other stuff in between
# Completed Datetime: 14 January 2022, 05h05

# ------------------------------------------------------------------------

import re
import spacy
import warnings
import constants as co

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


# ------------------ MANUAL SOLUTION HELPER ------------------
# Use the building blocks to evaluate the number words
def text_to_integer_helper(number, number_blocks):
    current_value, total_value = 0, 0
    for word in number:
        scale, increment = number_blocks[word.lower()]
        current_value = current_value * scale + increment
        if scale > 100:
            total_value += current_value
            current_value = 0
    whole = total_value + current_value
    return whole


# ------------------ MANUAL SOLUTION ------------------
# Example,
# One HundRED thousand => 100,000
# This method disregard context and the draft steps to the solutions
# of the problem. This function picks up any text that can be parsed into
# a numeric form
# Please checkout /constants.py
def number_words_to_integer(text):
    
    # This will store keys and associated values.
    # Example { "thousand": 1000 }, these are used as building blocks
    # to parse alpha into numeric
    number_blocks = {}
    
    if not number_blocks:
        # "and" and "cent(s)" represent joints or cents, i.e. 500.cents
        number_blocks["and"] = (1, 0)
        number_blocks["cent"] = (1, 0)
        number_blocks["cents"] = (1, 0)
        
        # Initializing building blocks and values
        for index, word in enumerate(co.units):
            number_blocks[word] = (1, index)
        
        for index, word in enumerate(co.tens):
            number_blocks[word] = (1, index * 10)
        
        for index, word in enumerate(co.scales):
            number_blocks[word] = (10 ** (index * 3 or 2), 0)
    
    words = text.split()
    number_words, numerals = [], []
    
    # We'll be forming groups of words based on positions
    # if an integer non-parsable word (stop word) is met, we save the previous
    # parsable words as one number
    for index, word in enumerate(words):
        word = word.lower()  # lowering word case just to temp. process
        
        # stop word, time to save previous recordings
        # strip any "and"s
        if word not in number_blocks:
            while len(numerals) > 0:
                if numerals[0].lower() == "and":
                    numerals.pop(0)
                    continue
                number_words.append(numerals)
                numerals = []
                break
            continue
        # keep recording until stop word
        numerals.append(words[index])
    
    # now we have recordings, find if they have any "cent(s)"
    numbers = []
    for number in number_words:
        
        # initialize, if cents, then remove the last "cent" strings
        # from the full number so we parse cents and whole amounts separately
        limit = len(number)
        cents_value = ""
        separator = "."
        temp = [x.lower() for x in number]
        # temp = ["one", "hundred", "and", "fifty", "cents"]
        if "cent" in temp or "cents" in temp:
            # ["one hundred", "fifty cents"]
            cents = " ".join(number).lower().split("and")
            if len(cents) == 1:
                separator = ""

            # strip and remove `cents` => "fifty"
            cents = cents[len(cents) - 1].strip()
            cents = re.sub(r'(\s)cent\w+', r'\1', cents)
            cents = cents.split()
            
            # update limit, subtract 1, len(["fifty"])
            limit -= len(cents) + 1
            
            # Parse number words for cents to digits
            cents_value = text_to_integer_helper(cents, number_blocks)
            
            # keep cents to two digits, standards
            if cents_value > 99:
                cents_value = round(cents_value / 10) * 10
            cents_value = f'{separator}{cents_value:02}'[:3]
        
        # main parse number words for whole number
        temp_number = number[:limit]
        whole = text_to_integer_helper(temp_number, number_blocks)
        
        # if we only have cents
        if whole == 0:
            whole = f'{cents_value}'
        else:
            whole = f'{whole:,}{cents_value}'
        numbers.append([whole, " ".join(number)])
    
    return numbers


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
    
    # converting the number word forms to integers
    numbers = number_words_to_integer(clean_text)
    
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
