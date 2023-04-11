import openai
from modeltester import ModelTester
# get a tester object with data
openai.api_key = 'your_key'

tester = ModelTester(
                  log_path = "/your_path_to_logs/Hadoop_2k.log_structured.csv",              # .log_structured_csv
                  dataset = "Hadoop",
                  emb_path = "embeddings", 
                  cand_ratio = 0.2,       # ratio of candidate set
                  split_method = "DPP",   # random or DPP
                  warmup=False,
                  )