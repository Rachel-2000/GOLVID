#!/bin/bash
# model: HDFS, Spark, BGL, Windows, Linux, Andriod, Mac, Hadoop, HealthApp, OpenSSH, Thunderbird, Proxifier, Apache, HPC, Zookeeper, OpenStack
openai_key="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

python batchtest.py -key $openai_key --model HDFS
python batchtest.py -key $openai_key --model Spark
python batchtest.py -key $openai_key --model BGL
python batchtest.py -key $openai_key --model Windows
python batchtest.py -key $openai_key --model Linux
python batchtest.py -key $openai_key --model Andriod
python batchtest.py -key $openai_key --model Mac
python batchtest.py -key $openai_key --model Hadoop
python batchtest.py -key $openai_key --model HealthApp
python batchtest.py -key $openai_key --model OpenSSH
python batchtest.py -key $openai_key --model Thunderbird
python batchtest.py -key $openai_key --model Proxifier
python batchtest.py -key $openai_key --model Apache
python batchtest.py -key $openai_key --model HPC
python batchtest.py -key $openai_key --model Zookeeper
python batchtest.py -key $openai_key --model OpenStack

