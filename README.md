# README

## Dataset

- Raw logs: https://github.com/logpai/loghub

## How to run

### All-in-one

Just run `./batch.sh`. Remember to use your own openai key

#### RQ1:

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

#### RQ2:

```shell
python batchtest.py -key $openai_key --dataset Mac --split_method random --subname _randomSplit
python batchtest.py -key $openai_key --dataset Mac --order_method random --subname _randomOrder
python modeltester_no_locators.py -key $openai_key --dataset Mac --subname _noLocators

python batchtest.py -key $openai_key --dataset Mac --cand_ratio 0.15 --subname _candRatio015
python batchtest.py -key $openai_key --dataset Mac --cand_ratio 0.125 --subname _candRatio0125
python batchtest.py -key $openai_key --dataset Mac --cand_ratio 0.075 --subname _candRatio0075
python batchtest.py -key $openai_key --dataset Mac --cand_ratio 0.05 --subname _candRatio005
python batchtest.py -key $openai_key --dataset Mac --N 1 --subname _N1
python batchtest.py -key $openai_key --dataset Mac --N 3 --subname _N3
python batchtest.py -key $openai_key --dataset Mac --N 7 --subname _N7
python batchtest.py -key $openai_key --dataset Mac --N 9 --subname _N9

python batchtest.py -key $openai_key --dataset Mac --permutation descend --subname _descend
python batchtest.py -key $openai_key --dataset Mac --permutation random --subname _random

python batchtest.py -key $openai_key --dataset Mac --model ada --subname _ada
python batchtest.py -key $openai_key --dataset Mac --model babbage --subname _babbage
python batchtest.py -key $openai_key --dataset Mac --model davinci --subname _davinci
```

You can also run `python draw.py` to generate all plots in the paper.

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

Additionally, we compare the grouping accuracy as a reference. The results are shown below:

```
HDFS:    GA:     0.890000
Spark:   GA:     0.820000
BGL:     GA:     0.963889
Windows:         GA:     1.000000
Linux:   GA:     0.994444
Andriod:         GA:     0.948333
Mac:     GA:     0.813889
Hadoop:  GA:     0.991667
HealthApp:       GA:     1.000000
OpenSSH:         GA:     0.728889
Thunderbird:     GA:     0.893889
Proxifier:       GA:     1.000000
Apache:  GA:     1.000000
HPC:     GA:     0.958333
Zookeeper:       GA:     1.000000
OpenStack:       GA:     0.981111
Average grouping accuracy: 0.9365277777777778
```



<img src="https://github.com/Rachel-2000/GOLVID/blob/main/pictures/box_GA.png" alt="box_GA" style="zoom: 80%;" />

You can also run `evaluate_group_acc.py` to reproduce the GA evaluation.
