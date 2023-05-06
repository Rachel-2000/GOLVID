import os
import pandas as pd

def evaluateGA(dataset, groundtruth, result):
    # load logs and templates
    df_groundtruth = pd.read_csv(groundtruth)
    df_parsedlog = pd.read_csv(result)

    compared_list = df_parsedlog['log'].tolist()

    # select groundtruth logs that have been parsed
    # Content, EventTemplate
    # gtLogs = []
    parsed_idx = []
    for idx, row in df_groundtruth.iterrows():
        if row['Content'] in compared_list:
            parsed_idx.append(idx)
            compared_list.remove(row['Content'])

    if not (len(parsed_idx) == 1800):
        print(len(parsed_idx))
        print("Wrong number of groundtruth logs!")
        return 0

    df_groundtruth = df_groundtruth.loc[parsed_idx]

    # l1 = df_groundtruth['Content'].tolist()
    # l2 = df_parsedlog['log'].tolist()
    # l1.sort()
    # l2.sort()
    # print(f"The two lists are equivalent: {l1 == l2}")

    # grouping
    groundtruth_dict = {}
    for idx, row in df_groundtruth.iterrows():
        if row['EventTemplate'] not in groundtruth_dict:
            # create a new key
            groundtruth_dict[row['EventTemplate']] = [row['Content']]
        else: 
            # add the log in an existing group
            groundtruth_dict[row['EventTemplate']].append(row['Content'])

    result_dict = {}
    for idx, row in df_parsedlog.iterrows():
        if row['template'] not in result_dict:
            # create a new key
            result_dict[row['template']] = [row['log']]
        else: 
            # add the log in an existing group
            result_dict[row['template']].append(row['log'])

    # sorting for comparison
    for key in groundtruth_dict.keys():
        groundtruth_dict[key].sort()

    for key in result_dict.keys():
        result_dict[key].sort()

    # calculate grouping accuracy
    count = 0
    for parsed_group_list in result_dict.values():
        for gt_group_list in groundtruth_dict.values():
            if parsed_group_list == gt_group_list:
                count += len(parsed_group_list)
                break

    GA = count / 1800
    print("{}:\t GA:\t {:.6f}".format(dataset, GA))
    return GA

datasets = ['HDFS', 'Spark', 'BGL', 'Windows', 'Linux', 'Andriod', 'Mac', 'Hadoop', 'HealthApp', 'OpenSSH', 'Thunderbird', 'Proxifier', 'Apache', 'HPC', 'Zookeeper', 'OpenStack']

sum = 0
for dataset in datasets:
    sum += evaluateGA(dataset, f"logs/{dataset}/{dataset}_2k.log_structured.csv", f"results/1800_{dataset}_result.csv")

print(f"Average grouping accuracy: {sum/len(datasets)}")