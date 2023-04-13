import openai
import argparse
from modeltester import ModelTester

def main(args):
    # get a tester object with data
    openai.api_key = args.key
    print("Parsing " + args.dataset + " ...")

    tester = ModelTester(
                log_path = args.log_path,        # .log_structured_csv
                result_path=args.result_path,    # .result_csv
                map_path=args.map_path,          # .map_json
                dataset = args.dataset,       # HDFS, Spark, BGL, Windows, Linux, Andriod, Mac, Hadoop, HealthApp, OpenSSH, Thunderbird, Proxifier, Apache, HPC, Zookeeper, OpenStack
                emb_path = args.emb_path, # embedding path
                cand_ratio = args.cand_ratio,       # ratio of candidate set
                split_method = args.split_method,   # random or DPP
                warmup = args.warmup,               # warmup or not
                )

    tester.textModelBatchTest(model = args.model, 
                        model_name = args.model_name, 
                        max_token = args.max_token,       # token number in model response
                        limit = args.limit,         # number of logs for testing, <= 2000*(1-cand_ratio)
                        N = args.N,                  # number of examples in the prompt
                        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-key', type=str, help='openai key')
    parser.add_argument('--log_path', type=str, default='logs', help='log path')
    parser.add_argument('--result_path', type=str, default='results', help='result path')
    parser.add_argument('--map_path', type=str, default='maps', help='map path')
    parser.add_argument('--dataset', type=str, default='HDFS', help='dataset name')
    parser.add_argument('--emb_path', type=str, default='embeddings', help='embedding path')
    parser.add_argument('--cand_ratio', type=float, default=0.1, help='ratio of candidate set')
    parser.add_argument('--split_method', type=str, default='DPP', help='random or DPP')
    parser.add_argument('--warmup', type=bool, default=False, help='warmup or not')
    parser.add_argument('--model', type=str, default='curie', help='model name')
    parser.add_argument('--model_name', type=str, default='gptC', help='model name')
    parser.add_argument('--max_token', type=int, default=180, help='token number in model response, <= 180')
    parser.add_argument('--limit', type=int, default=1800, help='number of logs for testing, <= 2000*(1-cand_ratio)')
    parser.add_argument('--N', type=int, default=5, help='number of examples in the prompt')
    args = parser.parse_args()
    main(args)
