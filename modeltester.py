import json
import os
import pandas as pd
import re
import time
import openai
import random
from dpp import *
from sklearn.model_selection import train_test_split
from openai.embeddings_utils import get_embedding, cosine_similarity


class ModelTester():
  def __init__(self, 
        # raw_log_path,   # .log file and .log_structured.csv file
        log_path, 
        # look_up_map_path,
        dataset,
        emb_path,
        cand_ratio = 0.2,
        split_method = "random", # random or DPP
        warmup=False,
    ):

    self.dataset = dataset
    self.emb_path = emb_path + "/" + dataset + ".json"
    # split for candidate set and test set
    self.log_test, self.log_cand, self.gt_test, self.gt_cand = self.splitCandidates(log_path, cand_ratio, split_method)
    # self.cand_ratio = cand_ratio
    # whether do warmup
    self.warmup = warmup
    # look up map
    if (os.path.exists(dataset+"_lookupmap.json")): 
      with open(dataset+"_lookupmap.json", "r") as file:
            self.lookUpMap = json.load(file)
    else: self.lookUpMap = self.generateLuMap(dataset+"_lookupmap.json")

  # extract groundtruth templates from log_structured.csv file
  def extractCsvContent(self, groundtruth_path):
      dataframe = pd.read_csv(groundtruth_path)
      content_list = dataframe['Content'].values.tolist()
      return content_list

  # extract groundtruth templates from log_structured.csv file
  def extractCsvTemplate(self, groundtruth_path):
      dataframe = pd.read_csv(groundtruth_path)
      template_list = dataframe['EventTemplate'].values.tolist()
      return template_list

  # split the candidate set from raw logs
  def splitCandidates(self, groundtruth_path, cand_ratio, method="random"):
      log_list = self.extractCsvContent(groundtruth_path)
      groundtruth_template = self.extractCsvTemplate(groundtruth_path)
      if method == "random":
          # split randomly
          log_test, log_cand, gt_test, gt_cand = train_test_split(log_list, groundtruth_template, test_size=cand_ratio, random_state=42)
      elif method == "DPP":
          # split with diversity
          file = open(self.emb_path, "r")
          emb_map = json.load(file)
          file.close()
          log_embs = []
          for log in log_list:
            log_embs.append(emb_map[log])
          print(f"length of log embs is {len(log_embs)}")
          candidate_idx = getDppIndex(log_embs, item_size=2000, cand_ratio)
          log_test, log_cand, gt_test, gt_cand = DPPsplit(log_list, groundtruth_template, candidate_idx)
      return log_test, log_cand, gt_test, gt_cand

  def generateEmbeddings(self, str_list):
      # each embedding has length 2048
      # engine: text-search-{ada, babbage, curie, davinci}-{query, doc}-001 
      # | code-search-{ada, babbage}-{code, text}-001
      return [get_embedding(log, engine="text-search-babbage-query-001") for log in str_list]

  # generate a look up map that records the cosine similarity 
  # between two logs with descendant sequence
  def generateLuMap(self, look_up_map_path):
      # raw_log_list = self.generateEmbeddings(self.log_test)
      # cand_list = self.generateEmbeddings(self.log_cand)

      # get embeddings from embedding json file
      with open(self.emb_path, "r") as file:
          emb_map = json.load(file)

      test_embs = [emb_map[log] for log in self.log_test]
      cand_embs = [emb_map[log] for log in self.log_cand]
      # print(len(emb_map))
      # print(len(self.log_test))
      # print(len(self.log_cand))
      # print(len(test_embs))
      # print(len(cand_embs))

      lookUpMap = {}
      for test_idx in range(len(self.log_test)):
        dis_dict = {}
        for cand_idx in range(len(self.log_cand)):
          dis_dict[cosine_similarity(test_embs[test_idx], cand_embs[cand_idx])] = cand_idx
        # get a list in sorted key (descending order), key = cosine similarity
        sorted_list = []
        for key in sorted(dis_dict, reverse=True): 
          sorted_list.append(dis_dict[key])
        # dict: {log_message : list of similar candidate indexes in order}
        lookUpMap[self.log_test[test_idx]] = sorted_list

      # write the map into a json file
      with open(look_up_map_path, 'w') as file:
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
        # update: modify the prompt format to <prompt>:xx \n <extraction>:xx \n\n <prompt>: xx ...
        prompt = prompt + "<prompt>:" + self.log_cand[idxes[i]] + \
                '<extraction>: <START> ' + self.gt_cand[idxes[i]] + ' <END>\n\n'
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
        r = self.compareTemplate(result[i], self.gt_test[i])
        if not r: 
          print("Groundtruth: " + self.gt_test[i])
          print("Unmatched result: " + result[i])
        correct += r
        # correct += self.compareTemplate(result[i], self.gt_test[i])
      return correct/length

  # correctly identified templates over total num of identified template
  def evaluatePTA(self, result):
      # generate a "template: log indexes list" mapping for groundtruth
      oracle_tem_dict = {}
      for idx in range(len(self.gt_test)):
          if self.gt_test[idx] not in oracle_tem_dict:
            oracle_tem_dict[self.gt_test[idx]] = [idx]
          else: oracle_tem_dict[self.gt_test[idx]].append(idx)

      # generate mapping for identified template
      result_tem_dict = {}
      for idx in range(len(result)):
          if result[idx] not in result_tem_dict:
            result_tem_dict[result[idx]] = [idx]
          else: result_tem_dict[result[idx]].append(idx)

      correct_num = 0
      for key in result_tem_dict.keys():
          if key not in oracle_tem_dict: continue
          else:
            if oracle_tem_dict[key] == result_tem_dict[key]: correct_num += 1
      
      return correct_num/len(result_tem_dict)

  # correctly identified templates over total num of oracle template
  def evaluateRTA(self, result):
      oracle_tem_dict = {}
      for idx in range(len(self.gt_test)):
          if self.gt_test[idx] not in oracle_tem_dict:
            oracle_tem_dict[self.gt_test[idx]] = [idx]
          else: oracle_tem_dict[self.gt_test[idx]].append(idx)

      # generate mapping for identified template
      result_tem_dict = {}
      for idx in range(len(result)):
          if result[idx] not in result_tem_dict:
            result_tem_dict[result[idx]] = [idx]
          else: result_tem_dict[result[idx]].append(idx)

      correct_num = 0
      for key in oracle_tem_dict.keys():
          if key not in result_tem_dict: continue
          else:
            if oracle_tem_dict[key] == result_tem_dict[key]: correct_num += 1
      
      return correct_num/len(oracle_tem_dict)

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
      wordCount = 0
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
          # print(response)
          answer_list.append(self.extractResultTemplate(response["choices"][0]["message"]["content"]))

      PA = self.evaluatePA(answer_list)
      print("The parsing accuracy in this test is {:.4}".format(PA))
      self.writeResult(answer_list, "{}_test_result.txt".format(model_name))
      return

  def textModelBatchTest(self, model, model_name, max_token, limit, N=5):
      # list to store the model's parsing on each log message
      answer_list = []
      instruction = "For each log after <prompt> tag, extract one log template\
(substitute variable tokens in the log as <*> and remain constant tokens to construct the template)\
and put the template after <extraction> tag and between <START> and <END> tags."

      for line_idx in range(len(self.log_test)):
        if line_idx >= limit: break
        line = self.log_test[line_idx]
        # get a prompt with five examples for each log message
        prompt = self.generatePrompt(line, nearest_num=N)
        try:
          response = openai.Completion.create(
                                              model=model, 
                                              prompt=instruction + "\n\n\n" + prompt + "<prompt>:" + line, 
                                              temperature=0,
                                              max_tokens=max_token)
        except: # if interrupt by request busy
          print("Request busy, log {} is now waiting ...".format(line_idx))
          time.sleep(5)
          line_idx -= 1
          continue
        else:
          # if no exception, the model response a dict
          # format for CodeX, GPT-D
          # print(response)
          answer_list.append(self.extractResultTemplate(response["choices"][0]["text"]))

      PA = self.evaluatePA(answer_list)
      PTA = self.evaluatePTA(answer_list)
      RTA = self.evaluateRTA(answer_list)
      print("The parsing accuracy in this test is {:.4}".format(PA))
      print("The parsing template accuracy in this test is {:.4}".format(PTA))
      print("The oracle template accuracy in this test is {:.4}".format(RTA))
      self.writeResult(answer_list, "{}_test_result.txt".format(model_name))
      return

  def textDemo(self, model, model_name, max_token, N=5):
      # instruction = "extract the log template after <extraction> and between <START> and <END> (substitute constant tokens in the message as <*>) for one log message after <prompt>"
      instruction = "For each log after <prompt> tag, extract one log template\
(substitute variable tokens in the log as <*> and remain constant tokens to construct the template)\
and put the template after <extraction> tag and between <START> and <END> tags."
#Digits are usually variable tokens.
      line = random.sample(self.log_test, 1)[0] # random.sample return a list
      prompt = self.generatePrompt(line, nearest_num=N)
      response = openai.Completion.create(
                                          model=model, 
                                          prompt=instruction + "\n\n\n" + prompt + "<prompt>:" + line + "\n<extraction>: ", 
                                          temperature=0,
                                          max_tokens=max_token)

      print("Prompt = " + instruction + "\n\n\n" + prompt + "<prompt>:" + line + "\n<extraction>: ")
      print("Result = " + response["choices"][0]["text"])