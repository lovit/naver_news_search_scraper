## Install

Python 3 로 작성되었습니다. 아래의 패키지를 이용합니다.

- beautifulsoup4 >= 4.6.0
- requiests >= 2.14.2

설치는 git clone 으로 코드를 받거나 downloads 를 합니다.

## Usage

실행 코드는 Python 으로 py 파일을 실행합니다. naver_news_search_crawler 폴더로 이동합니다.

    python searching_news_comments.py --verbose --debug --comments

searching_news_comments.py 파일을 실행하면 output 폴더에 뉴스와 댓글이 저장됩니다. 이 파일은 몇 가지 arguments 를 제공합니다.

| argument name | default value | note |
| --- | --- | --- |
| --root_directory | ../output/ | 수집된 뉴스와 댓글의 저장 위치 |
| --begin_date | 2018-10-26 | yyyy-mm-dd 형식으로 입력되는 데이터 수집의 첫 날 |
| --end_date | 2018-10-26 | yyyy-mm-dd 형식으로 입력되는 데이터 수집의 마지막 날 |
| --sleep | 0.1 | 네이버 뉴스 사이트에 부하를 주지 않기 위한 여유시간. 단위는 초. 이 시간이 짧으면 네이버로부터 공격성 접근으로 인식되어 접속이 차단될 수 있습니다 |
| --header | None | news 파일과 저장 폴더의 이름입니다. 아래에서 자세히 이야기합니다 |
| --query_file | queries.txt | 질의어가 입력된 텍스트 파일. 한 줄에 하나의 단어를 입력합니다 |
| --debug | False | --debug 입력 시 True, 각 일자별로 3 페이지의 뉴스와 댓글만 수집합니다 |
| --verbose | False | --verbose 입력 시 True, 진행 상황을 자세히 보여줍니다|
| --comments | False | --comments 입력 시 True, 각 뉴스에 해당하는 댓글을 함께 수집합니다|

## Directory structure

기본 arguments 를 기준으로 설명합니다. 수집된 데이터의 기본 저장 위치는 ../output/ 입니다.

header 를 입력하면 output 폴더 아래에 header 의 이름으로 폴더가 생깁니다. diplomacy 폴더는 --header diplomacy 를 입력한 경우입니다. diplomacy 아래에는 query term 의 순서에 따라서 0 부터 폴더가 생성됩니다. 그 아래에 news 와 comments 폴더가 생성되며, news 폴더 아래에는 각 일자별 뉴스 (.txt) 와 뉴스의 인덱스 (.index) 파일이 생성됩니다. comments 에는 댓글이 존재하는 기사의 댓글이 tap 으로 분리되는 tsv 파일 형식으로 저장됩니다.

header 를 입력하지 않을 경우 스크립트를 실행시킨 시각 (초 단위까지)으로 폴더가 생성됩니다. 이때는 뉴스와 인덱스 파일에 header 가 붙지 않습니다.

    --| naver_news_search_crawler
    --| output
        --| diplomacy
            --| 0
                --| news
                    --| 2018-10-26_diplomacy.txt
                    --| 2018-10-26_diplomacy.index
                --| comments
                    --| 001-0010429592.txt
                    --| 001-0010429850.txt
                    --| ...
        --| 2018-10-29_18-52-27
            --| 0
                --| news
                    --| 2018-10-26.txt
                    --| 2018-10-26.index
                --| comments
                    --| 001-0010429592.txt
                    --| 001-0010429850.txt
                    --| ...


## News 파일 구조

`2018-10-26[_header].txt` 로 명명되어 있으며, 한 줄이 하나의 뉴스기사이고 한 뉴스기사 내 줄바꿈은 두 칸 띄어쓰기로 구분됩니다.

## Index 파일 구조

`2018-10-26[_header].index` 명명되어 있으며, 한 줄이 하나의 뉴스기사의 인덱스입니다. `2018-10-26[_header].txt` 파일과 줄 단위로 같은 기사를 지칭합니다.

index 파일은 네 가지 정보로 구성된 tap separated value (tsv) 형식입니다. 첫줄에 header 가 없습니다.

| column | example | note |
| --- | --- | --- |
| key | 052/2018/10/01/0001199008 | 언론사ID / yy / mm / dd / 기사ID |
| 카테고리 이름 (혹은 번호) | 104 | 104 번 뉴스 카테고리 |
| 기사 작성 시각 | 2018-10-01 23:52 | 혹은 최종 수정 시각. 때로 포멧이 일정하지 않은 경우가 있음 |
| 기사 제목 | . | 기사 제목 |

## Comments 파일 구조

001-0010429592.txt 은 10-26 에 작성된 (언론사=001, 뉴스기사=0010370550) 의 리뷰로 tap 구분으로 이뤄진 csv 파일 입니다.

이 파일의 첫줄은 column head 입니다.

| column | example | note |
| --- | --- | --- |
| comment_no | 1514778615 | 댓글 고유 아이디 |
| user_id_no | 6EVlK | 댓글 등록자 아이디의 해쉬값 |
| contents | 좋은 방향으로 얘기 잘 되었으면.. | 댓글 내용 |
| reg_time | 2018-10-28T23:41:26+0900 | 댓글 등록 시각 | 
| sympathy_count | 0 | 댓글 공감 수 |
| antipathy_count | 0 | 댓글 비공감 수 |
