import argparse
import glob
import os

def merge(inputs, output, header=None):
    with open(output, 'w', encoding='utf-8') as fo:
        if header is not None:
            fo.write('{}\n'.format(header))
        for inp in inputs:
            if header is None:
                prefix = ''
            else:
                prefix = inp.split('/')[-1][:-4] + '\t'
            with open(inp, encoding='utf-8') as fi:
                if header is not None:
                    next(fi)
                for line in fi:
                    fo.write('{}{}'.format(prefix, line))
    print('merge {} files to {}'.format(len(inputs), output))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', type=str, default='../output/', help='news and comments root directory')

    args = parser.parse_args()
    directory = args.directory

    fileprefix = directory[:-1] if directory[-1] == '/' else directory
    corpus_paths = sorted(glob.glob('{}/news/*.txt'.format(directory)))
    corpus_file = '{}.txt'.format(fileprefix)
    merge(corpus_paths, corpus_file)

    index_paths = sorted(glob.glob('{}/news/*.index'.format(directory)))
    index_file = '{}.index'.format(fileprefix)
    merge(index_paths, index_file)

    header = 'press-article comment_no user_id_no contents reg_time sympathy_count antipathy_count'.replace(' ', '\t')

if __name__ == '__main__':
    main()
