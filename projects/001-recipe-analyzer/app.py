from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document, Text, connections, Index

HOSTS = ['localhost:9200']
CONNECTION_ALIAS = 'dev'
es_client = Elasticsearch(HOSTS, timeout=5)
connections.add_connection(CONNECTION_ALIAS, es_client)

DEFAULT_INDEX_SETTING = {
    "analysis": {
        "analyzer": {
            "ik_smart_synonym_analyzer": {
                "type": "custom",
                "tokenizer": "ik_smart",
                "filter": ["equal_synonyms"],
                "char_filter": ["symbol_mapping"],
            },
            "ik_smart_nonsynonym_analyzer": {
                "type": "custom",
                "tokenizer": "ik_smart",
                "filter": [],
                "char_filter": ["symbol_mapping"],
            },
            "ik_max_synonym_analyzer": {
                "type": "custom",
                "tokenizer": "ik_max_word",
                "filter": ["equal_synonyms"],
                "char_filter": ["symbol_mapping"],
            },
            "ik_max_nonsynonym_analyzer": {
                "type": "custom",
                "tokenizer": "ik_max_word",
                "filter": [],
                "char_filter": ["symbol_mapping"],
            },
        },
        "filter": {
            "equal_synonyms": {
                "type": "synonym",
                "synonyms_path": "equal_synonyms.txt"
            },
            "my_pinyin": {
                "type": "pinyin",
                "first_letter": "prefix",
                "padding_char": " "
            }
        },
        "char_filter": {
            "symbol_mapping": {
                "type": "mapping",
                "mappings": [
                    "- => \\u0020"
                ]
            }
        }
    }
}

class Recipe(Document):
    title = Text()

    class Index:
        name = 'recipe'
        using = CONNECTION_ALIAS


def _create_index(index_name):
    new_index = Index(index_name, using=CONNECTION_ALIAS)
    new_index.delete(ignore=[400, 404])
    new_index.settings(index=DEFAULT_INDEX_SETTING)
    new_index.create()


def create_indices():
    model = Recipe
    _create_index(model._index._name)
    model.init()  # create mapping


def main():
    # create_indices()

    titles = []
    with open('recipe_titles.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            _line = line.strip()
            if not _line:
                continue
            titles.append(_line)

    for title in titles[225:250]:
        keyword = title
        analyzer = 'ik_max_word'
        r = es_client.indices.analyze(index='recipe', body={"analyzer": analyzer, "text": keyword})
        t = '_'.join([token['token'] for token in r['tokens']])
        print(f'{keyword} -> {t}')


if __name__ == '__main__':
    main()
