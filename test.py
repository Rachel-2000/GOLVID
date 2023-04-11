import sys
import openai
from modeltest import ModelTester

# command line format: python test.py --raw_log_path --groundtruth_path -- model --token_limt --API_key
def main():
    # get a tester object with data
    openai.api_key = sys.argv[5]
    tester = ModelTester(
                raw_log_path = sys.argv[1], 
                groundtruth_path = sys.argv[2], 
                warmup = False)

    tester.chatModelBatchTest(
                  model = sys.argv[3],
                  model_name = "test",
                  limit = sys.argv[4])

if __name__ == "__main__":
    main()
