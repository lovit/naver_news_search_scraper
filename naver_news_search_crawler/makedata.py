import argparse
from collections import defaultdict
from datetime import datetime
from glob import glob
import os
import zipfile


def convert_str_date_to_datetime(string_date):
    try:
        return datetime.strptime(string_date, '%Y-%m-%d')
    except Exception as e:
        raise ValueError('Failed to Convert String to Datetime %s' % str(e))

def date_match(begin, end, date):
    return begin <= date <= end

def path_date_match(begin, end, path):
    date = path.split('/')[-1][:10]
    date = convert_str_date_to_datetime(date)
    return date_match(begin, end, date)

def group_by_datetime(paths, monthly=True):
    key_to_path = defaultdict(lambda: [])
    for path in paths:
        if monthly:
            key = path.split('/')[-1][:7]
        else:
            key = path.split('/')[-1][:10]
        key_to_path[key].append(path)
    return dict(key_to_path)

def make_news_data(scrap_directory, output_directory, begin, end, monthly, selected_queries):
    scrap_directory = os.path.abspath(scrap_directory)
    output_directory = os.path.abspath(output_directory)
    query_dirs = sorted(glob('{}/*'.format(scrap_directory)))
    if selected_queries is not None:
        query_dirs = [p for p in query_dirs if p.split('/')[-1] in selected_queries]

    for query_dir in query_dirs:
        source_paths = sorted(glob('{}/news/*'.format(query_dir)))
        source_paths = [p for p in source_paths if path_date_match(begin, end, p)]
        zipname_paths = group_by_datetime(source_paths, monthly)

        for zipname, paths in sorted(zipname_paths.items()):
            zippath = '{}/news/{}.zip'.format(query_dir, zipname)
            zippath = zippath.replace(scrap_directory, output_directory, 1)
            dirname = os.path.dirname(zippath)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            with zipfile.ZipFile(zippath, 'w') as zipf:
                for file in paths:
                    zipf.write(file, os.path.basename(file), compress_type=zipfile.ZIP_DEFLATED)
            print('compressed {}'.format(zippath))

def make_comment_data(scrap_directory, output_directory, begin, end, monthly, selected_queries):
    scrap_directory = os.path.abspath(scrap_directory)
    output_directory = os.path.abspath(output_directory)
    query_dirs = sorted(glob('{}/*'.format(scrap_directory)))
    if selected_queries is not None:
        query_dirs = [p for p in query_dirs if p.split('/')[-1] in selected_queries]

    for query_dir in query_dirs:
        source_paths = sorted(glob('{}/comments/*'.format(query_dir)))
        source_paths = [p for p in source_paths if path_date_match(begin, end, p)]
        zipname_paths = group_by_datetime(source_paths, monthly)

        for zipname, paths in sorted(zipname_paths.items()):
            zippath = '{}/comments/{}.zip'.format(query_dir, zipname)
            zippath = zippath.replace(scrap_directory, output_directory, 1)
            dirname = os.path.dirname(zippath)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            with zipfile.ZipFile(zippath, 'w') as zipf:
                for date_dir in paths:
                    date_dir = os.path.abspath(date_dir)
                    files = glob(date_dir + '/*.txt')
                    for file in files:
                        zipf.write(file, '/'.join(file.split('/')[-2:]), compress_type=zipfile.ZIP_DEFLATED)
            print('compressed {}'.format(zippath))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scrap_directory', type=str, default='./', help='JSON storage directory')
    parser.add_argument('--output_directory', type=str, default='./', help='Petitions archive directory')
    parser.add_argument('--begin_date', type=str, default='2013-01-01', help='Begin data yyyy-mm-dd format')
    parser.add_argument('--end_date', type=str, default='2018-08-01', help='End data yyyy-mm-dd format')
    parser.add_argument('--queries', type=str, nargs='*', default=None, help='Selected directories')
    parser.add_argument('--comments', dest='comments', action='store_true')
    parser.add_argument('--monthly', dest='monthly', action='store_true', help='A compressed file for a month')

    args = parser.parse_args()
    scrap_directory = args.scrap_directory
    output_directory = args.output_directory
    begin_date = convert_str_date_to_datetime(args.begin_date)
    end_date = convert_str_date_to_datetime(args.end_date)
    queries = args.queries
    if queries is not None:
        queries = set(queries)
    comments = args.comments
    monthly = args.monthly

    make_news_data(scrap_directory, output_directory, begin_date, end_date, monthly, queries)
    if comments:
        make_comment_data(scrap_directory, output_directory, begin_date, end_date, monthly, queries)

if __name__ == '__main__':
    main()
