import argparse
from datetime import datetime
from search_crawler import SearchCrawler

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
    try:
        with open(query_file, encoding='utf-8') as f:
            queries = [query.strip() for query in f]
            queries = [query for query in queries if query]
    except:
        raise ValueError('Query file are not found: {}'.format(query_file))

    for query_idx, query in enumerate(queries):
        directory = '{}/{}/'.format(root_directory, query_idx)
        crawler = SearchCrawler(directory, VERBOSE, DEBUG, GET_COMMENTS, header, sleep)
        crawler.search(query, begin_date, end_date)

if __name__ == '__main__':
    main()