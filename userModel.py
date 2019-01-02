import sys
import os
import re
import nltk
import pickle
import collections

class User:
    name = ""
    pickle_file_name = ""
    user_preferences = {}

    def __init__(self, name):
        self.name = name.lower()

        self.pickle_file_name = self.name + '.pkl'

        try:
            file = open(self.pickle_file_name, 'rb')
        except IOError:
            with open(self.pickle_file_name, 'wb') as file:
                pickle.dump(self.user_preferences, file)
                file.close()
            file = open(self.pickle_file_name, 'rb')

        self.user_preferences = pickle.load(file)
        file.close()

    # Function for getting likes and dislikes from pickle file
    def get_preferences(self):
        return self.user_preferences

    # Function for storing/updating Likes and dislikes for pickle file.
    def set_preference(self, key, value):
        if key not in self.user_preferences:
            self.user_preferences[key] = value
        elif type(self.user_preferences[key]) == list:
            self.user_preferences[key].append(value)
        else:
            self.user_preferences[key] = [self.user_preferences[key], value]

        output = open(self.pickle_file_name, 'wb')
        pickle.dump(self.user_preferences, output)
        output.close()
