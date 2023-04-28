# Prompt4UniParsing

## Dataset

- Raw logs: https://github.com/logpai/loghub


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

## Result

```
HDFS:	 PA:	 0.998889	 PTA:	 0.818182	 RTA:	 0.900000
Spark:	 PA:	 0.999444	 PTA:	 0.882353	 RTA:	 0.882353
BGL:	 PA:	 0.981667	 PTA:	 0.857143	 RTA:	 0.867470
Windows:	 PA:	 1.000000	 PTA:	 1.000000	 RTA:	 1.000000
Linux:	 PA:	 0.997222	 PTA:	 0.950000	 RTA:	 0.904762
Andriod:	 PA:	 0.938333	 PTA:	 0.846154	 RTA:	 0.838095
Mac:	 PA:	 0.849444	 PTA:	 0.587814	 RTA:	 0.616541
HealthApp:	 PA:	 0.996111	 PTA:	 0.950000	 RTA:	 0.950000
OpenSSH:	 PA:	 0.939444	 PTA:	 0.947368	 RTA:	 0.900000
Thunderbird:	 PA:	 0.967778	 PTA:	 0.656716	 RTA:	 0.862745
Proxifier:	 PA:	 1.000000	 PTA:	 1.000000	 RTA:	 1.000000
Apache:	 PA:	 1.000000	 PTA:	 1.000000	 RTA:	 1.000000
HPC:	 PA:	 0.979444	 PTA:	 0.735294	 RTA:	 0.892857
Zookeeper:	 PA:	 1.000000	 PTA:	 1.000000	 RTA:	 1.000000
Hadoop:	 PA:	 0.993333	 PTA:	 0.914894	 RTA:	 0.955556
OpenStack:	 PA:	 0.997778	 PTA:	 0.950000	 RTA:	 0.950000
```

You can also run `python draw.py` to generate all plots in the paper.
