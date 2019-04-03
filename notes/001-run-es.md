# run es

- 使用官方的 elasticsearch 镜像创建
- 绑定一下 9200 和 9300 端口号

```shell
curl http://localhost:9200
```

```shell
docker run -d \
  -v /Users/clip/ved/test/es/config:/usr/share/elasticsearch/config \
  -v /Users/clip/ved/test/es/data:/usr/share/elasticsearch/data \
  -v /Users/clip/ved/test/es/plugins:/usr/share/elasticsearch/plugins \
  -p 9300:9300 \
  -p 9200:9200 \
  elasticsearch
```
