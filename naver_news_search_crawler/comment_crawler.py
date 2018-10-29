import requests
import json
from bs4 import BeautifulSoup


def get_comments(news_url):
    base_url = ''.join(['https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=news&',
                    'templateId=view_politics&pool=cbox5&lang=ko&country=KR&objectId=news',
                    '{}%2C{}&pageSize={}&page={}&sort={}&initialize=true&useAltSort=true&indexSize=10'])
    
    (oid, aid) = _parse_oid_aid(news_url)    
    if oid == None or aid == None:
        return []
    
    n_comments = _n_comments(base_url.format(oid, aid, 10, 1, 'favorite'), news_url)
    max_page = round(n_comments/100 + 0.5)
    if max_page <= 0:
        return []
    
    comments = []
    headers = {'Referer':news_url}
    for page in range(1, max_page + 1):
        url = base_url.format(oid, aid, 100, page, 'favorite')
        response = _get_response(url, {'Referer':news_url})
        for comment_json in response.get('result', {}).get('commentList', []):
            try:
                comments.append(_parse_comment(comment_json))
            except:
                continue
    return comments
    
def _get_response(url, headers=None):
    try:
        if not headers:
            r = requests.get(url)
        else:
            r = requests.get(url, headers=headers)
        html = r.text
        html = html[10:-2]
        response = json.loads(html)
        return response
    except:
        return {}

def _parse_oid_aid(news_url):
    parts = news_url.split('?')[-1].split('&')
    (oid, aid) = (None, None)
    for part in parts:
        if 'oid=' in part:
            oid = part[4:]
        if 'aid=' in part:
            aid = part[4:]
    return oid, aid

def _n_comments(url, news_url):
    response = _get_response(url, {'Referer':news_url})
    n_comments = response.get('result', {}).get('count', {}).get('comment', 0)
    return n_comments

def _parse_comment(comment_json):
    antipathy_count = comment_json['antipathyCount']
    sympathy_count = comment_json['sympathyCount']
    comment_no = comment_json['commentNo']
    contents = comment_json['contents'].replace('\t', ' ').replace('\r', ' ').replace('\n', ' ')
    reg_time = comment_json['regTime']
    user_id_no = comment_json['userIdNo']
    return (comment_no, user_id_no, contents, reg_time, sympathy_count, antipathy_count)