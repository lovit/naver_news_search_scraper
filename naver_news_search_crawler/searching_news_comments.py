import argparse
import os
from datetime import datetime
from search_crawler import SearchCrawler

def parse_query_file(query_file, begin_date, end_date):
    """
    query_file : str
        query.txt file path
    begin_date : str
        Default begin_date
    end_date : str
        Default end_date
    """
    with open(query_file, encoding='utf-8') as f:
        docs = [doc.strip().split() for doc in f]
    if not docs:
        raise ValueError('Query file must be inserted')
    args = []
    for i, cols in enumerate(docs):
        query = cols[0]
        outname = '%d'%i
        bd = begin_date
        ed = end_date

        if len(cols) == 2:
            out = cols[1]
        elif len(cols) == 4:
            bd = cols[2]
            ed = cols[3]
        args.append((query, outname, bd, ed))
    return args

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root_directory', type=str, default='../output/', help='news and comments root directory')
    parser.add_argument('--begin_date', type=str, default='2018-10-28', help='datetime yyyy-mm-dd')
    parser.add_argument('--end_date', type=str, default='2018-10-30', help='datetime yyyy-mm-dd')
    parser.add_argument('--sleep', type=float, default=0.1, help='Sleep time')
    parser.add_argument('--header', type=str, default=None, help='corpus file name header')
    parser.add_argument('--query_file', type=str, default='queries.txt', help='query file. a line a query')
    parser.add_argument('--debug', dest='DEBUG', action='store_true')
    parser.add_argument('--verbose', dest='VERBOSE', action='store_true')
    parser.add_argument('--comments', dest='GET_COMMENTS', action='store_true')

    args = parser.parse_args()
    root_directory = args.root_directory
    begin_date = args.begin_date
    end_date = args.end_date
    sleep = args.sleep
    header = args.header
    DEBUG = args.DEBUG
    VERBOSE = args.VERBOSE
    GET_COMMENTS = args.GET_COMMENTS

    now_strf = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    root_header = now_strf if header is None else header
    root_directory += '/%s/' % root_header

    query_file = args.query_file
    if not os.path.exists(query_file):
        raise ValueError('Query file are not found: {}'.format(query_file))

    scraping_args = parse_query_file(query_file, begin_date, end_date)
    for query, outname, bd, ed in scraping_args:
        directory = '{}/{}/'.format(root_directory, outname)
        if bd > ed:
            continue
        crawler = SearchCrawler(directory, VERBOSE, DEBUG, GET_COMMENTS, header, sleep)
        crawler.search(query, bd, ed)

if __name__ == '__main__':
    main()