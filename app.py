# Wilson Ding & Keaton Khonsari
# NLP Semester Project
# CS 4301

import sys
import os
import urllib.request
import re
import requests
import nltk
import pickle
from random import randint
from userModel import User
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import sentiwordnet as swn

# constants
url = 'https://en.wikipedia.org/wiki/Keeping_Up_with_the_Kardashians'  # starting url
url_keywords = ['kardashian', 'kardashians', 'jenner', 'kanye'] # whitelisted url keywords

# blacklisted urls
blacklist_urls = ['google', 'wiki', 'youtube', 'huffingtonpost',
                    'tv', 'hulu', 'video', 'interviewmagazine',
                    'broadcastingcable', 'hollywoodreporter',
                    'washingtontimes', 'psychologytoday', 'vudu',
                    'amazon', 'download', 'dvd', 'web.archive', 'variety']

# functions
def urls(url):
    print("Selecting urls...")
    starter_url = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(starter_url).read()
    soup = BeautifulSoup(webpage, "html.parser")
    data = soup.text

    # Writes urls to a text file
    with open('urls.txt', 'w') as f:
        f.write('https://en.wikipedia.org/wiki/Keeping_Up_with_the_Kardashians' + '\n')
        for link in soup.find_all('a'):
            link_str = str(link.get('href'))
            if any(keyword in link_str.lower() for keyword in url_keywords):
                if link_str.startswith('/url?q='):
                    link_str = link_str[7:]
                if '&' in link_str:
                    i = link_str.find('&')
                    link_str = link_str[:i]
                if link_str.startswith('http') and not any(domain in link_str.lower() for domain in blacklist_urls):
                    f.write(link_str + '\n')
        f.close()

def text():
    print("Extracting text...")
    with open('urls.txt', 'r') as f:
        urls = f.readlines()
        f.close()

    # create text/ directory if not exist
    if not os.path.exists(append_path('texts')):
        os.makedirs(append_path('texts'))

    for url in urls:
        name = re.sub(r'[^\w\s]', '', url.lower())    # remove all punctuation from url for name
        with open(append_path('texts/{}.txt'.format(name.rstrip())), 'w+') as f:
            html = urllib.request.urlopen(url)
            soup = BeautifulSoup(html, "html.parser")
            data = soup.findAll(text=True)
            result = filter(visible, data)
            f.write(' '.join(list(result)))
            f.close()

def kb():
    print("Creating Knowledge Base...")
    # create sanitized_texts folder
    if not os.path.exists(append_path('sanitized_texts')):
        os.makedirs(append_path('sanitized_texts'))

    terms = dict()
    topTerms = []

    # iterate through all files to find relevant terms (tokens)
    for file in os.listdir(append_path('texts')):
        with open(append_path('texts/{}'.format(file)), 'r') as f:
            lines = f.read()
            f.close()

        # sanitize text
        sanitizedText = re.sub(r'[^\w\s]', '', lines.lower())    # remove all punctuation
        sanitizedText = re.sub(r'[\n\d\t]', ' ', sanitizedText)   # remove \n \d \t

        # get tokens
        tokens = word_tokenize(sanitizedText)

        # remove stop words and other words
        stop_words = set(stopwords.words('english'))    # get list of English stopwords
        other_words = ['reacttext', 'show', 'like', 'keeping', 'new', 'news', 'family', 'would', 'end', 'one', 'time', 'get', 'said', 'people', 'first', 'life', 'also', 'home', 'know', 'video', 'yes', 'reality', 'series', 'view']
        important_tokens = [t for t in tokens if not t in stop_words and not t in other_words and len(t) > 2]   # remove stopwords from tokens and words smaller than 2

        # count words and add to terms dict
        for word in important_tokens:
            if word in list(terms.keys()):
                terms[word] += 1  
            else:
                terms[word] = 1

    # top 15 terms
    print("Top 15 terms:")
    for k in sorted(terms, key=lambda k: terms[k], reverse=True)[:15]:
        print(k)
        # add to topTerms dict
        topTerms.append(k)

    # create knowledgebase based on top 40 terms

    kb = dict()

    # iterate through all files in texts/, remove \n \t and sentence tokenize 
    for file in os.listdir(append_path('texts')):
        with open(append_path('texts/{}'.format(file)), 'r') as f:
            lines = f.read()
            f.close()

        lines = re.sub(r'[\n\t]', ' ', lines)   # remove \t and \n
        lines = re.sub(' +', ' ', lines)    # replace multiple spaces with single space

        sents = sent_tokenize(lines)

        # write to sanitized_texts
        with open(append_path('sanitized_texts/{}'.format(file)), 'w+') as f:
            for sent in sents:
                f.write(sent + '\n')
                # add to kb if sent contains one of top 40 terms
                for term in topTerms:
                    if term in sent.lower():
                        if term in list(kb.keys()):
                            kb[term].append(sent)  
                        else:
                            kb.update({term: [sent]})
            f.close()

    # save kb to pickle file
    with open('chatbot_kb.pkl', 'wb') as f:
        pickle.dump(kb, f)
        f.close()

    # save terms to pickle file
    with open('chatbot_terms.pkl', 'wb') as f:
        pickle.dump(topTerms, f)
        f.close()

def chat():
    print("Running Chat Bot...")

    # load kb and topTerms
    try:
        kbfile = open('chatbot_kb.pkl', 'rb')
        termsfile = open('chatbot_terms.pkl', 'rb')

        kb = pickle.load(kbfile)
        terms = pickle.load(termsfile)

        kbfile.close()
        termsfile.close()
    except IOError:
        print('Error, could not find pickle files for kb and terms.')

    # introductory message
    print("\n\n\n")
    print("###### Welcome to the KUWTK Chat Bot! ######")

    # get name and create user
    name = input("Bot: Before we get started... what should I call you? ")
    user = User(name)
    print("Bot: Nice to meet you, " + name + "!")
    print("Bot: I am trained to talk about a variety of topics related to the Kardashians.")
    print("Bot: Feel free to ask me a question... (examples below)")
    print("\n")
    print("ex: Hello, how are you?")
    print("ex: Tell me about Kim.")
    print("ex: I hate Kylie.")
    print("ex: Do you like Bruce?")
    print("ex: How does the world feel about Kendall?")
    print("ex: !data (list all likes/dislikes associated to you)")
    print("\n")

    response = ""

    # Continual message loop
    while True:
        message = input(name + ": ")
        response = respondTo(user, message, kb, terms)
        print("Bot: " + response)

        if response == 'Goodbye!':
            sys.exit(0)

# rudimentary chatbot
def respondTo(user, message, kb, terms):
    response = ''

    # lists
    greetings = ['hello', 'hey', 'hi ', 'good morning', 'good afternoon', 'good evening']
    status = ['whats up', 'how are you', 'how are you doing']
    goodbye = ['bye', 'goodbye', 'exit', 'quit', 'end']
    feeling = ['feel about ', ' think about ', 'think of ', 'feel of ']
    likes = ['like ', 'love ', 'adore ', 'enjoy ']
    dislikes = ['dislike ', 'hate ', 'dont like ', 'dont enjoy ', 'dont love ']

    # checking for data! message type
    if message == '!data':
        return 'User data for ' + user.name + ': ' + str(user.get_preferences())

    # sanitize message
    sanitizedMessage = re.sub(r'[^\w\s]', '', message.lower())

    # checking for goodbye message type
    if sanitizedMessage in goodbye:
        return 'Goodbye!'

    # checking for greetings message type
    if any(substring in sanitizedMessage for substring in greetings):
        response += 'Hello! '

    # checking for status message type
    if any(substring in sanitizedMessage for substring in status):
        response += 'Everything seems to be running smoothly...'

    # if response exists, return it.
    if response != '':
        return response

    # if no return yet, try to parse for a response related to the terms

    # try to find term - exit if no term detected
    tokens = word_tokenize(sanitizedMessage)
    relevant_terms = [term for term in terms if term in tokens] # get terms that appear in tokens
    
    # if no term found...
    if len(relevant_terms) == 0:
        return 'I\'m not quite familiar with this topic... Try another?'

    # try doing sentiment analysis

    # checking for dislikes message type
    if any(substring in sanitizedMessage for substring in dislikes):
        if 'i ' in sanitizedMessage:
            for term in relevant_terms:
                user.set_preference('dislikes', term)
            return 'I\'ll remember that you dislike ' + str(*relevant_terms)
        elif 'do you' in sanitizedMessage:
            if randint(0,1) == 0:
                return 'Yes, I dislike ' + relevant_terms[0]
            else:
                return 'No, I actually kinda like ' + relevant_terms[0]
        else:
            return 'I think you dislike ' + str(*relevant_terms)

    # checking for likes message type
    if any(substring in sanitizedMessage for substring in likes):
        if 'i ' in sanitizedMessage:
            for term in relevant_terms:
                user.set_preference('likes', term)
            return 'I\'ll remember that you like ' + str(*relevant_terms)
        elif 'do you' in sanitizedMessage:
            if randint(0,1) == 0:
                return 'Yes, I like ' + relevant_terms[0]
            else:
                return 'No, I actually kinda dislike ' + relevant_terms[0]
        else:
            return 'I think you like ' + str(*relevant_terms)

    # check for polarity (feeling question)
    if any(substring in sanitizedMessage for substring in feeling):
        term = relevant_terms[0]
        return 'Overall, the feelings are ' + assess_polarity(term, kb) + ' for ' + term

    # last ditch effort... respond with a random sentence from the kb
    if response == '':
        return kb[relevant_terms[0]][randint(0,len(kb[relevant_terms[0]])-1)]

# assess polarity
def assess_polarity(term, kb):
    score = 0

    for sentence in kb:
        tokens = word_tokenize(sentence)

        total_neg_polarity = 0.0
        total_pos_polarity = 0.0

        for token in tokens:
            syn = list(swn.senti_synsets(token))
            if syn:
                syn = syn[0]
                total_neg_polarity += syn.neg_score()
                total_pos_polarity += syn.pos_score()
        pos_score = total_pos_polarity / len(tokens)
        neg_score = total_neg_polarity / len(tokens)

        if pos_score > neg_score:
            score += 1
        else:
            score -= 1

    if score >= 0:
        return 'positive'
    else:
        return 'negative'

# helper functions
def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True

def append_path(path):
    return os.path.join(os.getcwd(), path)

# error messages
def printArgMissingErrorMessage():
    print('KUWTK NLP Semester Project: Please run the program with an arg:')
    print(' - `urls` (URL Selection)   - Ex: python3 app.py urls')
    print(' - `text` (Text Extraction) - Ex: python3 app.py text')
    print(' - `kb` (Knowledge Base)    - Ex: python3 app.py kb')
    print(' - `chat` (Chat Bot)        - Ex: python3 app.py chat')
    print(' - `all (Run everything)    - Ex: python3 app.py all')
    sys.exit(1)

def printWrongOrderMessage(cmd):
    print('Error: please run the {} command before attempting to run the current command.'.format(cmd))

# main
def main():
    # error checking for sys arg containing command
    if len(sys.argv) != 2:
        printArgMissingErrorMessage()

    command = sys.argv[1]

    if command == 'urls':   # URL Selection
        urls(url)
    elif command == 'text': # Text Extraction
        if not os.path.isfile(append_path('urls.txt')): # checking that previous command has been run
            printWrongOrderMessage('urls')
        text()
    elif command == 'kb':   # Knowledge Base
        if not os.path.isdir(append_path('texts/')):    # checking that previous command have been run
            printWrongOrderMessage('text')
        kb()
    elif command == 'chat':   # Chatbot
        if not os.path.isfile(append_path('chatbot_kb.pkl')):   # checking that previous command have been run
            printWrongOrderMessage('kb')
        chat()
    elif command == 'all':  # Run Everything
        urls(url)
        text()
        kb()
        chat()
    else:
        printArgMissingErrorMessage()

if __name__== '__main__':
    main()
