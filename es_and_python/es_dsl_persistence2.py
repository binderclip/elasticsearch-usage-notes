from datetime import datetime

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch_dsl import Document, Date, Nested, Boolean, \
    analyzer, InnerDoc, Completion, Keyword, Text, connections


HOSTS = ['localhost:9200']
CONNECTION_ALIAS = 'dev'
INDEX = 'blog'
es_client = Elasticsearch(HOSTS, timeout=5)
connections.add_connection(CONNECTION_ALIAS, es_client)


html_strip = analyzer('html_strip',
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)


class Comment(InnerDoc):
    author = Text(fields={'raw': Keyword()})
    content = Text(analyzer='snowball')
    created_at = Date()

    def age(self):
        return datetime.now() - self.created_at


class Post(Document):
    title = Text()
    title_suggest = Completion()
    created_at = Date()
    published = Boolean()
    category = Text(
        analyzer=html_strip,
        fields={'raw': Keyword()}
    )

    comments = Nested(Comment)

    class Index:
        name = INDEX
        using = CONNECTION_ALIAS

    def add_comment(self, author, content):
        self.comments.append(
          Comment(author=author, content=content, created_at=datetime.now()))

    def save(self, ** kwargs):
        self.created_at = datetime.now()
        return super().save(** kwargs)


def init():
    print('=== init ===')
    Post.init()


def create_and_save():
    print('=== create_and_save ===')
    post = Post(meta={'id': 25}, title='Hello ES!')
    post.created_at = datetime.now()
    post.published = False
    post.category = 'es dev tutorial'
    post.add_comment(author='clip', content='good')
    post.save()


def update():
    print('=== update ===')
    post = Post.get(id=25)
    post.update(published=True)


def get():
    print('=== get ===')
    post = Post.get(id=25)
    print(post.comments, post.published)

def get_none():
    print('=== get_none ===')
    Post.get(id='not-in-es')  # elasticsearch.exceptions.NotFoundError: TransportError(404, '{"_index":"blog","_type":"doc","_id":"not-in-es","found":false}')
    post = Post.get(id='not-in-es', ignore=404)
    print(post)


def get_multi():
    print('=== get_multi ===')
    posts = Post.mget([25, 26])
    print(posts)


def delete():
    print('=== delete ===')
    post = Post.get(id=25)
    post.delete()


def bulk_create():
    print('=== bulk_create ===')
    posts = [
        Post(meta={'id': 10}, title='Get Started with ES 01'),
        Post(meta={'id': 11}, title='Get Started with ES 02'),
    ]
    actions = (doc.to_dict(include_meta=True) for doc in posts)
    # es_client.bulk(actions)  # not work
    bulk(es_client, actions)


def bulk_delete():
    print('=== bulk_delete ===')
    post_ids = [10, 11]
    actions = []
    for post_id in post_ids:
        actions.append({
            "_op_type": "delete",
            "_index": Post._index._name,
            "_type": Post._doc_type.mapping.properties._name,
            "_id": str(post_id)
        })
    errors = bulk(es_client, actions=actions)
    return not errors


def search():
    print('=== search ===')
    s = Post.search()
    s = s[0:1]
    s = s.filter('term', published=True).query('match', title='Hello')
    results = s.execute()
    for post in results:
        print(post.meta.score, post.title)
    print(f'total: {results.hits.total}')


def main():
    # init()
    # create_and_save()
    # update()
    # get()
    # get_none()
    # get_multi()
    # delete()
    # bulk_create()
    # bulk_delete()
    search()
    print(Post._doc_type.mapping.properties._name)


if __name__ == '__main__':
    main()

# https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html
