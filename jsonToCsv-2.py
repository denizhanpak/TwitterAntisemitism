#Written by Anurag Kumar and Denizhan Pak
import json
import sys
import csv
import argparse


def createCSV(path:str, out:str):
    with open(path, "r") as infile:
        to_write = []
        for data in infile:
            try:
                json_data = json.loads(data)
                id_ = json_data['id_str']
                user = json_data['user_screen_name']
                text = json_data['text']
                date = json_data['created_at']
                row = [id_, user, text, date]
                to_write.append(row)
            except Exception as e:
                pass

    with open("./" + out, "w") as outfile:
        csvwriter = csv.writer(outfile, delimiter=",", quotechar='"')
        csvwriter.writerow(["TweetID", "Username", "Text", "CreateDate"])
        for line in to_write:
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
