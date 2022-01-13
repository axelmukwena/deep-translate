import re
import constants as co


# ------------------ MANUAL SOLUTION HELPER ------------------
# Use the building blocks to evaluate the number words
def text_to_numeric_helper(number, number_blocks):
    current_value, total_value = 0, 0
    for word in number:
        scale, increment = number_blocks[word.lower()]
        current_value = current_value * scale + increment
        if scale > 100:
            total_value += current_value
            current_value = 0
    whole = total_value + current_value
    return whole


# ------------------ MANUAL SOLUTION - NUMBERS WORDS TO NUMERIC ------------------
# Example,
# One HundRED thousand => 100,000
# This method disregard context and the draft steps to the solutions
# of the problem. This function picks up any text that can be parsed into
# a numeric form
# Please checkout /constants.py
def to_numeric(text):
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
    # if a non-parsable word (stop word) is met, we save the previous
    # parsable words as one number
    for index, word in enumerate(words):
        word = word.lower()
        
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
            cents_value = text_to_numeric_helper(cents, number_blocks)
            
            # keep cents to two digits, standards
            if cents_value > 99:
                cents_value = round(cents_value / 10) * 10
            cents_value = f'{separator}{cents_value:02}'[:3]
        
        # main parse number words for whole number
        temp_number = number[:limit]
        whole = text_to_numeric_helper(temp_number, number_blocks)
        
        # if we only have cents
        if whole == 0:
            whole = f'{cents_value}'
        else:
            whole = f'{whole:,}{cents_value}'
        numbers.append([whole, " ".join(number)])
    
    return numbers
