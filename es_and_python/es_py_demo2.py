import json

import requests
from elasticsearch import Elasticsearch


INDEX_NAME = 'sw'


def insert_star_war_people_data(es: Elasticsearch):
    r = requests.get('http://localhost:9200')
    i = 18
    while r.status_code == 200:
        r = requests.get('http://swapi.co/api/people/' + str(i))
        es.index(index=INDEX_NAME, doc_type='people', id=i, body=json.loads(r.content))
        i = i + 1
    print(i)


def count_documents(es: Elasticsearch):
    r = es.count(index=INDEX_NAME)
    print(r)


def have_a_search(es: Elasticsearch):
    r = es.search(index=INDEX_NAME, body={"query": {"match": {'name':'Darth Vader'}}})
    print(r)

    r = es.search(index=INDEX_NAME, body={"query": {"prefix": {'name':'lu'}}})
    print(r)


def main():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    # insert_star_war_people_data(es)
    # count_documents(es)
    have_a_search(es)


if __name__ == '__main__':
    main()
