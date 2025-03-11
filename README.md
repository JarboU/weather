# 贵阳天气预报推送系统

## 项目介绍
这是一个自动获取贵阳市天气信息并通过企业微信webhook发送通知的Python程序。系统支持获取以下天气信息：
- 天气预警信息
- 三日天气预报
- 分钟级降水预报
- 生活指数
- 高精度实时天气

## 功能特性
- 支持多种天气数据的获取和展示
- 企业微信消息推送
- 数据缓存机制，避免频繁请求
- 失败重试机制，提高系统稳定性
- 支持命令行参数，灵活获取不同类型的天气信息
- 支持定时检查降水情况

## 安装依赖
1. 克隆项目到本地
2. 安装所需依赖包：
```bash
pip install -r requirements.txt
```

## 配置说明
在使用前，需要在`config.py`文件中配置以下信息：
1. 和风天气API配置
   - `WEATHER_API_KEY`：和风天气API密钥
   - `LOCATION_ID`：城市ID（默认为贵阳市）
   - `LOCATION_COORD`：经纬度坐标（默认为贵阳市观山湖区）

2. 企业微信配置
   - `WEBHOOK_URL`：企业微信机器人的Webhook地址

3. 缓存配置
   - `CACHE_EXPIRATION`：缓存过期时间（默认300秒）
   - `MAX_RETRIES`：最大重试次数（默认3次）
   - `RETRY_DELAY`：重试延迟时间（默认1秒）

## 使用方法
### 命令行参数
程序支持以下命令行参数：
- `--now`：只返回实时天气信息
- `--rain`：只返回分钟级降水预报
- `--forecast`：只返回三日天气预报
- `--life`：只返回生活指数信息
- `--check_rain`：检查降水情况

示例：
```bash
# 获取所有天气信息
python weather_notify.py

# 只获取实时天气
python weather_notify.py --now

# 检查降水情况
python weather_notify.py --check_rain
```

### 定时任务配置
可以使用crontab配置定时任务，实现自动天气推送。示例配置：
```bash
# 每天早上7点推送天气预报
0 7 * * * cd /path/to/weather && python weather_notify.py

# 每小时检查一次降水情况
0 * * * * cd /path/to/weather && python weather_notify.py --check_rain
```

## 单元测试
运行单元测试：
```bash
python -m unittest test_weather_notify.py
```
