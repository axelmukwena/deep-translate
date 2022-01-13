# Deep Translate Solution

### Programming solution for assessment at Deep Translate

##### Problem
 Using Python, List out (1) ‘special words’ found in the input text where the special words are amounts which you might typically see on cheques, e.g. “one hundred and fifty-one dollars and twenty-seven cents”, together with (2) the number corresponding to the special words.


## Technologies used

1. #### SpaCy
    - https://spacy.io/
    - Supports wide range of languages and entity types. Our focus will be the ***MONEY*** entity.
    - 


## Running the program

- Should work in any environment, but if experiencing any problems, setup as below.
- My native environment is **macOS Catalina 10.15.7, PyCharm 2021.1**
- Prerequisites: Python 3, pip

      $ cd folder/folder/deep-translate
      
- Install virtualenv
      
      # Mac OS
      $ sudo -H pip install virtualenv
      
      # Windows
      $ pip install virtualenv
  
- Create a virtual environment
  
      # Mac OS
      $ virtualenv -p python3 venv

      # Windows
      $ python3 -mvenv venv
      
- Activate the environment
  
      # Mac OS
      $ source venv/bin/activate
      
      # Windows
      $ venv\Scripts\activate

- Install the requirements.txt
  
      # Mac OS
      $ pip3 install -r requirements.txt
      
      # Windows
      $ python3 -m pip install -r requirements.txt
    
- Run the script...

      $ python3 main.py

- Follow the prompt terminal instructions

### Installing or updating packages
Just make sure env exists, otherwise create another one

- Go to folder

      $ cd folder/folder/deep-translate

- Activate env

      # Mac OS
      $ source venv/bin/activate

      # Windows
      $ venv\Scripts\activate
  
- Install or update package

      # specific command
      # MacOS
      $ pip install --upgrade package

- Update *requirements.txt*

      $ pip freeze > requirements.txt

### Deactivate env
- Deactivate env

      # Mac OS
      $ deactivate

      # Windows
      $ 