# readme

## 配置 es

```bash
docker run -d \
  -v /Users/clip//ved/test/es/data:/usr/share/elasticsearch/data \
  -v /Users/clip//ved/test/es/plugins:/usr/share/elasticsearch/plugins \
  -p 9300:9300 \
  -p 9200:9200 \
  elasticsearch
```

拷贝一份 config 目录下的内容出来

```bash
docker run -d \
  -v /Users/clip//ved/test/es/config:/usr/share/elasticsearch/config \
  -v /Users/clip//ved/test/es/data:/usr/share/elasticsearch/data \
  -v /Users/clip//ved/test/es/plugins:/usr/share/elasticsearch/plugins \
  -p 9300:9300 \
  -p 9200:9200 \
  elasticsearch
```
