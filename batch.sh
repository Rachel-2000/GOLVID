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

