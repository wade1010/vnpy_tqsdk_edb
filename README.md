# VnPy TQSdk EDB Datafeed

VnPy 的天勤 EDB 免费行情数据适配器。

## 功能特性

- 支持从天勤 EDB 服务获取历史 K 线数据
- 免费模式支持：
  - 日线数据：任意历史区间
  - 分钟线数据：最近 1 年
- 支持多种时间周期：1分钟、日线


## 安装

安装环境推荐基于3.0.0版本以上的【[**VeighNa Studio**](https://www.vnpy.com)】。

直接使用pip命令：

```
pip install vnpy_tqsdk_edb
```


或者下载源代码后，解压后在cmd中运行：

```
pip install -e .
```


## VNPY桌面应用使用

在VeighNa中使用 vnpy_tqsdk_edb 时，需要在全局配置中填写以下字段信息：

|名称|含义|必填||
|---------|----|---|---|
|datafeed.name|名称|是|tqsdk_edb|
|datafeed.username|用户名|否||
|datafeed.password|密码|否||


### 桌面应用使用截图
![image.png](https://gitee.com/hxc8/images10/raw/master/img/202602091349644.png)

![image.png](https://gitee.com/hxc8/images10/raw/master/img/202602091350826.png)

![image.png](https://gitee.com/hxc8/images10/raw/master/img/202602091351337.png)

![image.png](https://gitee.com/hxc8/images10/raw/master/img/202602091355019.png)

![image.png](https://gitee.com/hxc8/images10/raw/master/img/202602091355247.png)


## 代码使用

```python
from vnpy.trader.datafeed import get_datafeed
from vnpy.trader.object import HistoryRequest
from vnpy.trader.constant import Exchange, Interval
import datetime
# 获取数据源
datafeed = get_datafeed()

# 构造查询请求
req = HistoryRequest(
    symbol="ag2604",
    exchange=Exchange.SHFE,
    interval=Interval.DAILY,
    start=datetime.datetime(2026, 1, 1),
    end=datetime.datetime(2026, 2, 10)
)

# 查询历史数据
bars = datafeed.query_bar_history(req)
print(bars[0])

#打印结果如下:
BarData(gateway_name='EDB', extra=None, symbol='ag2604', exchange=<Exchange.SHFE: 'SHFE'>, datetime=datetime.datetime(2026, 1, 5, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='Asia/Shanghai')), interval=<Interval.DAILY: 'd'>, volume=np.int64(671811), turnover=0, open_interest=np.int64(222892), open_price=np.int64(18200), high_price=np.int64(18399), low_price=np.int64(17926), close_price=np.int64(18247))
```

## 接口限制

免费访问限制（来自天勤 EDB 服务）：
- 日线数据：任意历史区间
- 分钟线数据：最近 1 年

如需完整历史数据，请前往天勤官网购买专业版访问权限。

## 许可证

MIT License
