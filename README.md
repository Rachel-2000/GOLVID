# Prompt4UniParsing

## Dataset

- Raw logs: https://github.com/logpai/loghub

- Embeddings: https://drive.google.com/file/d/1PpV-5GIiA3KZWo5KSaMOlX4SCRfap7mS/view?usp=sharing

## How to run

In the current version, you need to firstly initialize a ModelTester instance:

```
tester = ModelTester(
                  log_path = "/your_path_to_logs/Hadoop_2k.log_structured.csv",
                  dataset = "Hadoop",
                  emb_path = "embeddings",	# the path to embedding json files   
                  cand_ratio = 0.2,       	# ratio of candidate set
                  split_method = "DPP",   	# random or DPP
                  warmup=False,
                  )
```

Then, you can run a demo to parse a random selected log from the test set by:

```
tester.textDemo(model = "curie", model_name = "gptC", max_token = 60, N=5)
```

You can also run batch testing:

```
tester.textModelBatchTest(model = "curie", 
                          model_name = "gptC", 
                          max_token = 80,       # token number in model response
                          limit = 100,          # number of logs for testing, <= 2000*(1-cand_ratio)
                          N=5,                  # number of examples in the prompt
                          )
```

The sample codes are in batchtest.py.