# Prompt4UniParsing

## Dataset

- Raw logs: https://github.com/logpai/loghub

- Embeddings: https://drive.google.com/file/d/1PpV-5GIiA3KZWo5KSaMOlX4SCRfap7mS/view?usp=sharing

## How to run

### All-in-one

Just run `./batch.sh`. Remember to use your own openai key

```shell
#!/bin/bash
# dataset: HDFS, Spark, BGL, Windows, Linux, Andriod, Mac, Hadoop, HealthApp, OpenSSH, Thunderbird, Proxifier, Apache, HPC, Zookeeper, OpenStack
openai_key="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

python batchtest.py -key $openai_key --dataset HDFS
python batchtest.py -key $openai_key --dataset Spark
python batchtest.py -key $openai_key --dataset BGL
python batchtest.py -key $openai_key --dataset Windows
python batchtest.py -key $openai_key --dataset Linux
python batchtest.py -key $openai_key --dataset Andriod
python batchtest.py -key $openai_key --dataset Mac
python batchtest.py -key $openai_key --dataset Hadoop
python batchtest.py -key $openai_key --dataset HealthApp
python batchtest.py -key $openai_key --dataset OpenSSH
python batchtest.py -key $openai_key --dataset Thunderbird
python batchtest.py -key $openai_key --dataset Proxifier
python batchtest.py -key $openai_key --dataset Apache
python batchtest.py -key $openai_key --dataset HPC
python batchtest.py -key $openai_key --dataset Zookeeper
python batchtest.py -key $openai_key --dataset OpenStack
```

### Step by step

In the current version, you need to firstly initialize a ModelTester instance:

```python
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

```python
tester.textDemo(model = "curie", model_name = "gptC", max_token = 60, N=5)
```

You can also run batch testing:

```python
tester.textModelBatchTest(model = "curie", 
                          model_name = "gptC", 
                          max_token = 80,       # token number in model response
                          limit = 100,          # number of logs for testing, <= 2000*(1-cand_ratio)
                          N=5,                  # number of examples in the prompt
                          )
```

The sample codes are in batchtest.py.