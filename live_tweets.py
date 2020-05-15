#Written by Anurag Kumar and Denizhan Pak

#This is a script used to randomly select live tweets from a folder containing
#a json dump of tweets (based on the Twitter API). Since whether a tweet is live 
#is checked using an https request for efficiency reservoir sampling is used.
import json, os, urllib, random, argparse 
import urllib.request

#This function will check if each tweet is live by attempting to connect to that
#tweet's page.The script then determines if the tweet is still live by comparing
#the URL that it is directed to to the URL that was given. If a tweet is live, 
#the return value will be 1.
def tweet_is_live(ID:str, username:str, verbose=False) -> bool:
    #creates the URL of the tweet from specified ID and username
    url = 'https://twitter.com/' + username + '/status/' + ID 
    if verbose:
        print("URL: " + url)
    try:
        page = urllib.request.urlopen(url) #contact the web page
        if ID in page.geturl(): #compare the final destination URL to the original
            #print(url + ' is live')
            return 1
        elif url == 'https://twitter.com/account/suspended': #detects if the user was suspended
            error = 'User Suspended'
            pass
        else: #print message if the final URL was not the same as the original. AKA redirected to another tweet.
            error = 'Redirect maybe removed'
            pass
    except urllib.error.HTTPError as e: #exception if web server returns an error
        error = 'HTTP Error'
        pass
    except urllib.error.URLError as e:
        error = 'URL Error'
        pass
    
    if verbose:
        print(error)
    
    return 0


#This function takes a path to a folder and a sample_size
#It returns a list of sample_size lines from all files in the folder
#randomly sampled.
def read_files(directory_path:str, sample_size:int, verbose:bool) -> list :
    folder = os.fsencode(directory_path)
    selected_sample = []
    counter = 0
    if verbose:
        print("Start reading files...")
    
    #Open argument directory
    for fileobject in os.listdir(folder): 
        filename = os.fsdecode(fileobject) 
        if "ex" in filename:
            if verbose:
                print("Reading file: " + filename)
            #Open file in directory and apply reservoir sampling
            with open(os.fsdecode(folder) + "/" + filename, "r") as f:
                for line in f:
                    if counter < sample_size:
                        selected_sample.append(line) 
                    else:
                        index = random.randrange(counter)
                        if index < sample_size:
                            selected_sample[index] = line
                    counter += 1
            if verbose:
                print(str(counter) + " lines read")
    return selected_sample

#This function takes a list of tweets in the standard json format
#and filters out dead tweets. It returns all live tweets in the 
#original list.
def live_tweets(dataset:list, verbose=False, vverbose=False) -> list:
    live_tweets = []
    counter = 0
    numb_live = 0
    numb_dead = 0
    
    for tweet in dataset:
        try:
            json_data = json.loads(tweet)
            
            #Case in which this is a retweet
            if "retweeted_status" in json_data:
                id_ = json_data['retweeted_status']['id_str']
                user = json_data['retweeted_status']['user_screen_name']
            #Case in which this is an original tweet
            else:
                id_, user = json_data['id_str'], json_data['user_screen_name']

            if tweet_is_live(id_,user, vverbose) == 1:
                live_tweets.append(tweet)
                numb_live += 1
            else:
                numb_dead += 1
            
            counter += 1
            if verbose:
                if counter % 200 == 0 or counter == len(tweet)-1:
                    print(counter," tweets checked.")
        except Exception as e:
            if verbose:    
                print(e)
            pass                  
    
    if verbose:
        print("numb_live = " + str(numb_live) + "\n numb_dead = " + str(numb_dead))
    return live_tweets
        
#This function writes a collection json files [data] to a file [name]
def writeFile(data:list, name:str, verbose=False):
    #Writing in the file
    with open(name, "w+") as outfile:
        for i in data:
            try:
                outfile.write(str(i) + "\n") 
            except Exception as e:
                if verbose:
                    print(e)
                pass
        
#This script works in 3 steps
#1) From a given folder [directory] containing collected tweets 
#(json formatted) generate a random sample of size [reservoir_size]
#2) Get a live random subset of the reservoir of size [sample_size].
#In the case where there are not enough live tweets all live
#tweets are returned.
#3)Write a sample file with name [sample_name]
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Generate a sub-sample of live tweets")
    
    parser.add_argument('directory', type=str, nargs=1, help="Directory containing json files")
    parser.add_argument('-rs', '--reservoir_size', type=int, nargs=1, help="Number of tweets to check if live (default=2000)", default=[2000])
    parser.add_argument('-ss', '--sample_size', type=int, nargs=1, help="Size of generated sample (default=500)", default=[500])
    parser.add_argument('-v', '--verbose', action="store_true", help="Add additional output statements",default=False)
    parser.add_argument('-vv', '--very_verbose', action="store_true", help="Add additional output statements per tweet checked",default=False)
    parser.add_argument('-o', '--output_file', type=str, nargs=1, help="Name for output file to write sample to",default=["placeholder"])

    args = parser.parse_args()
    directory_path = args.directory[0]
    reservoir_size = args.reservoir_size[0]
    sample_size = args.sample_size[0]
    verbose = args.verbose
    vverbose = args.very_verbose
    output = args.output_file[0]

    if output == "placeholder":
        output = str(sample_size) + "sample.json"
    if vverbose: verbose = True

    tweets_to_sample = read_files(directory_path, reservoir_size, verbose)
    
    if verbose:
        print("Filtering live tweets....")
    
    tweets = live_tweets(tweets_to_sample, verbose, vverbose)
    try:
        sampling = random.sample(tweets, sample_size)
    except:
        print("Not enough tweets using all live.")
    writeFile(sampling, output, verbose)
