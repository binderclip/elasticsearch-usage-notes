import datetime
import time

from elasticsearch import Elasticsearch
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


def get_connection(using):
    return connections.connections.get_connection(using)


class IndexMixin:
    """一些用到的 index 的操作，dsl 的 index 没有实现的功能，简单封装一下"""

    @classmethod
    def _generate_new_index_name(cls, alias):
        now = datetime.datetime.now()
        new_name = "{alias}_{time_str}".format(alias=alias, time_str=now.strftime("%Y%m%d_%H%M%S"))
        return new_name

    @classmethod
    def _get_index_name_by_alias(cls, alias):
        index_names = get_connection(cls._doc_type.using).indices.get_alias(name=alias).keys()
        if not len(index_names) == 2:
            return None
        return index_names[0]

    @classmethod
    def _delete_alias(cls, index_name, alias):
        get_connection(cls._doc_type.using).indices.delete_alias(index=index_name, name=alias)

    @classmethod
    def _put_alias(cls, index_name, alias):
        get_connection(cls._doc_type.using).indices.put_alias(index=index_name, name=alias)

    @classmethod
    def _change_alias(cls, remove_ops=[], add_ops=[]):
        body = {"actions": []}
        for remove_op in remove_ops:
            body["actions"].append({"remove": {"index": remove_op[0], "alias": remove_op[1]}})
        for add_op in add_ops:
            body["actions"].append({"add": {"index": add_op[0], "alias": add_op[1]}})
        get_connection(cls._doc_type.using).indices.update_aliases(body=body)

    @classmethod
    def _create_index(cls, index_name):
        new_index = Index(index_name)
        new_index.delete(ignore=[400, 404])
        new_index.settings(index=DEFAULT_INDEX_SETTING)
        new_index.create()
        return new_index

    # @classmethod
    # def index_data(cls, index):
    #
    @classmethod
    def re_index(cls, new_name=None):
        """
        重新索引全部数据
        test: 等于 True 的话，不执行 _change_alias 和 _delete_index
        """
        alias = cls._doc_type.index
        new_name = new_name or cls._generate_new_index_name(alias)

        new_index = cls._create_index(new_name)

        old_name = cls._get_index_name_by_alias(alias)
        if old_name:
            cls._change_alias()
        old_name = cls._get_index_name_by_alias(alias)
        if old_name:
            cls._change_alias(remove_ops=[(old_name, alias), (new_name, tmp_new_alias)], add_ops=[(new_name, alias)])
        else:
            cls._change_alias(remove_ops=[(new_name, tmp_new_alias)],
                              add_ops=[(new_name, alias)])

        cls._delete_index(old_name)


class Movie(Document):
    title = Text(
        analyzer='ik_max_word',  # 建索引时用
        search_analyzer='ik_max_word',  # 搜索时用
        fields={'raw': Keyword()})

    class Index:
        name = 'movie'
        using = CONNECTION_ALIAS


def _create_index(index_name):
    new_index = Index(index_name, using=CONNECTION_ALIAS)
    new_index.delete(ignore=[400, 404])
    new_index.settings(index=DEFAULT_INDEX_SETTING)
    new_index.create()


def create_indices():
    model = Movie
    _create_index(model._index._name)
    model.init()  # create mapping


def main():
    create_indices()

    titles = ["肖申克的救赎", "霸王别姬", "这个杀手不太冷", "阿甘正传", "美丽人生", "泰坦尼克号", "千与千寻", "辛德勒的名单",
              "盗梦空间", "忠犬八公的故事", "机器人总动员", "三傻大闹宝莱坞", "海上钢琴师", "放牛班的春天", "楚门的世界",
              "大话西游之大圣娶亲", "星际穿越", "龙猫", "教父", "熔炉", "无间道", "疯狂动物城", "当幸福来敲门", "怦然心动",
              "触不可及" ]
    # 创建数据
    Movie(title=titles[0]).save()

    # 批量创建数据
    movie_docs = [Movie(title=title) for title in titles[1:]]
    actions = (doc.to_dict(include_meta=True) for doc in movie_docs)
    bulk(es_client, actions)

    time.sleep(1)

    # 搜索
    results = Movie.search().query("match", title='世界').execute()
    print(results.hits.total)
    for movie in results:
        print(movie.title, movie.meta.score)


if __name__ == '__main__':
    main()
