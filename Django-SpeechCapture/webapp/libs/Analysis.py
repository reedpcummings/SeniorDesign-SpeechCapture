import sys, json, boto3, awscli, re
from nltk import word_tokenize, sent_tokenize, pos_tag
import os
from nltk.stem import SnowballStemmer
snowball_stemmer = SnowballStemmer("english")
stop_words = open(os.path.join(os.path.curdir, 'webapp', 'stopwords.txt')).read().split("\n")

stepOnePath = "webapp/libs/step1.json"
stepTwoPath = "webapp/libs/step2.json"
stepThreePath = "webapp/libs/step3.json"

key_file = open(os.path.join(os.path.curdir, 'webapp', 'keys.txt'), 'r')
    
keys = key_file.read()
key_file.close()
keys_json = json.loads(keys)

comprehend = boto3.client('comprehend',
                            aws_access_key_id=keys_json['aws_access_key_id'],
                            aws_secret_access_key=keys_json['aws_secret_access_key'],
                            region_name='us-west-2'
                            )

s3_client = boto3.client('s3',
                             aws_access_key_id=keys_json['aws_access_key_id'],
                             aws_secret_access_key=keys_json['aws_secret_access_key'],
                             region_name='us-west-2'
                             )

def GenerateUseCase(content):
    questionDict, answerDict = ExtractAllQuestions(content)

    # Default values for use cases
    name = "Generated Use Case"
    id = "UC - 1"
    trigger = "No Triggers found."
    actors = "No Actors found."
    preconditions = "No Preconditions found."
    postconditions = "No Post-conditions found."
    normalFlow = "No Normal Flow found."
    altFlow = "No Alternative Flow found."

    # Index placements in the content
    nameIndex = -1
    idIndex = -1
    actorIndex = -1
    triggerIndex = -1
    precondtionIndex = -1
    postconditionIndex = -1
    normalFlowIndex = -1
    alternativeFlowIndex = -1

    total_dict = {}
    dict_num = 0

    for key, value in questionDict.items():
        for sent in value:
            wpFound = False
            postFound = False
            normalFlowFound = False
            alternativeFlowFound = False
            tokens = word_tokenize(sent)
            tokens = [word.lower() for word in tokens]
            tagged = pos_tag(tokens)
            for items in tagged:
                if items[1] == 'WP':
                    wpFound = True
                    continue
                if snowball_stemmer.stem(items[0]) == snowball_stemmer.stem("actors"):
                    normalFlowFound = True
                    continue
                if snowball_stemmer.stem(items[0]) == snowball_stemmer.stem("actors"):
                    alternativeFlowFound = True
                    continue
                if wpFound and snowball_stemmer.stem(items[0]) == snowball_stemmer.stem("actors"):
                    actorIndex = key
                if wpFound and snowball_stemmer.stem(items[0]) == snowball_stemmer.stem("name"):
                    nameIndex = key
                if wpFound and snowball_stemmer.stem(items[0]) == snowball_stemmer.stem("triggers"):
                    triggerIndex = key
                if wpFound and snowball_stemmer.stem(items[0]) == snowball_stemmer.stem("id"):
                    if idIndex == -1:
                        idIndex = key
                    else:
                        usecase_dict = {"Name": name,
                                        "ID": id,
                                        "Trigger": trigger,
                                        "Actors": actors,
                                        "Preconditions": preconditions,
                                        "Postconditions": postconditions,
                                        "NormalFlow": normalFlow,
                                        "AlternativeFlow": altFlow}
                        total_dict[dict_num] = usecase_dict
                        dict_num += 1
                if wpFound and snowball_stemmer.stem(items[0]) == snowball_stemmer.stem("precondition"):
                    precondtionIndex = key
                if wpFound and snowball_stemmer.stem(items[0]) == snowball_stemmer.stem("post"):
                    postFound = True
                    continue
                if wpFound and postFound and snowball_stemmer.stem(items[0]) == snowball_stemmer.stem("condition"):
                    postconditionIndex = key
                if wpFound and snowball_stemmer.stem(items[0]) == snowball_stemmer.stem("flow"):
                    if normalFlowFound:
                        normalFlowIndex = key
                    elif alternativeFlowFound:
                        alternativeFlowIndex = key
                if wpFound and snowball_stemmer.stem(items[0]) == snowball_stemmer.stem("precondition"):
                    precondtionIndex = key
                alternativeFlowFound = False
                normalFlowFound = False

        if nameIndex != -1:
            name = ' '.join(answerDict[nameIndex])
        if idIndex != -1:
            id = ' '.join(answerDict[idIndex])
        if actorIndex != -1:
            actors = ' '.join(answerDict[actorIndex])
        if precondtionIndex != -1:
            preconditions = ' '.join(answerDict[precondtionIndex])
        if postconditionIndex != -1:
            postconditions = ' '.join(answerDict[postconditionIndex])
        if normalFlowIndex != -1:
            normalFlow = ' '.join(answerDict[normalFlowIndex])
        if alternativeFlowIndex != -1:
            altFlow = ' '.join(answerDict[alternativeFlowIndex])
        if precondtionIndex != -1:
            preconditions = ' '.join(answerDict[precondtionIndex])
        if alternativeFlowIndex != -1:
            altFlow = ' '.join(answerDict[alternativeFlowIndex])
        # if triggerIndex != -1:
        #     triggerIndex = ' '.join(answerDict[triggerIndex])
    total_dict[dict_num] = usecase_dict
    return total_dict


def GetAllAttributesV2(content, fileName):
    questionDict, answerDict = ExtractAllQuestions(content)
    useCaseDict = GenerateUseCase(content)
    overallSummary, overallKeywords = GenerateSummary(content, 5, 5)
    print(content)
    totalQuestionDict = {}
    index = 0
    for key, value in questionDict.items():
        joinedList = questionDict[key] + answerDict[key]
        joinedString = ' '.join(joinedList)
        entities = ExtractEntities(joinedString, 5)
        sentiment = ExtractSentiments(joinedList)
        qaDict = {"Index": index,
                  "Question": ' '.join(questionDict[key]),
                  "Answer": ' '.join(answerDict[key]),
                  "Summary": None,
                  "Entities": entities,
                  "Keywords": None,
                  "Sentiment": sentiment}
        totalQuestionDict[key] = qaDict
        index += 1
    totalDict = {"OverallSummary": overallSummary,
                 "Questions": totalQuestionDict,
                 "UseCases": useCaseDict}

    fileName = fileName.replace(".txt", "Analysis.json")
    with open(fileName, 'w') as outfile:
        json.dump(totalDict, outfile)

    s3_client.upload_file(Filename=os.path.join(os.getcwd(), fileName), Bucket='test-speechcapture',
                          Key=fileName, ExtraArgs={'ACL': 'public-read'})


# Given an entity, perform ExtractSentences and then find the average sentiment of
# all of the sentences involved. Returns a dict with the keys of positive, neutral,
# negative and mixed and the values of their corresponding weight in the sentences ranging
# from 0.0 to 1.0
def ExtractSentiments(content, entity=None):
    if entity is not None:
        content = ExtractSentences(entity, content)
    sentiment = {"positive": 0.0, "negative": 0.0, "mixed": 0.0, "neutral": 0.0}
    content = ' '.join(content)
    if content.__len__() > 4500:
        content = __SplitString(content, 4500)
    else:
        content = [content]
    for s in content:
        sentFile = comprehend.detect_sentiment(Text=s, LanguageCode='en')
        sentiment["positive"] += round(sentFile["SentimentScore"]["Positive"], 4)
        sentiment["negative"] += round(sentFile["SentimentScore"]["Negative"], 4)
        sentiment["mixed"] += round(sentFile["SentimentScore"]["Mixed"], 4)
        sentiment["neutral"] += round(sentFile["SentimentScore"]["Neutral"], 4)
    return sentiment

# Extracts all questions and answers in the document, return 2 dicts
# one for questions, oen for answers
def ExtractAllQuestions(content):
    questionDict = {}
    answerDict = {}
    sentToken = sent_tokenize(content)
    index = 0
    questionFound = False
    answerFound = False
    for vals in sentToken:
        if re.match(r'(^|(?<=[.?!]))\s*[A-Za-z,;:\'\"\s]+\?', vals):
            index += 1
            questionDict[index] = [""]
            answerDict[index] = [""]
            questionDict[index].append(vals)
            questionFound = True
            continue
        if questionFound:
            answerDict[index].append(vals)
    return questionDict, answerDict


def DelineateSentences(content):
    content = sent_tokenize(content)
    sentList = []
    for sent in content:
        if re.match(r'(^|(?<=[.?!]))\s*[A-Za-z,;:\'\"\s]+\?', sent):
            sentList.append(sent)
            sentList.append('\n')
        else:
            sentList.append(sent)
    return sentList


def RemoveQuestions(content):
    for vals in content:
        if re.match(r'(^|(?<=[.?!]))\s*[A-Za-z,;:\'\"\s]+\?', vals):
            content.remove(vals)
    return content
# Get questions relevant to the entity provided in the argument. Must provide the dictionaries
# returned from ExtractAllQuestions filters through all the questions and answers to see which
# contain references to the provided entity
def ExtractRelevantQuestions(questionDict, answerDict, entity):
    questAndAnsw = ""
    for key, value in questionDict.items():
        for sents in value:
            if entity in sents:
                questAndAnsw += (' '.join(value) + "\n" + ' '.join(answerDict[key]) + "\n\n")
    return questAndAnsw

# Given an entity and a document in which the entity resides, extract
# all sentences pertaining to that entity. Returns a list of sentences.
def ExtractSentences(entity, content):
    entitySentences = []
    sentToken = sent_tokenize(content)
    for sent in sentToken:
        if entity in sent:
            entitySentences.append(sent)
    return entitySentences

# Extract a given number of entities from a document, the returned entities are
# ordered by how common they were in the document. Given 10 for numEntities, returns
# top 10 entities in document.
def ExtractEntities(content, numEntities):
    js = __DetectEntities(content)

    entities = {}
    for element in js:
        for key, value in element.items():
            for item in value:
                if item == "RequestId" or item == "HTTPStatusCode" or item == "HTTPHeaders" or item == "RetryAttempts":
                    continue
                if item["Type"] == "QUANTITY" or item["Type"] == "DATE":
                    continue
                if item["Text"] in entities:
                    entities[item["Text"]] += 1
                else:
                    entities[item["Text"]] = 1
    index = 0
    sortedDict = {}
    for k in sorted(entities, key=lambda k: entities[k], reverse=True):
        if index > numEntities:
            break
        sortedDict[k] = entities[k]
        index += 1
    return sortedDict

# Create a comprehend object and run the Detect Entities function
def __DetectEntities(content):
    # Create the comprehend object

    #comprehend = boto3.client(service_name='comprehend', region_name='us-west-2')

    # Split the string
    if content.__len__() > 4500:
        content = __SplitString(content, 4500)
    else:
        content = [content]

    json = []
    for s in content:
        json.append(comprehend.detect_entities(Text=s, LanguageCode='en'))
    return json

# Splits up input strings due to comprehend's limit on input to 5000 characters
def __SplitString(s, count):
    return [''.join(x) for x in zip(*[list(s[z::count]) for z in range(count)])]


def GenerateSummary(content, num_sents, num_keywords):
    sent_tokens_raw = sent_tokenize(content)
    sent_tokens_cleaned = []
    for tokens in sent_tokens_raw:
        clean_token = re.sub(r'[^a-zA-Z_ ]', "", tokens)
        clean_token = clean_token.lower()
        word_tokens = word_tokenize(clean_token)
        for word in word_tokens:
            if word not in stop_words:
                sent_tokens_cleaned.append(word)
    frequency_dict = {}
    for words in sent_tokens_cleaned:
        if words in frequency_dict:
            frequency_dict[words] += 1
        else:
            frequency_dict[words] = 1
    sorted_values = sorted(frequency_dict.items(), key=lambda kv: kv[1], reverse=True)
    max_value = sorted_values[0][1]
    weighted_frequency_dict = {}
    for key, value in frequency_dict.items():
        weighted_frequency_dict[key] = value / max_value
    weighted_sentence_dict = {}
    for sent in sent_tokens_raw:
        words = word_tokenize(sent)
        weighted_val = 0
        for word in words:
            if  word in sent_tokens_cleaned:
                weighted_val += weighted_frequency_dict[word]
        weighted_sentence_dict[sent] = weighted_val
    sorted_sents = sorted(weighted_sentence_dict, key=(lambda key: weighted_sentence_dict[key]), reverse=True)
    summary_list = []
    index = 0
    while index < num_sents:
        summary_list.append(sorted_sents[index])
        index += 1

    keyword_list = []
    index = 0
    while index < num_keywords:
        keyword_list.append(sorted_values[index][0])
        index += 1

    return ' '.join(summary_list), ' '.join(keyword_list)

# Public method for extracting the summary of a given text
# INPUT: A bunch of text
# OUTPU: A dictionary containing the summary and keywords
# def GenerateSummary(docInput):
#     docInput = RemoveQuestions(docInput)
#     __StepOne(docInput)
#     __StepTwo()
#     __StepThree()
#     return __StepFour()
#
# # Steps for generating the summary of provided text
# def __StepOne(docInput):
#     docInput = ' '.join(docInput)
#     jsonData = {"id": 0, "text": docInput}
#     with open('webapp/libs/summaryData.json', 'w') as outFile:
#         json.dump(jsonData, outFile)
#     with open(stepOnePath, 'w') as f:
#         for graf in pytextrank.parse_doc(pytextrank.json_iter("webapp/libs/summaryData.json")):
#             f.write("%s\n" % pytextrank.pretty_print(graf._asdict()))
#
# def __StepTwo():
#     graph, ranks = pytextrank.text_rank(stepOnePath)
#     pytextrank.render_ranks(graph, ranks)
#
#     with open(stepTwoPath, 'w') as f:
#         for r1 in pytextrank.normalize_key_phrases(stepOnePath, ranks):
#             f.write("%s\n" % pytextrank.pretty_print(r1._asdict()))
#
# def __StepThree():
#     kernel = pytextrank.rank_kernel(stepTwoPath)
#
#     with open(stepThreePath, 'w') as f:
#         for s in pytextrank.top_sentences(kernel, stepOnePath):
#             f.write(pytextrank.pretty_print(s._asdict()))
#             f.write("\n")
#
# def __StepFour():
#     phrases = ", ".join(set([p for p in pytextrank.limit_keyphrases(stepTwoPath, phrase_limit=12)]))
#     sent_iter = sorted(pytextrank.limit_sentences(stepThreePath, word_limit=150), key=lambda x: x[1])
#     s = []
#
#     for sent_text, idx in sent_iter:
#         s.append(pytextrank.make_sentence(sent_text))
#
#     graf_text = " ".join(s)
#     summaryDict = {"summary": graf_text, "keywords": phrases}
#     return graf_text, phrases
