#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class WeatherConfig:
    # 和风天气API配置
    WEATHER_API_KEY = "******"  # 请替换为实际的API密钥
    WEATHER_API_URL = "https://devapi.qweather.com/v7/weather/3d"
    WEATHER_WARNING_URL = "https://devapi.qweather.com/v7/warning/now"  # 天气预警API
    MINUTELY_RAIN_URL = "https://devapi.qweather.com/v7/minutely/5m"  # 分钟级降水API
    LIFE_INDEX_URL = "https://devapi.qweather.com/v7/indices/1d"  # 生活指数API
    REALTIME_WEATHER_URL = "https://devapi.qweather.com/v7/grid-weather/now"  # 高精度实时天气API
    LOCATION_ID = "101260101"  # 贵阳市的城市ID
    LOCATION_COORD = "106.61,26.64"  # 贵阳市观山湖区的经纬度坐标

class WechatConfig:
    # 企业微信配置
    WEBHOOK_URL = "******"  # 请替换为实际的Webhook URL

class CacheConfig:
    # 缓存配置
    CACHE_EXPIRATION = 300  # 缓存过期时间（秒）
    MAX_RETRIES = 3  # 最大重试次数
    RETRY_DELAY = 1  # 重试延迟（秒）
