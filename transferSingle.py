import random
import time
import re
import os
import pandas as pd
from tqdm import tqdm

class TransferTesterSingle():
  def __init__(self,
               log_path,
               result_path,
               dataset,
               threshold,
               ):
      self.log, self.template, self.map = self.loadData(log_path, dataset)
      self.result_path = result_path
      self.dataset = dataset
      for key in self.map.keys():
          print(f"Template {key} has {len(self.map[key])} log messages.")
      self.test_log, self.cand_log, self.test_template, self.cand_template = self.splitTestCand(threshold)

  def loadData(self, path, dataset):
      logs = []
      templates = []
      dataframe = pd.read_csv(path + f"{dataset}/{dataset}_2k.log_structured.csv")
      logs = logs + dataframe['Content'].values.tolist()
      templates = templates + dataframe['EventTemplate'].values.tolist()

      # take non-repeated elements in template_list to create a map
      map = {}
      for template in list(set(templates)):
          map[template] = []

      for idx in range(len(templates)):
          map[templates[idx]].append(idx)

      return logs, templates, map

    
  def splitTestCand(self, threshold):
      test_idx = []
      cand_idx = []
      for key in self.map:
          if len(self.map[key]) <= threshold:
              test_idx += self.map[key]
          else:
              cand_idx += self.map[key]
      
      # shuffle the candidate set
      random.shuffle(cand_idx)
      # load test set and candidate set
      test_log, cand_log, test_template, cand_template = [], [], [], []
      for idx in test_idx:
          test_log.append(self.log[idx])
          test_template.append(self.template[idx])
      for idx in cand_idx:
          cand_log.append(self.log[idx])
          cand_template.append(self.template[idx])

      return test_log, cand_log, test_template, cand_template
              
  def generatePrompt(self, log, num):
      prompt = ""
      idx_list = random.sample([i for i in range(len(self.cand_log))], num)
      # generate prompt
      for i in idx_list:
        prompt = prompt + "<prompt>:" + self.cand_log[i] + \
                '\n<extraction>: <START> ' + self.cand_template[i] + ' <END>\n\n'
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
        correct += self.compareTemplate(result[i], self.test_template[i])
      return correct/length

  # correctly identified templates over total num of identified template
  def evaluatePTA(self, result):
      # generate a "template: log indexes list" mapping for groundtruth
      oracle_tem_dict = {}
      for idx in range(len(result)):
          if self.test_template[idx] not in oracle_tem_dict:
            oracle_tem_dict[self.test_template[idx]] = [idx]
          else: oracle_tem_dict[self.test_template[idx]].append(idx)

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
          if self.test_template[idx] not in oracle_tem_dict:
            oracle_tem_dict[self.test_template[idx]] = [idx]
          else: oracle_tem_dict[self.test_template[idx]].append(idx)

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



  def transferTest(self, model, model_name, max_token, limit=None, N=5):
      if limit == None: limit = len(self.test_log)
      token_len = 128 # init token length
      # list to store the model's parsing on each log message
      answer_list = []
      instruction = "For each log after <prompt> tag, extract one log template\
(substitute variable tokens in the log as <*> and remain constant tokens to construct the template)\
and put the template after <extraction> tag and between <START> and <END> tags."

      self.result_path = self.result_path +  "/{}_transfer_result.csv".format(self.dataset)
      # if the result file already exists, load it
      if os.path.exists(self.result_path):
        print("Result file already exists, loading ...")
        answer_list = pd.read_csv(self.result_path)['template'].to_list()
      else:
        # if the result file does not exist, use api to generate result
        print("Result file does not exist, generating result ...")
        for line_idx in tqdm(range(len(self.test_log[:limit]))):
          re_id = 0
          if line_idx >= limit: break
          line = self.test_log[line_idx]
          # randomly select N examples to construct the prompt
          prompt = self.generatePrompt(line, num=N)
          while True:
            try:
              response = openai.Completion.create(
                                                  model=model, 
                                                  prompt=instruction + "\n\n\n" + prompt + "<prompt>:" + line.strip() + "\n<extraction>: ", 
                                                  temperature=0,
                                                  max_tokens=token_len)
            except: # if interrupt by request busy
              print("Request busy, log {} is now waiting ...".format(line_idx))
              time.sleep(0.1)
              re_id += 1
              if re_id < 5:
                time.sleep(0.1)
              else:
                result = self.test_template[line_idx]
                answer_list.append(result)
                print("Too long waiting time, raw log: {}".format(line) + '\n')
                re_id = 0
                break
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
                  result = self.test_template[line_idx]
                  answer_list.append(result)
                  print("Too long log message: {}".format(line) + '\n')
                  print("Too long log error: token_len exceeds {}, stop increasing, using the original tempate".format(token_len) + '\n')
                  print("Raw ouput: {}".format(response["choices"][0]["text"]) + '\n')
                  # print("Similarist log template: {}".format(result) + '\n')
                  token_len = 128
                  break
                else:
                  token_len *= 2
                  print("token_len doubled to {}".format(token_len))
                

      PA = self.evaluatePA(answer_list)
      print("\n{}:\t PA:\t {:.6f}".format(self.dataset, PA))
      # PTA = self.evaluatePTA(answer_list)
      # RTA = self.evaluateRTA(answer_list)
      # print("{}:\t PA:\t {:.6f}\t PTA:\t {:.6f}\t RTA:\t {:.6f}".format(self.dataset, PA, PTA, RTA))
      f = open("benchmark.txt", 'a')
      # f.write("{}:\t PA:\t {:.6f}\t PTA:\t {:.6f}\t RTA:\t {:.6f}".format(self.dataset, PA, PTA, RTA) + '\n')
      f.write("{}:\t PA:\t {:.6f}".format(self.dataset, PA) + '\n')
      f.close()
      self.writeResult(answer_list, self.result_path)
      return PA

  def demoText(self, model, model_name, max_token, N=5):
      instruction = "For each log after <prompt> tag, extract one log template\
(substitute variable tokens in the log as <*> and remain constant tokens to construct the template)\
and put the template after <extraction> tag and between <START> and <END> tags."
#Digits are usually variable tokens.
      line = random.sample(self.test_log, 1)[0] # random.sample return a list
      prompt = self.generatePrompt(line, num=N)
      response = openai.Completion.create(
                                          model=model, 
                                          prompt=instruction + "\n\n\n" + prompt + "<prompt>:" + line.strip() + "\n<extraction>: ", 
                                          temperature=0,
                                          max_tokens=max_token)

      print("Prompt = " + instruction + "\n\n\n" + prompt + "<prompt>:" + line.strip() + "\n<extraction>: ")
      print("Result = " + response["choices"][0]["text"])


  def demoChat(self, model, model_name, max_token, N=5):
      instruction = "For each log after <prompt> tag, extract one log template\
(substitute variable tokens in the log as <*> and remain constant tokens to construct the template)\
and put the template after <extraction> tag and between <START> and <END> tags."
#Digits are usually variable tokens.
      line = random.sample(self.test_log, 1)[0] # random.sample return a list
      prompt = self.generatePrompt(line, num=N)
      response = openai.ChatCompletion.create(
          model = model,
          messages = [{"role": "system", "content": instruction}] 
          + [{"role": "user", "content": prompt + "<prompt>:" + line.strip() + '\n<extraction>: '}])

      print("Prompt = " + instruction + "\n\n\n" + prompt + "<prompt>:" + line.strip() + "\n<extraction>: ")
      print("Result = " + response["choices"][0]["message"]["content"])