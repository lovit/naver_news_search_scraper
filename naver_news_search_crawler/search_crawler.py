import re
import os
import time
from comment_crawler import get_comments
from news_crawler import scrap
from datetime import datetime, timedelta
from utils import check_dir
from utils import convert_datetime_to_str
from utils import convert_str_date_to_datetime
from utils import get_soup
from utils import get_path
from utils import url_encode


def get_article_urls(query, start_date, end_date=None, verbose=True, debug=True):
    if end_date == None:
        end_date = start_date

    search_result_url = _get_search_result_url(query, start_date, end_date)
    num_articles = _parse_article_num(search_result_url)
    if verbose:
        print('Search From %s' % search_result_url)
        print('Total Article Numbers: {} ({} ~ {}, {})'.format(num_articles, start_date, end_date, query))

    urls = _extract_urls_from_search_result(
        search_result_url, num_articles, verbose, debug)
    return urls

def get_article_num(query, start_date, end_date=None):
    if end_date == None:
        end_date = start_date
    search_result_url = _get_search_result_url(query, start_date, end_date)
    return _parse_article_num(search_result_url)

def _parse_article_num(search_result_url):
    try:
        soup = get_soup(search_result_url)
        if not soup:
            return 0
        result_header_text = soup.select('div[class=section_head] div[class^=title_desc] span')
        if not result_header_text:
            return 0
        result_header_text = result_header_text[0].text
        result_header_text = re.findall('[,\\d]+건', result_header_text)[0]
        result_header_text = re.sub(',', '', result_header_text) # Remove Comma
        num_articles = int(result_header_text[:-1])
        return num_articles

    except Exception as e:
        raise ValueError('Failed to get total number of articles %s' % str(e))

def _get_search_result_url(query, start_date, end_date):
        url_prefix = 'https://search.naver.com/search.naver?where=news&query={0}&sm=tab_opt&sort=0&photo=0&field=0&reporter_article=&pd=3&ds={1}&de={2}'
        start_date_ = start_date.replace('-', '.')
        end_date_ = end_date.replace('-', '.')
        search_result_url = url_prefix.format(url_encode(query), start_date_, end_date_)
        return search_result_url

def _article_num_to_page_num(num_articles):
    num_pages = num_articles // 10
    if num_articles % 10 != 0:
        num_pages += 1
    return num_pages

def _extract_urls_from_search_result(search_result_url, num_articles, verbose=True, debug=True):
    urls = set()
    num_pages = _article_num_to_page_num(num_articles)
    page = 0
    for page in range(num_pages):
        urls_in_page = _parse_urls_from_page(search_result_url, page)
        urls.update(urls_in_page)
        # Print Status
        if verbose and page % 5 == 0:
            print('  .. extract urls: page= {}, #urls= {}'.format(page, len(urls)))
        if debug and page >= 3:
            break
    if verbose:
        print('  .. extract urls: page= {}, #urls= {}'.format(page, len(urls)))

    return urls

def _parse_urls_from_page(base_url, page):

    url_patterns = ('a[href^="https://news.naver.com/main/read.nhn?"]',
            'a[href^="https://entertain.naver.com/main/read.nhn?"]',
            'a[href^="https://sports.news.naver.com/sports/index.nhn?"]',
            'a[href^="https://news.naver.com/sports/index.nhn?"]')

    urls_in_page = set()
    page_url = '{}&start={}&refresh_start=0'.format(base_url, 1 + 10*(page-1))
    soup = get_soup(page_url)
    if not soup:
        return urls_in_page
    try:
        article_blocks = soup.select('ul[class=type01]')[0]
        for pattern in url_patterns:
            article_urls = [link['href'] for link in article_blocks.select(pattern)]
            urls_in_page.update(article_urls)
    except Exception as e:
        raise ValueError('Failed to extract urls from page %s' % str(e))

    return urls_in_page

class SearchCrawler:
    def __init__(self, root, verbose, debug, comments, header=None, sleep=0.03):
        self.root = root
        self.verbose = verbose
        self.debug = debug
        self.comments = comments
        if header is None:
            header = ''
        self.header = header
        self.header_strf = '' if not header else '_' + header
        self.sleep = sleep

    def search(self, query, start_date, end_date=None):
        """start_date: str
               ex) 2017-05-01
        """
        if end_date == None:
            end_date = start_date

        start_date = convert_str_date_to_datetime(start_date)
        end_date = convert_str_date_to_datetime(end_date)

        for i in range((end_date - start_date).days + 1):
            scrap_date = start_date + timedelta(days=i)
            scrap_date = convert_datetime_to_str(scrap_date)
            year, month, date = scrap_date.split('-')
            urls = get_article_urls(query, scrap_date,
                scrap_date, verbose=self.verbose, debug=self.debug)

            docs = []
            indexs = []
            comments = []

            for i, url in enumerate(urls):
                if self.verbose and i % 50 == 0:
                    print('\r  - scrapping {} / {} news'.format(i+1, len(urls)), end='')
                try:
                    json_dict = scrap(url)
                    content = json_dict.get('content', '')
                    if not content:
                        continue
                    index = '{}\t{}\t{}\t{}'.format(
                        get_path(json_dict['oid'], year, month, date, json_dict['aid']),
                        json_dict.get('sid1',''),
                        json_dict.get('writtenTime', ''),
                        json_dict.get('title', '')
                    )
                    docs.append(content.replace('\n', '  ').replace('\r\n', '  ').strip())
                    indexs.append(index)
                    if self.comments:
                        comments.append(get_comments(url))
                    time.sleep(self.sleep)
                except Exception as e:
                    print('Exception: {}\n{}'.format(url, str(e)))
                    continue

            if self.verbose:
                print('\r  .. search crawler saved {} articles in {} on {}\n\n'
                              .format(len(urls), len(urls), year+month+date))

            if not docs:
                continue

            self._save_news_as_corpus(scrap_date, docs, indexs)
            if self.comments:
                self._save_comments(scrap_date, indexs, comments)

        if self.verbose:
            print('Search Crawling For Query [{}] Time Between [{}] ~ [{}] Finished'
                  .format(query, start_date, end_date))

        return True

    def _save_news_as_corpus(self, scrap_date, docs, indexs):
        corpus_path = '{}/news/{}{}.txt'.format(self.root, scrap_date, self.header_strf)
        index_path = '{}/news/{}{}.index'.format(self.root, scrap_date, self.header_strf)
        check_dir(corpus_path)

        with open(corpus_path, 'w', encoding='utf-8') as f:
            for doc in docs:
                f.write('{}\n'.format(doc.strip()))
        with open(index_path, 'w', encoding='utf-8') as f:
            for index in indexs:
                f.write('{}\n'.format(index))

    def _save_comments(self, scrap_date, indexs, comments):
        def comment_filename(index):
            oid, _, _, _, aid = index.split('\t')[0].split('/')
            return '{}-{}'.format(oid, aid)

        columns = 'comment_no user_id_no contents reg_time sympathy_count antipathy_count'.replace(' ', '\t')

        dirname = '{}/comments/{}/'.format(self.root, scrap_date)
        dirname = os.path.abspath(dirname)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        for comments_, index in zip(comments, indexs):
            if not comments_:
                continue
            filename = comment_filename(index)
            path = '{}/{}.txt'.format(dirname, filename)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(columns+'\n')
                for comment in comments_:
                    comment_strf = '\t'.join(str(v) for v in comment)
                    f.write('{}\n'.format(comment_strf))