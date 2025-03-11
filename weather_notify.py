#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import logging
from datetime import datetime
from functools import wraps
from time import sleep
from config import WeatherConfig, WechatConfig, CacheConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 缓存字典
cache = {}

def cache_result(func):
    """缓存装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        cache_key = f"{func.__name__}_{args}_{kwargs}"
        now = datetime.now().timestamp()
        
        if cache_key in cache:
            result, timestamp = cache[cache_key]
            if now - timestamp < CacheConfig.CACHE_EXPIRATION:
                return result
        
        result = func(*args, **kwargs)
        cache[cache_key] = (result, now)
        return result
    return wrapper

def retry_on_failure(func):
    """重试装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < CacheConfig.MAX_RETRIES:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                retries += 1
                if retries == CacheConfig.MAX_RETRIES:
                    logger.error(f"{func.__name__} 最终失败: {str(e)}")
                    return None
                logger.warning(f"{func.__name__} 失败，正在重试 ({retries}/{CacheConfig.MAX_RETRIES}): {str(e)}")
                sleep(CacheConfig.RETRY_DELAY)
    return wrapper

@retry_on_failure
@cache_result
def get_weather_warning():
    """获取天气预警信息"""
    params = {
        'location': WeatherConfig.LOCATION_ID,
        'key': WeatherConfig.WEATHER_API_KEY
    }
    response = requests.get(WeatherConfig.WEATHER_WARNING_URL, params=params)
    response.raise_for_status()
    warning_data = response.json()

    if warning_data.get('code') == '200':
        return warning_data.get('warning')
    logger.error(f"获取天气预警数据失败: {warning_data.get('code')}, {warning_data.get('fxLink')}")
    return None

@retry_on_failure
@cache_result
def get_weather_forecast():
    """获取贵阳市三日天气预报"""
    params = {
        'location': WeatherConfig.LOCATION_ID,
        'key': WeatherConfig.WEATHER_API_KEY
    }
    response = requests.get(WeatherConfig.WEATHER_API_URL, params=params)
    response.raise_for_status()
    weather_data = response.json()

    if weather_data.get('code') == '200':
        return weather_data.get('daily')
    logger.error(f"获取天气数据失败: {weather_data.get('code')}, {weather_data.get('fxLink')}")
    return None

@retry_on_failure
@cache_result
def get_minutely_rain():
    """获取分钟级降水预报"""
    params = {
        'location': WeatherConfig.LOCATION_COORD,
        'key': WeatherConfig.WEATHER_API_KEY
    }
    response = requests.get(WeatherConfig.MINUTELY_RAIN_URL, params=params)
    response.raise_for_status()
    rain_data = response.json()

    if rain_data.get('code') == '200':
        return {
            'summary': rain_data.get('summary'),
            'minutely': rain_data.get('minutely')
        }
    logger.error(f"获取分钟级降水数据失败: {rain_data.get('code')}, {rain_data.get('fxLink')}")
    return None

@retry_on_failure
@cache_result
def get_life_indices():
    """获取生活指数"""
    params = {
        'location': WeatherConfig.LOCATION_ID,
        'key': WeatherConfig.WEATHER_API_KEY,
        'type': '2,3,5,6,8,9,15,16'
    }
    response = requests.get(WeatherConfig.LIFE_INDEX_URL, params=params)
    response.raise_for_status()
    indices_data = response.json()

    if indices_data.get('code') == '200':
        return indices_data.get('daily')
    logger.error(f"获取生活指数数据失败: {indices_data.get('code')}, {indices_data.get('fxLink')}")
    return None

@retry_on_failure
@cache_result
def get_realtime_weather():
    """获取高精度实时天气"""
    params = {
        'location': WeatherConfig.LOCATION_COORD,
        'key': WeatherConfig.WEATHER_API_KEY
    }
    response = requests.get(WeatherConfig.REALTIME_WEATHER_URL, params=params)
    response.raise_for_status()
    realtime_data = response.json()

    if realtime_data.get('code') == '200':
        return realtime_data.get('now')
    logger.error(f"获取实时天气数据失败: {realtime_data.get('code')}, {realtime_data.get('fxLink')}")
    return None

@retry_on_failure
def send_wechat_message(message):
    """发送企业微信消息"""
    try:
        data = {
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        response = requests.post(WechatConfig.WEBHOOK_URL, json=data)
        response.raise_for_status()
        result = response.json()

        if result.get('errcode') == 0:
            logger.info("消息发送成功")
            return True
        else:
            logger.error(f"消息发送失败: {result.get('errmsg')}")
            return False
    except Exception as e:
        logger.error(f"发送消息出错: {str(e)}")
        return False

def format_weather_message(weather_data=None, warning_data=None, life_indices=None, realtime_weather=None, rain_data=None, mode=None):
    """格式化天气信息"""
    message = "贵阳市天气信息\n\n"

    # 如果指定了模式，则只返回对应的天气信息
    if mode == 'rain' and rain_data:
        message += "分钟级降水预报:\n"
        message += f"{rain_data.get('summary')}\n"
        if rain_data.get('minutely'):
            for minute in rain_data.get('minutely'):
                message += f"{minute.get('fxTime').split('T')[1][:5]}: {minute.get('precip')}mm\n"
        return message
    elif mode == 'now' and realtime_weather:
        message += "实时天气:\n"
        message += f"温度: {realtime_weather.get('temp')}°C\n"
        message += f"体感温度: {realtime_weather.get('feelsLike')}°C\n"
        message += f"相对湿度: {realtime_weather.get('humidity')}%\n"
        message += f"天气状况: {realtime_weather.get('text')}\n"
        return message
    elif mode == 'forecast' and weather_data:
        message += "三日天气预报:\n"
        for daily in weather_data:
            date = datetime.strptime(daily['fxDate'], '%Y-%m-%d').strftime('%m月%d日')
            message += f"【{date}】\n"
            message += f"天气: {daily['textDay']}\n"
            message += f"温度: {daily['tempMin']}°C ~ {daily['tempMax']}°C\n"
            message += f"湿度: {daily['humidity']}%\n"
            message += f"降水概率: {daily['precip']}%\n"
            message += f"风向: {daily['windDirDay']} {daily['windScaleDay']}级\n"
            message += "\n"
        return message
    elif mode == 'life' and life_indices:
        message += "生活指数:\n"
        for index in life_indices:
            message += f"{index.get('name')}: {index.get('category')} - {index.get('text')}\n"
        return message

    # 处理分钟级降水预报
    if rain_data:
        message += "分钟级降水预报:\n"
        message += f"{rain_data.get('summary')}\n"
        if rain_data.get('minutely'):
            for minute in rain_data.get('minutely'):
                message += f"{minute.get('fxTime').split('T')[1][:5]}: {minute.get('precip')}mm\n"
        message += "\n"

    # 处理天气预警信息
    if warning_data is None:
        message += "获取天气预警数据失败，失败原因：403, None\n\n"
    elif warning_data:
        message += "⚠️ 天气预警:\n"
        for warning in warning_data:
            message += f"{warning.get('typeName')}: {warning.get('text')}\n"
        message += "\n"

    # 处理天气预报信息
    if not weather_data:
        message += "获取天气数据失败，失败原因：403, None\n\n"
    else:
        message += "三日天气预报:\n"
        for daily in weather_data:
            date = datetime.strptime(daily['fxDate'], '%Y-%m-%d').strftime('%m月%d日')
            message += f"【{date}】\n"
            message += f"天气: {daily['textDay']}\n"
            message += f"温度: {daily['tempMin']}°C ~ {daily['tempMax']}°C\n"
            message += f"湿度: {daily['humidity']}%\n"
            message += f"降水概率: {daily['precip']}%\n"
            message += f"风向: {daily['windDirDay']} {daily['windScaleDay']}级\n"
            message += "\n"

    # 处理生活指数信息
    if life_indices:
        message += "生活指数:\n"
        for index in life_indices:
            message += f"{index.get('name')}: {index.get('category')} - {index.get('text')}\n"
        message += "\n"

    # 处理实时天气信息
    if realtime_weather is None:
        message += "获取实时天气数据失败，失败原因：400, None\n"
    elif realtime_weather:
        message += "实时天气:\n"
        message += f"温度: {realtime_weather.get('temp')}°C\n"
        message += f"体感温度: {realtime_weather.get('feelsLike')}°C\n"
        message += f"相对湿度: {realtime_weather.get('humidity')}%\n"
        message += f"天气状况: {realtime_weather.get('text')}\n"

    return message

def format_error_message(error_type, error_msg):
    """格式化错误消息"""
    return f"⚠️ 系统错误提醒\n\n错误类型: {error_type}\n错误信息: {error_msg}"

def check_hourly_rain():
    """检查未来两小时的降水情况"""
    rain_data = get_minutely_rain()
    if not rain_data:
        logger.error("获取降水数据失败")
        return

    # 检查是否有降水
    has_rain = False
    for minute in rain_data.get('minutely', []):
        if float(minute.get('precip', 0)) > 0:
            has_rain = True
            break

    # 如果有降水，发送通知
    if has_rain:
        message = format_weather_message(rain_data=rain_data, mode='rain')
        send_wechat_message(message)
        logger.info("检测到降水，已发送通知")
    else:
        logger.info("未检测到降水")

if __name__ == '__main__':
    import argparse

    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='贵阳天气预报推送系统')
    parser.add_argument('--now', action='store_true', help='只返回实时天气信息')
    parser.add_argument('--rain', action='store_true', help='只返回分钟级降水预报')
    parser.add_argument('--forecast', action='store_true', help='只返回三日天气预报')
    parser.add_argument('--life', action='store_true', help='只返回生活指数信息')
    parser.add_argument('--check_rain', action='store_true', help='检查降水情况')
    args = parser.parse_args()

    try:
        if args.check_rain:
            check_hourly_rain()
        else:
            # 根据参数获取对应的天气数据
            weather_data = get_weather_forecast() if not args.now and not args.rain and not args.life or args.forecast else None
            warning_data = get_weather_warning() if not args.now and not args.rain and not args.forecast and not args.life else None
            rain_data = get_minutely_rain() if not args.now and not args.forecast and not args.life or args.rain else None
            realtime_weather = get_realtime_weather() if not args.rain and not args.forecast and not args.life or args.now else None
            life_indices = get_life_indices() if not args.now and not args.rain and not args.forecast or args.life else None

            # 确定模式
            mode = None
            if args.now:
                mode = 'now'
            elif args.rain:
                mode = 'rain'
            elif args.forecast:
                mode = 'forecast'
            elif args.life:
                mode = 'life'

            # 格式化并发送消息
            message = format_weather_message(weather_data, warning_data, life_indices, realtime_weather, rain_data, mode)
            send_wechat_message(message)
    except Exception as e:
        error_message = format_error_message("系统错误", str(e))
        send_wechat_message(error_message)
        logger.error(f"程序执行出错: {str(e)}")
