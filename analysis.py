import gensim as gensim
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from nltk import *

tknzr = RegexpTokenizer(r'\w+')

"""
Gensim is used to perform topic modeling on the data. 
"""

def topicModeling():
    with open('articles.json') as file:
        data = json.load(file)
    df = pd.DataFrame(data)
    preprocessedList = []
    for article in df['preprocessed']:
        preprocessedList.append(tknzr.tokenize(article))

    dictionary = gensim.corpora.Dictionary(preprocessedList)
    dictionary.filter_n_most_frequent(200)
    bow_corpus = [dictionary.doc2bow(doc) for doc in preprocessedList]
    models = []
    coherences = []
    perplexity = []
    nts = []
    for nt in range(10, 31):
        print("Number of topics: ", nt)
        lda_model = gensim.models.ldamodel.LdaModel(corpus = bow_corpus,
                                               num_topics=nt,
                                               id2word=dictionary,
                                               per_word_topics=True)
        models.append(lda_model)
        coherence_model_lda = gensim.models.CoherenceModel(model=lda_model, texts=preprocessedList,
                                                           dictionary=dictionary, coherence='c_v')
        coherence_lda = coherence_model_lda.get_coherence()
        print("Coherence: ", coherence_lda)
        coherences.append(coherence_lda)
        perplexity.append(lda_model.log_perplexity(bow_corpus))
        nts.append(nt)

    filePerplexity = "plotPerplexity.svg"
    plt.plot(nts, perplexity)
    plt.title("Perplexity")
    plt.xlabel("Number of topics")
    plt.ylabel("Perplexity")
    plt.xticks(np.arange(10, 31, 1))
    plt.savefig(filePerplexity)
    plt.close()

    # coherence
    fileCoherence = "plotCoherence.svg"
    plt.plot(nts, coherences)
    plt.title("Coherence")
    plt.xlabel("Number of topics")
    plt.ylabel("Coherence value")
    plt.xticks(np.arange(10, 31, 1))
    plt.savefig(fileCoherence)
    plt.close()
    return bow_corpus, dictionary


if __name__ == '__main__':
    bow_corpus, dictionary = topicModeling()

    """
    No of topics: 26
    To reach here we also filtered out the words which are very frequent as during our research we found out that these are mostly noises. 
    The optimal number of topics we choose that has the maximum coherence before it flattens and then we get a huge drop
    """

    no_of_topics = 26
    lda_model = gensim.models.ldamodel.LdaModel(corpus=bow_corpus,
                                                num_topics=no_of_topics,
                                                id2word=dictionary,
                                                per_word_topics=True)
    dataFrame_to_write = pd.DataFrame({1 : [], 2:[],3:[],4:[],5:[],6:[],7:[],8:[],9:[],10:[]
                                       ,11:[],12:[],13:[],14:[],15:[],16:[]})
    dict_to_write = {}
    list_to_write = lda_model.show_topics(num_topics=no_of_topics, num_words=20, log=False, formatted=False)
    for index in range(0, no_of_topics):
        current_list = list_to_write[index][1]
        words_list = []
        for pair in current_list:
            words_list.append(pair[0])
        dict_to_write[index] = words_list

    df_to_write = pd.DataFrame(dict_to_write)
    columns = [range(0, no_of_topics), range(1, no_of_topics+1)]
    df_to_write.columns = pd.MultiIndex.from_arrays(columns)

    df_to_write.to_csv(r'topic_model.csv', index=False)
    df_to_latex = df_to_write.to_latex()

    """
    Projecting articles into the topic model. 
    For each topic, the article where that topic is the most likely is found. 
    """

    df = pd.read_csv('topic_model.csv')
    tm = list(df.columns)
    jsonFile = open('articles.json', mode='r', encoding="UTF-8")
    jsonArticles = json.load(jsonFile)
    for topic in tm:
        countwords = 0
        articlename = ""
        date = ""
        listOfWords = list(df[topic])
        for article in jsonArticles:
            preprocessed = article['preprocessed'].split()
            currentCount = 0
            for word in preprocessed:
                if word in listOfWords:
                    currentCount += 1
            if currentCount > countwords:
                countwords = currentCount
                articlename = article['title']
                date = article['date']
        print("Topic Number : " + topic + " with header '" + listOfWords[0]+"'")
        print("Name of article : " + articlename)
        print("Date : " + date)
