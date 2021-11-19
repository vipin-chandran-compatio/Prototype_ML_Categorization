from bs4 import BeautifulSoup
import re
import pandas as pd

def remove_tags(html):
    # parse html content
    soup = BeautifulSoup(html, "html.parser")

    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)


def clean_text(namearray):
    ser = pd.Series()
    i = 0
    # ps = PorterStemmer()
    ##cleanr = re.compile('<.*?>')
    for text in namearray:
        string = ""
        # words = word_tokenize(text)
        text = remove_tags(text)
        text = re.sub(r"[^A-Za-z]", " ", text)
        # ser.at[i] = remov_duplicates(text.lower())
        ser.at[i] = text.lower()

        # ser.at[i] = ps.stem(text.lower())
        # print("Before---",text)
        # ser.at[i] = do_lemm(ps.stem(text.lower()))
        # string = '-'.join(list_string)
        # for w in words:
        # print("After---",ps.stem(text.lower()))
        # string = " ".join(ps.stem(w))
        # print("After---",string)
        # do_lemm(sentence)
        i = i + 1

    return ser