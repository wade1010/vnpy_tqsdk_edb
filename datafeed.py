"""
VnPy 的 EDB 数据源适配器。

实现 VnPy 的 BaseDatafeed 接口，从天勤 EDB 服务获取历史行情数据。
"""

import traceback
from datetime import datetime, timedelta
from typing import Callable

import pandas as pd
import requests
from io import StringIO
from vnpy.trader.constant import Interval
from vnpy.trader.datafeed import BaseDatafeed
from vnpy.trader.object import BarData, HistoryRequest
from vnpy.trader.database import DB_TZ

GATEWAY_NAME: str = "EDB"
EDB_BASE_URL: str = "https://edb.shinnytech.com/md/kline"
FREE_MODE_MINUTE_DATA_DAYS: int = 365  # 1 year

# VnPy Interval 到 EDB period (秒) 的映射
INTERVAL_VT2EDB: dict[Interval, int] = {
    Interval.MINUTE: 60,
    Interval.DAILY: 86400,
}


class EdbDatafeed(BaseDatafeed):
    """
    天勤 EDB 免费行情数据适配器，供 VnPy 使用。
    免费访问限制：
    - 日线数据：任意历史区间
    - 分钟线数据：最近 1 年
    """

    def __init__(self) -> None:
        """初始化 EDB 数据源适配器。"""
        super().__init__()

        self.gateway_name: str = GATEWAY_NAME

    def init(self, output: Callable = print) -> bool:
        return True

    def query_bar_history(
            self, req: HistoryRequest, output: Callable = print
    ) -> list[BarData]:
        """
        从 EDB 免费服务查询历史 K 线数据。

        参数:
            req: 包含查询参数的 HistoryRequest 对象
            output: 用于输出日志的可调用对象（默认 print）

        返回:
            BarData 列表（出错时返回空列表）

        注意:
            免费模式限制：
            - 日线数据：任意历史区间
            - 分钟线数据：最近 1 年
        """
        # 获取时间周期（秒）
        period = INTERVAL_VT2EDB.get(req.interval)
        if not period:
            output(f"EDB免费版查询K线数据失败：不支持的时间周期{req.interval.value}")
            return []

        # 计算起始日距今天数（使用带时区的 datetime）
        now = datetime.now(DB_TZ)
        req.start = req.start.astimezone(DB_TZ)
        days_from_start = (now - req.start).days
        if req.interval == Interval.MINUTE and days_from_start >= FREE_MODE_MINUTE_DATA_DAYS:
            output(f"免费用户仅可获取最近 {FREE_MODE_MINUTE_DATA_DAYS} 天内的1分钟数据,自动处理开始时间。您请求的起始日距今 {days_from_start} 天。日线数据可查询任意历史区间。")
            # 1分钟周期刚好满1年时，使用当前时间往前一年+1分钟作为起始时间
            req.start = now - timedelta(days=FREE_MODE_MINUTE_DATA_DAYS) + timedelta(minutes=1)

        if req.symbol.endswith("888"):
            tq_symbol = f"KQ.m@{req.exchange.value}.{req.symbol.replace('888', '')}"
        elif req.symbol.endswith("999"):
            tq_symbol = f"KQ.m@{req.exchange.value}.{req.symbol.replace('999', '')}"
        else:
            if req.exchange.value in req.symbol:
                tq_symbol = req.symbol
            else:
                tq_symbol = f"{req.exchange.value}.{req.symbol}"

        # 构造请求参数
        params = {
            "symbol": tq_symbol,
            "period": period,
            "start_time": req.start.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": req.end.strftime("%Y-%m-%d %H:%M:%S"),
        }

        # 发起请求（免费模式不需要token）
        try:
            resp = requests.get(
                EDB_BASE_URL,
                params=params,
                timeout=30
            )
            resp.raise_for_status()
        except Exception:
            output(traceback.format_exc())
            return []

        # 解析返回的CSV数据
        bars: list[BarData] = []

        try:
            # 从文本读取CSV
            df = pd.read_csv(StringIO(resp.text))
            # 转换每一行数据为BarData
            for _, row in df.iterrows():
                bar = BarData(
                    symbol=req.symbol,
                    exchange=req.exchange,
                    interval=req.interval,
                    datetime=datetime.fromtimestamp(
                        row["datetime_nano"] / 1_000_000_000,
                        tz=DB_TZ
                    ),
                    open_price=row["open"],
                    high_price=row["high"],
                    low_price=row["low"],
                    close_price=row["close"],
                    volume=row["volume"],
                    open_interest=row["open_oi"],
                    gateway_name=GATEWAY_NAME,
                )
                bars.append(bar)

        except Exception:
            output(traceback.format_exc())
            return []

        return bars
