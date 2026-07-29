# Python 实用教程：文件、JSON 和网络请求

## 文件读写

`open` 可以读写文件。读取文本时推荐写明 `encoding="utf-8"`。处理文件时使用 `with open(...) as f`，可以自动关闭文件。

## JSON

JSON 常用于配置和接口数据。`json.loads` 把字符串转成 Python 对象，`json.dumps` 把 Python 对象转成字符串。

## 网络请求

调用 API 时要关注 URL、请求方法、请求头和请求体。标准库 `urllib` 可以完成基本请求，实际项目常用 `requests` 或 `httpx`。

## 练习

读取一个 `.json` 文件，统计里面每个分类的数量，再把统计结果保存成新的 JSON 文件。
