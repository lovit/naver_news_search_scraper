from .utils import get_soup

def get_press_list():
    def parse(link):
        oid = link['href'].split('oid=')[-1].split('&')[0]
        name = link.text
        return oid, name

    url = 'https://news.naver.com/main/officeList.nhn'
    soup = get_soup(url)
    links = soup.select('ul[class=group_list] a')
    press_list = [parse(link) for link in links]
    press_list = sorted(press_list, key=lambda x:int(x[0]))
    return press_list