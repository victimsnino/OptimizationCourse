from common import *
import argparse
import os
import ntpath

def list_of_input_and_answers_in_folder(folder):
    result = []
    for filename in os.listdir(folder):
        if not filename.endswith('.clq'):
            continue

        basename = filename.split('.clq')[0]
        answer_file = folder+'\\'+basename+'.txt'
        if not os.path.isfile(answer_file):
            continue
        
        result.append([folder+'\\'+filename, answer_file])
    return result

 
parser = argparse.ArgumentParser()
parser.add_argument('--folder', required=True, type=str,
                    help='Path to folder with examples of cliques')
args = parser.parse_args()

files = list_of_input_and_answers_in_folder(args.folder)
for input, answer in files:
    check_model_for(input, answer)