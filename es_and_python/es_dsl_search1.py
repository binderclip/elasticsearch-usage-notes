import datetime

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document, Text, connections, Date
from elasticsearch_dsl.query import MultiMatch, Range

HOSTS = ['localhost:9200']
CONNECTION_ALIAS = 'dev'
es_client = Elasticsearch(HOSTS, timeout=5)
connections.add_connection(CONNECTION_ALIAS, es_client)


class Post(Document):
    title = Text()
    content = Text()
    post_time = Date()

    class Index:
        name = 'post'
        using = CONNECTION_ALIAS


def create_data():
    print('=== create_data ===')
    Post(title='黄章全力打造的魅族16，能帮魅族找回失去的一年吗？',
         content="本文来自36氪魅族终究是黄章的魅族，他准备亲自下场拯救这个属于自己的品牌。"
                 "8月8日下午，魅友终于等来了由魅族创始人兼CEO黄章自称“全力打造”的魅族16系列。",
         post_time=datetime.datetime(2018, 8, 9)).save()
    Post(title='为16系列让路 魅族15全系降价：1398元起售',
         content='8月8日下午，魅族16系列旗舰正式发布。价格方面，魅族16th 6GB+64GB版售价2698元，6GB+128GB版售价2998元，'
                 '8GB+128GB版售价3298元。魅族16th Plus 6GB+128GB售价3198元，8GB+128GB售价3498元，8GB+256GB版售价3998元。'
                 '同时魅族科技高级副总裁李楠宣布，魅族15系列价格下调。',
         post_time=datetime.datetime(2018, 8, 8)).save()
    Post(title='少数派「全面屏」，我心中的魅族15',
         content="我没有想过魅族会如此艰难，曾经的意气风发到现如今节节败退，上一代旗舰PRO 7寻求变化抵不过全面屏的浪潮，"
                 "高端路受阻，造就连锁反应导致市场份额急剧萎缩，现在的魅族正处多事之秋。从MX3开始喜欢上魅族，止于PRO 7，"
                 "三年之秋，虽已离开，听到身边不少人把魅族归为国产手机中的“其他”，心中难免有些酸楚。好在15周年之际，"
                 "魅族重整旗鼓带来了全新的魅族15系列产品，高中低端全面布局。经过大半年的预热，你很难不关注，"
                 "尽管最后来一句小试牛刀，但我依旧在这款产品上看到了很多诚意。",
         post_time=datetime.datetime(2018, 5, 20)).save()


def search_with_multi_match():
    print('''=== search_with_multi_match ===''')
    s = Post.search()
    # q = MultiMatch(query='魅族 16', fields=['title', 'content'])
    q = MultiMatch(query='魅族 16', fields=['title^3', 'content'])    # ^x 提高几倍的权重
    s = s.query(q)
    results = s.execute()
    for post in results:
        print(post.meta.score, post.title)
    print(f'total: {results.hits.total}')


def search_with_filter():
    print('''=== search_with_filter ===''')
    s = Post.search()
    q = Range(post_time={'gte': datetime.datetime(2018, 8, 7), 'lt': datetime.datetime(2018, 8, 9)})
    s = s.query(q)
    q = MultiMatch(query='魅族 16', fields=['title^3', 'content'])    # ^x 提高几倍的权重
    s = s.query(q)
    results = s.execute()
    for post in results:
        print(post.meta.score, post.title)
    print(f'total: {results.hits.total}')


def main():
    # create_data()
    # search_with_multi_match()
    search_with_filter()


if __name__ == '__main__':
    main()

# https://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html#queries
# https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-multi-match-query.html#query-dsl-multi-match-query
# https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-range-query.html
