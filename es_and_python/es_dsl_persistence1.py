from datetime import datetime

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document, Date, Integer, Keyword, Text
from elasticsearch_dsl.connections import connections


HOSTS = ['localhost:9200']
CONNECTION_ALIAS = 'dev'
es_client = Elasticsearch(HOSTS, timeout=5)
connections.add_connection(CONNECTION_ALIAS, es_client)


class Article(Document):
    title = Text(analyzer='snowball', fields={'raw': Keyword()})
    body = Text(analyzer='snowball')
    tags = Keyword()
    published_from = Date()
    lines = Integer()

    class Index:
        name = 'blog'
        settings = {
          "number_of_shards": 2,
        }
        using = CONNECTION_ALIAS

    def save(self, ** kwargs):
        self.lines = len(self.body.split())
        return super(Article, self).save(** kwargs)

    def is_published(self):
        return datetime.now() >= self.published_from


def main():
    # create the mappings in elasticsearch
    # Article.init()

    # create and save and article
    article = Article(meta={'id': 42}, title='Hello world!', tags=['test'])
    article.body = ''' looong text '''
    article.published_from = datetime.now()
    article.save()

    article = Article.get(id=42)
    print(article.is_published())

    # Display cluster health
    print(connections.get_connection(alias=CONNECTION_ALIAS).cluster.health())


if __name__ == '__main__':
    main()

