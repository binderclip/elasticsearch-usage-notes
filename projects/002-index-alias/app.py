import datetime
import time

from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch.helpers import bulk
from elasticsearch_dsl import Document, Text, connections, Index, Keyword

HOSTS = ['localhost:9200']
CONNECTION_ALIAS = 'dev'
es_client = Elasticsearch(HOSTS, timeout=5)
connections.add_connection(CONNECTION_ALIAS, es_client)

DEFAULT_INDEX_SETTING = {
    "analysis": {
        "analyzer": {
        },
        "filter": {
        },
        "char_filter": {
        }
    }
}


class IndexMixin:
    """一些用到的 index 的操作，dsl 的 index 没有实现的功能，简单封装一下"""

    @classmethod
    def _generate_new_index_name(cls, alias):
        now = datetime.datetime.now()
        new_name = "{alias}_{time_str}".format(alias=alias, time_str=now.strftime("%Y%m%d_%H%M%S"))
        return new_name

    @classmethod
    def _get_index_names_by_alias(cls, alias):
        try:
            index_names = list(es_client.indices.get_alias(name=alias).keys())
        except NotFoundError:
            return None
        return index_names

    @classmethod
    def _delete_alias(cls, index_name, alias):
        es_client.indices.delete_alias(index=index_name, name=alias)

    @classmethod
    def _put_alias(cls, index_name, alias):
        es_client.indices.put_alias(index=index_name, name=alias)

    @classmethod
    def _change_alias(cls, remove_ops=[], add_ops=[]):
        body = {"actions": []}
        for remove_op in remove_ops:
            body["actions"].append({"remove": {"index": remove_op[0], "alias": remove_op[1]}})
        for add_op in add_ops:
            body["actions"].append({"add": {"index": add_op[0], "alias": add_op[1]}})
        es_client.indices.update_aliases(body=body)

    @classmethod
    def _create_index(cls, index_name):
        new_index = Index(index_name, using=CONNECTION_ALIAS)
        new_index.delete(ignore=[400, 404])
        new_index.create()
        return new_index

    @classmethod
    def _delete_index(cls, index_name):
        old_index = Index(index_name, using=CONNECTION_ALIAS)
        old_index.delete(ignore=[400, 404])

    @classmethod
    def new_index(cls, new_name=None, docs=None):
        """
        重新索引全部数据
        test: 等于 True 的话，不执行 _change_alias 和 _delete_index
        """
        alias = cls._index._name
        new_name = new_name or cls._generate_new_index_name(alias)

        cls._create_index(new_name)

        if docs:
            actions = []
            for doc in docs:
                d = doc.to_dict(include_meta=True)
                d['_index'] = new_name
                actions.append(d)
            bulk(es_client, actions)

        old_names = cls._get_index_names_by_alias(alias)
        if old_names:
            cls._change_alias(remove_ops=[(old_name, alias) for old_name in old_names], add_ops=[(new_name, alias)])
            for old_name in old_names:
                cls._delete_index(old_name)
        else:
            cls._change_alias(add_ops=[(new_name, alias)])


class Movie(Document, IndexMixin):
    title = Text(
        analyzer='ik_max_word',  # 建索引时用
        search_analyzer='ik_max_word',  # 搜索时用
        fields={'raw': Keyword()})

    class Index:
        name = 'movie'
        using = CONNECTION_ALIAS


def create_indices(docs=None):
    Movie.new_index(docs=docs)


def main():
    titles = ["肖申克的救赎", "霸王别姬", "这个杀手不太冷", "阿甘正传", "美丽人生", "泰坦尼克号", "千与千寻", "辛德勒的名单",
              "盗梦空间", "忠犬八公的故事", "机器人总动员", "三傻大闹宝莱坞", "海上钢琴师", "放牛班的春天", "楚门的世界",
              "大话西游之大圣娶亲", "星际穿越", "龙猫", "教父", "熔炉", "无间道", "疯狂动物城", "当幸福来敲门", "怦然心动",
              "触不可及" ]

    movie_docs = [Movie(title=title) for title in titles[1:]]
    create_indices(docs=movie_docs)

    time.sleep(1)

    # 搜索
    results = Movie.search().query("match", title='世界').execute()
    print(results.hits.total)
    for movie in results:
        print(movie.title, movie.meta.score)


if __name__ == '__main__':
    main()
