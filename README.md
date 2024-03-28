# Information Retrieval Project

## Overview
This project is part of the Information Retrieval course at Amirkabir University of Technology (Tehran Polytechnic). It focuses on implementing various components of an information retrieval system, including tokenization, stemming, normalization, and other preprocessing steps.

## Components
### Tokenization
The `Tokenizer` class in the `Tokenization` module is responsible for tokenizing the input text. It includes methods for handling conjunctions, stopwords, and performing stemming using the `Hazm` library.

### Stemming
The `stemming` method in the `Stemming` module is used to determine the root of a word based on its type (noun or verb). It utilizes the `Hazm` library for stemming or lemmatization.

### Normalization
The `Normalizer` class is responsible for correcting the structure of words and characters, including converting numeric characters from English to Persian, correcting three dots, hyphens, Hamzeh, and half-spaces.

### Hamsansaz
This component handles the normalization of similar words and abbreviations. The `hamsansaz` method corrects words based on predefined lists of similar words and abbreviations.

### Sorting
The `sort` function is used to rank documents based on their similarity to a query. It supports sorting by relevance, TF-IDF, and time.

## Usage
The project includes various Python scripts and modules that can be used to preprocess and analyze text data for information retrieval purposes.

## Conclusion
This project demonstrates the implementation of key components in an information retrieval system, including preprocessing techniques like tokenization, stemming, and normalization, as well as ranking documents based on their relevance to a query.
