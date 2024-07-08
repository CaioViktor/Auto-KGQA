from nltk.tokenize import sent_tokenize, word_tokenize 
from configs import MAX_SCORE_PARSER_TRIPLES_FAISS,MIN_SCORE_PARSER_TRIPLES_WOOSH
from functools import reduce

def chooseHit(hits,delta_score,delta_count):
    # print("test hits:")
    # print(hits)
    selected = None
    selected_rank = -1
    # print(f"delta_score:{delta_score}, delta_count:{delta_count}")
    for hit in hits:
        score = hit['score']
        count = hit['count']
        rank = (((score/delta_score) * 2 ) + (count/delta_count))/3 if delta_count > 0 else (score/delta_score)
        hit['rank'] = rank
        # print(f"{hit}\t {(score/delta_score)} + {(count/delta_count)}")
        # print(f"{url}:{count}")
        if selected_rank < rank:
            # print(f"trocou {selected}->{hit}")
            selected_rank = rank
            selected = hit
    # print("Selected: "+str(selected))
    if selected['score'] < MIN_SCORE_PARSER_TRIPLES_WOOSH:
        return None
    return selected

def parseText(text,index,normalizer,endpoint):
    #Search relevant elements in the whole text.
    # print("parseText: "+text)
    results = []
    terms_already_seen = set()
    if index.type == "SPOTLIGHT":
        results = index.search(text)
    else:
        if index.type == "WHOOSH":
            # print("normalizou")
            text = normalizer.normalizeSentece(text)
        matchs = []
        sentences = sent_tokenize(text)
        for sentence in sentences:
            matchs+=  parser_sentence(sentence,index,endpoint)
        for match in matchs:
            if not match['content']["?term"] in terms_already_seen:
                results.append(match)
                terms_already_seen.add(match['content']["?term"])
    return results

def tokenize_sentence(sentence):
    tokens = word_tokenize(sentence)
    return tokens

def select_hit_woosh(resultSearch,endpoint):
    #Term is present in index
    min_count =  min_score = 0
    max_count = max_score = 0
    for hit in resultSearch:
        url = hit["content"]["?term"]
        count = endpoint.countRankResource(url)
        hit['count'] = count
        if max_count < count:
            max_count = count
        if max_score < hit['score']:
            max_score = hit['score']
    delta_score = max_score - min_score
    delta_count = max_count - min_count

    selected_hit = chooseHit(resultSearch,delta_score,delta_count)
    return selected_hit

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
            # print("resultSearch " + term_search)
            # print(resultSearch)
            if resultSearch != None and len(resultSearch) > 0:
                if index.type == "WHOOSH":
                    selected_hit = select_hit_woosh(resultSearch,endpoint)
                elif index.type == "FAISS":
                    selected_hit = resultSearch[0]
                    if selected_hit['score'] > MAX_SCORE_PARSER_TRIPLES_FAISS:
                        selected_hit = None
                if selected_hit != None and not selected_hit in matchs:
                    # print(f"Escolheu: {selected_hit}")
                    matchs.append(selected_hit)
            window_start+=1
            window_end = window_start + window_size
        window_size-=1
    return matchs

