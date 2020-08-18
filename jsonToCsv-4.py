#Written by Anurag Kumar and Denizhan Pak
import json
import sys
import csv
import argparse
import re
from langdetect import detect_langs
from langdetect import DetectorFactory
DetectorFactory.seed = 0

def remove_pattern(input_txt, pattern):
    r = re.findall(pattern, input_txt)
    for i in r:
        input_txt = re.sub(i, '', input_txt)

    return input_txt
def clean_text(tweet):
    tweet = re.sub(r"RT", "", str(tweet))
    tweet = re.sub(r"http\S+", "", str(tweet))
    additional = ['rt', 'rts', 'retweet']
    return tweet


def detectlanguages(text):
    '''
    This method checks all the different languages present in the text and likewise gives us the result.
    If we detect the present of english language then we say the tweet is in english.
    :param text: Tweet Text
    :return: Boolean value
    '''
    text = clean_text(text)
    text = text.replace('\n', " ")
    ans = (map(str, detect_langs(text)))
    for i in ans:
        if i.split(":")[0] == 'en':
            return True
    return False


def createCSV(path : str, out : str):
    with open(path, "r", encoding='utf-8') as infile:
        to_write = []
        to_not_write = []
        c = 0
        for data in infile:
            if data == '\n':
                continue
            try:
                json_data = json.loads(data)

                text = json_data['text']

                id_ = json_data['id_str']
                user = json_data['user_screen_name']

                date = json_data['created_at']
                row = [id_, user, text, date]

                if detectlanguages(text):
                    to_write.append(row)
                else:
                    to_not_write.append(row)
            except Exception as e:
                print(e, data)
        print(c)

    # this is the output to the english file
    with open("./" + out, "w", newline='', encoding='utf-8') as outfile:
        csvwriter = csv.writer(outfile, delimiter=",", quotechar='"')
        csvwriter.writerow(["TweetID", "Username", "Text", "CreateDate"])
        for line in to_write:
            csvwriter.writerow(line)
    # this is the out put to the non-english file
    with open("./" + "non-eng.csv", "w", newline='', encoding='utf-8') as outfile:
        csvwriter = csv.writer(outfile, delimiter=",", quotechar='"')
        csvwriter.writerow(["TweetID", "Username", "Text", "CreateDate"])
        for line in to_not_write:
            csvwriter.writerow(line)
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Create a csv file from standard twitter json format")

    parser.add_argument("files", type=str, nargs='+',
                        help="File or files containing tweets in json format")
    parser.add_argument("-o", "--output", type=str, nargs='+', default=["sample.csv"],
                        help="""Name or names for output file. Will put numbers before
                        last given if less output names than input names default=[number]sample.csv""")

    args = parser.parse_args()
    numb_in = len(args.files)
    numb_out = len(args.output)

    if numb_out < numb_in:
        new_paths = []
        for i in range(numb_in - numb_out):
            new_path = str(i+1) + args.output[-1]
            new_paths.append(new_path)
        args.output += new_paths

    for path, out in zip(args.files, args.output):
        print(path, out)
        createCSV(path, out)
