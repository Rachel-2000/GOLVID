import json
import os
import pandas as pd
import re
import time
import openai
from sklearn.model_selection import train_test_split
from openai.embeddings_utils import get_embedding, cosine_similarity


class ModelTester():
  def __init__(self, 
        raw_log_path,   # .log file and .log_structured.csv file
        groundtruth_path, 
        warmup=False,
    ):
    # raw log messages and groundtruth paths
    self.log_test, self.log_cand, self.gt_test, self.gt_cand = self.splitCandidates(raw_log_path, groundtruth_path)
    # model: "gpt-3.5-turbo" for ChatGPT, "code-davinci-002" for CodeX
    self.warmup = warmup
    # look up map
    if (os.path.exists("look_up_map.txt")): 
      with open("look_up_map.txt", "r") as file:
            self.lookUpMap = json.load(file)
    else: self.lookUpMap = self.generateLuMap()

  # extract groundtruth templates from log_structured.csv file
  def extractCsvTemplate(self, groundtruth_path):
    dataframe = pd.read_csv(groundtruth_path)
    template_list = dataframe['EventTemplate'].values.tolist()
    return template_list

  # split the candidate set from raw logs
  def splitCandidates(self, raw_log_path, groundtruth_path, method="random"):
    log_list = []
    for line in open(raw_log_path, 'r'):
      log_list.append(line)
    groundtruth_template = self.extractCsvTemplate(groundtruth_path)
    if (method=="random"):
      # split randomly
      log_test, log_cand, gt_test, gt_cand = train_test_split(log_list, groundtruth_template, test_size=0.2, random_state=42)
    return log_test, log_cand, gt_test, gt_cand

  def generateEmbeddings(self, str_list):
    # each embedding has length 2048
    # engine: text-search-{ada, babbage, curie, davinci}-{query, doc}-001 
    # | code-search-{ada, babbage}-{code, text}-001
    return [get_embedding(log, engine="text-search-babbage-query-001") for log in str_list]

  # generate a look up map that records the cosine similarity 
  # between two logs with descendant sequence
  def generateLuMap(self):
    raw_log_list = self.generateEmbeddings(self.log_test)
    cand_list = self.generateEmbeddings(self.log_cand)
    lookUpMap = {}
    for test_idx in range(len(self.log_test)):
      dis_dict = {}
      for cand_idx in range(len(self.log_cand)):
        dis_dict[cosine_similarity(raw_log_list[test_idx], cand_list[cand_idx])] = cand_idx
      # get a list in sorted key (descending order)
      sorted_list = []
      for key in sorted(dis_dict, reverse=True): 
        sorted_list.append(dis_dict[key])
      # dict: {log_message : list of similar candidate indexes in order}
      lookUpMap[self.log_test[test_idx]] = sorted_list

    # write the map into a file
    with open('look_up_map.txt', 'w') as file:
     file.write(json.dumps(lookUpMap))

    return lookUpMap
    
  # find the N most similar logs to the input log
  # the index represents the similar ranking
  def getNearest(self, log, N=5):
    cand_list = self.lookUpMap[log]
    # return the idexes of most similar N log candidates
    return cand_list[:N]

  # generate a prompt in str for a specific log message
  def generatePrompt(self, log, nearest_num=5):
    idxes = self.getNearest(log, nearest_num)
    prompt = ""
    # backward iteration
    for i in range(len(idxes)-1,-1,-1):
      prompt = prompt + "<prompt>:" + self.log_cand[idxes[i]] + \
               '\n<extraction>: <START> ' + self.gt_cand[idxes[i]] + ' <END>\n'
    return prompt

  # compare if template is correctly extracted: if yes, return 1; else return 0
  def compareTemplate(self, tpl_1, tpl_2):
    token_list_1 = tpl_1.split()
    token_list_2 = tpl_2.split()
    if (len(token_list_1) != len(token_list_2)): return 0
    length = len(token_list_1)
    for i in range(length):
      if (token_list_1[i] != token_list_2[i]): return 0
    return 1;

  # calculate parsing accuracy
  def evaluatePA(self, result):
    # len(result) may smaller than len(groundtruth)
    length = len(result)
    if length == 0: return 0
    correct = 0
    for i in range(length):
      correct += self.compareTemplate(result[i], self.gt_test[i])
    return correct/length

  def writeResult(self, result, path):
    with open(path, 'w') as file:
      for line in result:
        file.write(line + '\n')

  # extract result from model's response
  def extractResultTemplate(self, text):
    # this pattern is for ChatGPT
    # pattern = re.compile('<START> <Event\d> (.+) <END>')
    pattern = re.compile('<START> (.+) <END>')
    # findall return a list
    result = pattern.findall(text)
    if (len(result)): return result[0]
    else: return ""

  # test log message parsing in chat completion model
  def chatModelBatchTest(self, model, model_name, limit):
      # list to store the model's parsing on each log message
      answer_list = []
      for line_idx in range(len(self.log_test)):
        if line_idx >= limit: break
        line = self.log_test[line_idx]
        # get a prompt with five examples for each log message
        prompt = self.generatePrompt(line, nearest_num=5)
        try:
          response = openai.ChatCompletion.create(
          model = model,
          messages = [{"role": "system", "content": "select <Event#> and extract log template (substitute constant tokens in the message as <*>) after <Event#>"}] 
          + [{"role": "user", "content": prompt + "<prompt>:" + line + '\n'}])
        except: # if interrupt by request busy
          # wait for 30 seconds if request busy
          print("Request busy, log {} is now waiting ...".format(line_idx))
          time.sleep(5)
          line_idx -= 1
          continue
        else:
          # if no exception, the model response a dict
          # the format here is for ChatGPT, for CodeX it should be 'response["choices"][0]["text"]'
          answer_list.append(self.extractResultTemplate(response["choices"][0]["message"]["content"]))

      PA = self.evaluatePA(answer_list)
      print("The parsing accuracy in this test is {:.4}".format(PA))
      self.writeResult(answer_list, "{}_test_result.txt".format(model_name))
      return

  def textModelBatchTest(self, model, model_name, max_token, limit):
      # list to store the model's parsing on each log message
      answer_list = []
      instruction = "extract a log template after <extraction> (substitute constant tokens in the message as <*>) for one log message after <prompt>"
      for line_idx in range(len(self.log_test)):
        if line_idx >= limit: break
        line = self.log_test[line_idx]
        # get a prompt with five examples for each log message
        prompt = self.generatePrompt(line, nearest_num=5)
        try:
          response = openai.Completion.create(
                                              model=model, 
                                              prompt=instruction + "\n\n\n" + prompt + "<prompt>:" + line + "\n", 
                                              temperature=0,
                                              max_tokens=max_token)
        except: # if interrupt by request busy
          print("Request busy, log {} is now waiting ...".format(line_idx))
          time.sleep(5)
          line_idx -= 1
          continue
        else:
          # if no exception, the model response a dict
          # format for CodeX, GPT-3
          answer_list.append(self.extractResultTemplate(response["choices"][0]["text"]))

      PA = self.evaluatePA(answer_list)
      print("The parsing accuracy in this test is {:.4}".format(PA))
      self.writeResult(answer_list, "{}_test_result.txt".format(model_name))
      return