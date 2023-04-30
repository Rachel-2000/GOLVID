#!/bin/bash
# dataset: HDFS, Spark, BGL, Windows, Linux, Andriod, Mac, Hadoop, HealthApp, OpenSSH, Thunderbird, Proxifier, Apache, HPC, Zookeeper, OpenStack
openai_key="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# RQ1
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


# RQ2:
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