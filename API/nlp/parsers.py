from nltk.tokenize import sent_tokenize, word_tokenize 
from functools import reduce

def chooseHit(hits,delta_score,delta_count):
    # print("test hits:")
    selected = None
    selected_rank = -1
    # print(f"delta_score:{delta_score}, delta_count:{delta_count}")
    for hit in hits:
        score = hit['score']
        count = hit['count']
        rank = ((score/delta_score) + (count/delta_count))/2
        hit['rank'] = rank
        # print(f"{hit}\t {(score/delta_score)} + {(count/delta_count)}")
        # print(f"{url}:{count}")
        if selected_rank < rank:
            selected_rank = rank
            selected = hit
    # print(selected)
    return selected

def parseText(text,index,normalizer,endpoint):
    #Search relevant elements in the whole text.
    # print("parseText: "+text)
    text = normalizer.normalizeSentece(text)
    matchs = []
    sentences = sent_tokenize(text)
    for sentence in sentences:
        matchs+=  parser_sentence(sentence,index,endpoint)
    results = []
    for match in matchs:
        if not match in results:
            results.append(match)
    return results

def tokenize_sentence(sentence):
    tokens = word_tokenize(sentence)
    return tokens

def parser_sentence(sentence,index,endpoint):
    #Search named entities in the sentence.
    # print("parser_sentence: "+sentence)
    sentence_splitted = tokenize_sentence(sentence)
    window_size = len(sentence_splitted)
    matchs = []
    while window_size > 0 and window_size <= len(sentence_splitted):
        #Uses a sliding window to match segments from sentence to index. Window's size begin as full sentence's lenght and going decreasing by one until 0 or all sentence's fragments already have match.
        window_start = 0
        window_end = window_start + window_size
        while window_end <= len(sentence_splitted):
            term_search = reduce(lambda x,y:"{} {}".format(x,y),sentence_splitted[window_start:window_end])
            resultSearch = index.search(term_search)
            if resultSearch != None and len(resultSearch) > 0:
                #Term is present in index
                min_count =  min_score = 0
                max_count = max_score = 0
                for hit in resultSearch:
                    url = hit["content"]["?term"]
                    count = endpoint.countRankResource(url)
                    hit['count'] = count
                    # if min_count > count:
                        # min_count = count
                    if max_count < count:
                        max_count = count
                    # if min_score > hit['score']:
                        # min_score = hit['score']
                    if max_score < hit['score']:
                        max_score = hit['score']
                delta_score = max_score - min_score
                delta_count = max_count - min_count
                selected_hit = chooseHit(resultSearch,delta_score,delta_count)
                if not selected_hit in matchs:
                    matchs.append(selected_hit)
            window_start+=1
            window_end = window_start + window_size
        window_size-=1
    return matchs

