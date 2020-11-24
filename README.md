![Logo](./doc/logo.png)

> 使用说明

```text
版本：V20201120.001
    使用说明：
         options:
             --url     / -u    需要下载的3dtiles数据，必填
             --dir     / -d    输出目录，必填")
             --start   / -s    开始下载的位置下标，默认从0开始，一般是分段下载或者某一个下载失败的时候使用
             --end     / -e    结束下载的位置下标，默认数据总长度，一般是分段下载或者某一个下载失败的时候使用
             --threads / -t    启动多线程下载，指定线程数，默认为1
             --help            查看帮助 
```

> 使用示例

`downloader.exe --url=https://lab.earthsdk.com/model/702aa950d03c11e99f7ddd77cbe22fea/tileset.json -d D:\3_Resources\3_数据\ddd -t 3`

> 注意事项

基于Python 3.7.0开发
