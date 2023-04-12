import json
import os
import pandas as pd
import re
import time
import openai
import random
from dpp import *
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from openai.embeddings_utils import get_embedding, cosine_similarity


class ModelTester():
  def __init__(self, 
        log_path, 
        result_path, 
        map_path, 
        dataset,
        emb_path,
        cand_ratio,
        split_method, # random or DPP
        warmup, # warmup or not
    ):

    self.log_path = log_path + "/{}/{}_2k.log_structured.csv".format(dataset,dataset)
    self.result_path = result_path
    self.map_path = map_path + "/{}_{}_lookupmap.json".format(cand_ratio,dataset)
    self.dataset = dataset
    self.emb_path = emb_path + "/{}.json".format(dataset)
    self.cand_ratio = cand_ratio
    self.split_method = split_method
    self.warmup = warmup

    # split candidate set
    self.log_test, self.log_cand, self.gt_test, self.gt_cand = self.splitCandidates(self.log_path, self.cand_ratio, self.split_method)

    # build lookup map
    self.lookUpMap = self.buildLookupMap(self.map_path)
  
  # generate lookup map
  def buildLookupMap(self, map_path):
    # build lookup map
    if (os.path.exists(map_path)): 
      print("Load look up map of {} ...".format(self.dataset))
      with open(map_path, "r") as file:
            return json.load(file)
    else: return self.generateLuMap(map_path)

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
          candidate_idx = getDppIndex(log_embs, 2000, cand_ratio)
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
      print('Generating lookup map for {} ...'.format(self.dataset))
      with open(self.emb_path, "r") as file:
          emb_map = json.load(file)

      test_embs = [emb_map[log] for log in self.log_test]
      cand_embs = [emb_map[log] for log in self.log_cand]

      lookUpMap = {}
      for test_idx in tqdm(range(len(self.log_test))):
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
              '\n<extraction>: <START> ' + self.gt_cand[idxes[i]] + ' <END>\n\n'  
      similarist_gt = self.gt_cand[idxes[0]]
      return prompt, similarist_gt

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

  # correctly identified templates over total num of identified template
  def evaluatePTA(self, result):
      # generate a "template: log indexes list" mapping for groundtruth
      oracle_tem_dict = {}
      for idx in range(len(result)):
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
      for idx in range(len(result)):
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

  def writeResult(self, result, path, limit):
      output = pd.DataFrame(data={"log": self.log_test[:limit], "template": result})
      output.to_csv(path, index=False)

  # extract result from model's response
  def extractResultTemplate(self, text):
      # this pattern is for ChatGPT
      # pattern = re.compile('<START> <Event\d> (.+) <END>')
      pattern = re.compile('<START> (.+) <END>')
      # findall return a list
      result = pattern.findall(text)
      if (len(result)): return result[0]
      else: return ""


  def textModelBatchTest(self, model, model_name, max_token, limit, N=5):
      token_len = 128 # init token length
      # list to store the model's parsing on each log message
      answer_list = []
      instruction = "For each log after <prompt> tag, extract one log template\
(substitute variable tokens in the log as <*> and remain constant tokens to construct the template)\
and put the template after <extraction> tag and between <START> and <END> tags."

      self.result_path = self.result_path +  "/{}_{}_result.csv".format(limit,self.dataset)
      # if the result file already exists, load it
      if os.path.exists(self.result_path):
        print("Result file already exists, loading ...")
        answer_list = pd.read_csv(self.result_path)['template'].to_list()
      else:
        # if the result file does not exist, use api to generate result
        print("Result file does not exist, generating result ...")
        for line_idx in tqdm(range(len(self.log_test))):
          if line_idx >= limit: break
          line = self.log_test[line_idx]
          # get a prompt with five examples for each log message
          prompt, similarist_gt = self.generatePrompt(line, nearest_num=N)
          while True:
            try:
              response = openai.Completion.create(
                                                  model=model, 
                                                  prompt=instruction + "\n\n\n" + prompt + "<prompt>:" + line + "\n<extraction>: ", 
                                                  temperature=0,
                                                  max_tokens=token_len)
            except: # if interrupt by request busy
              # print("Request busy, log {} is now waiting ...".format(line_idx))
              time.sleep(0.1)
            else:
              # if no exception, the model response a dict
              # format for CodeX, GPT-D
              # print(response)
              # to avoid empty response
              result = self.extractResultTemplate(response["choices"][0]["text"])
              if result != "":
                answer_list.append(result)
                break
              else:
                if token_len >= max_token:
                  result = similarist_gt
                  answer_list.append(result)
                  print("Too long log message: {}".format(line) + '\n')
                  print("Too long log error: token_len exceeds {}, stop increasing, using the similarist log message's tempate as prediction".format(token_len) + '\n')
                  print("Raw ouput: {}".format(response["choices"][0]["text"]) + '\n')
                  print("Similarist log template: {}".format(result) + '\n')
                  token_len = 128
                  break
                else:
                  token_len *= 2
                  print("token_len doubled to {}".format(token_len))
                

      PA = self.evaluatePA(answer_list)
      PTA = self.evaluatePTA(answer_list)
      RTA = self.evaluateRTA(answer_list)
      print("{}:\t PA:\t {:.6f}\t PTA:\t {:.6f}\t RTA:\t {:.6f}".format(self.dataset, PA, PTA, RTA))
      f = open("benchmark.txt", 'a')
      f.write("{}:\t PA:\t {:.6f}\t PTA:\t {:.6f}\t RTA:\t {:.6f}".format(self.dataset, PA, PTA, RTA) + '\n')
      f.close()
      self.writeResult(answer_list, self.result_path, limit)
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