from datetime import datetime

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document, Date, Nested, Boolean, \
    analyzer, InnerDoc, Completion, Keyword, Text, connections


HOSTS = ['localhost:9200']
CONNECTION_ALIAS = 'dev'
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
        name = 'blog'
        using = CONNECTION_ALIAS

    def add_comment(self, author, content):
        self.comments.append(
          Comment(author=author, content=content, created_at=datetime.now()))

    def save(self, ** kwargs):
        self.created_at = datetime.now()
        return super().save(** kwargs)


def main():
    # init
    # Post.init()

    # create and save
    # post = Post(meta={'id': 25}, title='Hello ES!')
    # post.created_at = datetime.now()
    # post.published = False
    # post.category = 'es dev tutorial'
    # post.add_comment(author='clip', content='good')
    # post.save()

    # update
    # post = Post.get(id=25)
    # post.update(published=True)

    # get
    # post = Post.get(id=25)
    # print(post.comments, post.published)

    # get none
    # Post.get(id='not-in-es')  # elasticsearch.exceptions.NotFoundError: TransportError(404, '{"_index":"blog","_type":"doc","_id":"not-in-es","found":false}')
    # post = Post.get(id='not-in-es', ignore=404)
    # print(post)

    # get multi
    # posts = Post.mget([25, 26])
    # print(posts)

    # delete
    # post = Post.get(id=25)
    # post.delete()

    # search
    s = Post.search()
    s = s.filter('term', published=True).query('match', title='Hello')
    results = s.execute()
    for post in results:
        print(post.meta.score, post.title)
    if not results:
        print('no search results')


if __name__ == '__main__':
    main()

