import pytextrank
import sys, json, boto3, awscli, re
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
stopWords = set(stopwords.words('english'))

stepOnePath = "webapp/libs/step1.json"
stepTwoPath = "webapp/libs/step2.json"
stepThreePath = "webapp/libs/step3.json"

def GetAllAttributes(content, numEntities):
    entityDict = {}
    totalDict = {}
    entityDict = ExtractEntities(content, numEntities)
    questionDict, answerDict = ExtractAllQuestions(content)
    index = 0
    for key in entityDict.keys():
        summary, keyWords = GenerateSummary(ExtractSentences(key, content))
        releventSents = ExtractSentences(key, content)
        releventSents = ' '.join(releventSents)
        ent = ExtractEntities(releventSents, 10)
        entString = ""
        for relKey in ent.keys():
            entString += relKey + ", "
        sentiment = ExtractSentiments(key, content)
        quest = ExtractRelevantQuestions(questionDict, answerDict, key)
        properyDict = {"Index": index,
                       "Summary": summary,
                       "Questions": quest,
                       "Keywords": keyWords,
                       "Entities": entString,
                       "Sentiment": sentiment}
        totalDict[key] = properyDict
        index += 1
    return totalDict

# Given an entity, perform ExtractSentences and then find the average sentiment of
# all of the sentences involved. Returns a dict with the keys of positive, neutral,
# negative and mixed and the values of their corresponding weight in the sentences ranging
# from 0.0 to 1.0
def ExtractSentiments(entity, content):
    sents = ExtractSentences(entity, content)
    comprehend = boto3.client(service_name='comprehend', region_name='us-west-2')
    entitySentiment = {"positive": 0.0, "negative": 0.0, "mixed": 0.0, "neutral": 0.0}
    sents = ' '.join(sents)
    if sents.__len__() > 4500:
        sents = __SplitString(sents, 4500)
    else:
        sents = [sents]
    for s in sents:
        sentFile = comprehend.detect_sentiment(Text=s, LanguageCode='en')
        entitySentiment["positive"] += round(sentFile["SentimentScore"]["Positive"], 4)
        entitySentiment["negative"] += round(sentFile["SentimentScore"]["Negative"], 4)
        entitySentiment["mixed"] += round(sentFile["SentimentScore"]["Mixed"], 4)
        entitySentiment["neutral"] += round(sentFile["SentimentScore"]["Neutral"], 4)
    return entitySentiment

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
            if not questionFound or answerFound:
                index += 1
                questionDict[index] = []
                questionFound = True
                answerFound = False
            questionDict[index].append(vals)
            continue
        if questionFound:
            if answerFound and not re.match(r'^(\w+[:])', vals):
                answerDict[index].append(vals)
                continue
            if re.match(r'^(\w+[:])', vals) and not answerFound:
                answerDict[index] = []
                answerFound = True
                answerDict[index].append(vals)
                continue
            if answerFound and re.match(r'^(\w+[:])', vals):
                questionFound = False
    return questionDict, answerDict

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
    comprehend = boto3.client(service_name='comprehend', region_name='us-west-2')

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

# Public method for extracting the summary of a given text
# INPUT: A bunch of text
# OUTPU: A dictionary containing the summary and keywords
def GenerateSummary(docInput):
    docInput = RemoveQuestions(docInput)
    __StepOne(docInput)
    __StepTwo()
    __StepThree()
    return __StepFour()

# Steps for generating the summary of provided text
def __StepOne(docInput):
    docInput = ' '.join(docInput)
    jsonData = {"id": 0, "text": docInput}
    with open('webapp/libs/summaryData.json', 'w') as outFile:
        json.dump(jsonData, outFile)
    with open(stepOnePath, 'w') as f:
        for graf in pytextrank.parse_doc(pytextrank.json_iter("webapp/libs/summaryData.json")):
            f.write("%s\n" % pytextrank.pretty_print(graf._asdict()))

def __StepTwo():
    graph, ranks = pytextrank.text_rank(stepOnePath)
    pytextrank.render_ranks(graph, ranks)

    with open(stepTwoPath, 'w') as f:
        for r1 in pytextrank.normalize_key_phrases(stepOnePath, ranks):
            f.write("%s\n" % pytextrank.pretty_print(r1._asdict()))

def __StepThree():
    kernel = pytextrank.rank_kernel(stepTwoPath)

    with open(stepThreePath, 'w') as f:
        for s in pytextrank.top_sentences(kernel, stepOnePath):
            f.write(pytextrank.pretty_print(s._asdict()))
            f.write("\n")

def __StepFour():
    phrases = ", ".join(set([p for p in pytextrank.limit_keyphrases(stepTwoPath, phrase_limit=12)]))
    sent_iter = sorted(pytextrank.limit_sentences(stepThreePath, word_limit=150), key=lambda x: x[1])
    s = []

    for sent_text, idx in sent_iter:
        s.append(pytextrank.make_sentence(sent_text))

    graf_text = " ".join(s)
    summaryDict = {"summary": graf_text, "keywords": phrases}
    return graf_text, phrases
