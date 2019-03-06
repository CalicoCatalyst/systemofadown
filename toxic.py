import configparser

import praw
import argparse
import logging
import time
import sys
from googleapiclient import discovery
from googleapiclient.errors import HttpError


class MeasuringTool:

    def __init__(self, reddit, config):
        self._reddit = reddit
        self._config = config

    def measure_string_toxicity(self, string):
        text = str(string)

        API_KEY = self._config.get_google()
        service = discovery.build('commentanalyzer', 'v1alpha1', developerKey=API_KEY, cache_discovery=False)

        analyze_request = {
            'comment': {'text': text},
            'requestedAttributes': {'TOXICITY': {}}
        }

        response = service.comments().analyze(body=analyze_request).execute()

        raw_level = response['attributeScores']['TOXICITY']['summaryScore']['value']

        measurement = float(raw_level) * 100

        human_measurement = round(measurement)

        return measurement

    def check_toxicity(self, reddit, alimit=1000, username=None, thread=None):
        comments = []
        logging.info("Gathering Comments")
        if username is not None:
            for comment in reddit.redditor(username).comments.new(limit=alimit):
                print_progress(len(comments), alimit-1)
                comments.append(comment.body)
        elif thread is not None:
            submission = reddit.submission(url=thread)
            submission.comments.replace_more(limit=alimit)
            for comment in submission.comments.list():
                print_progress(len(comments), alimit-1)
                comments.append(comment.body)

        logging.info("%s Comments Found" % len(comments))

        toxic_comments = []

        for comment in comments:
            level = float(0)

            try:
                level = self.measure_string_toxicity(comment)
            except HttpError as error:
                print("Error - Skipping and moving on")
                pass

            sys.stdout.write("\rmeasured %s / %s" % (len(toxic_comments), len(comments)))
            sys.stdout.flush()
            toxic_comments.append(level)
            time.sleep(0.15)
        sys.stdout.write("\n")
        sys.stdout.flush()
        print('Toxicity rating: %s' % self.average(toxic_comments))

    def average(self, lst):
        return sum(lst) / len(lst)


class Configuration(object):

    def __init__(self, config_file):
        self._config = configparser.ConfigParser()
        self._config.read(config_file)
        self.configfile = self._config

    def auth_reddit_from_config(self):
        return (praw.Reddit(client_id=self._config['Reddit']['client_id'],
                            client_secret=self._config['Reddit']['client_secret'],
                            user_agent="Toxicity Measuring Tool"))

    def get_google(self):
        return self._config['Google']['key']


def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=25):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '+' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(description='Bot To Add Titles To Images')
    parser.add_argument('-d', '--debug', help='Enable Debug Logging', action='store_true')
    parser.add_argument('-un', '--username',help='Declare a username parse', action='store_true')
    parser.add_argument('-th', '--thread', help="Declare a Link parse", action="store_true")
    parser.add_argument('link', help='username or thread to check comments of')
    parser.add_argument('limit', help='Limit of comments to parse', type=int)

    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

    logging.debug('Debug Enabled')
    logging.getLogger('googleapiclient.discovery').setLevel(logging.CRITICAL)

    config = Configuration("config.ini")

    r = config.auth_reddit_from_config()

    processor = MeasuringTool(r, config)

    un = None
    th = None

    if args.thread:
        th = args.link
    else:
        un = args.link

    try:
        processor.check_toxicity(r, args.limit, username=un, thread=th)
        logging.info('Checking Complete, Exiting Program')
        exit(0)
    except KeyboardInterrupt:
        logging.debug("KeyboardInterrupt Detected, Cleaning up and exiting...")
        print("Cleaning up and exiting...")
        exit(0)


if __name__ == '__main__':
    main()
