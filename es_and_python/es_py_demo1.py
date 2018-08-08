from elasticsearch import Elasticsearch


INDEX_NAME = 'novels'


def create_an_index(es):
    response = es.indices.create(index=INDEX_NAME)
    print(response)


def add_documents(es):
    author1 = {"name": "Sidney Sheldon", "novels_count": 18}
    resp = es.index(index=INDEX_NAME, doc_type="authors", body=author1, id=1)
    print(resp)

    author2 = {"name": "Charles Dickens", "novels_count": 16}
    resp2 = es.index(index=INDEX_NAME, doc_type="authors", body=author2, id=2)
    print(resp2)

    genre1 = {"name": "Romance", "interesting": "yes"}
    resp3 = es.index(index=INDEX_NAME, doc_type="authors", body=genre1)
    print(resp3)

    genre2 = {"name": "Sci-fi", "interesting": "maybe"}
    resp4 = es.index(index=INDEX_NAME, doc_type="authors", body=genre2)
    print(resp4)


def retrieving_documents(es):
    resp = es.get(index=INDEX_NAME, doc_type="authors", id=1)
    print(resp)
    resp2 = es.get(index=INDEX_NAME, doc_type="authors", id=2)
    print(resp2)


def updating_the_documents(es):
    # change certain fields for the document, use index()
    edit_author1 = {"name": "Sheldon Sid", "novels_count": 18}
    resp = es.index(index=INDEX_NAME, doc_type="authors", id=1, body=edit_author1)
    print(resp)

    resp2 = es.get(index=INDEX_NAME, doc_type="authors", id=1)
    print(resp2)

    # add another field to the document, use update()
    resp3 = es.update(index=INDEX_NAME, doc_type="authors", id=2, body={"doc": {"Years": "1812-1870"}})
    print(resp3)


def deleting_documents_and_the_entire_index(es):
    resp = es.delete(index=INDEX_NAME, doc_type="authors", id=2)
    print(resp)

    resp2 = es.indices.delete(index=INDEX_NAME)
    print(resp2)


def main():
    ES_HOST = {"host": "localhost", "port": 9200}
    es = Elasticsearch(hosts=[ES_HOST])
    # create_an_index(es)
    # add_documents(es)
    retrieving_documents(es)
    # updating_the_documents(es)
    # deleting_documents_and_the_entire_index(es)


if __name__ == '__main__':
    main()
