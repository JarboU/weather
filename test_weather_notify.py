#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from weather_notify import (
    get_weather_warning,
    get_weather_forecast,
    get_minutely_rain,
    get_life_indices,
    get_realtime_weather,
    send_wechat_message,
    format_weather_message
)

class TestWeatherNotify(unittest.TestCase):
    def setUp(self):
        """测试前的准备工作"""
        self.mock_warning_data = {
            'code': '200',
            'warning': [{'title': '测试预警'}]
        }
        self.mock_forecast_data = {
            'code': '200',
            'daily': [{
                'fxDate': '2024-01-01',
                'textDay': '晴',
                'tempMin': '10',
                'tempMax': '20',
                'humidity': '50',
                'precip': '0',
                'windDirDay': '东北风',
                'windScaleDay': '3'
            }]
        }
        self.mock_rain_data = {
            'code': '200',
            'summary': '未来两小时无降水',
            'minutely': [{
                'fxTime': '2024-01-01T12:00+08:00',
                'precip': '0'
            }]
        }
        self.mock_indices_data = {
            'code': '200',
            'daily': [{
                'name': '运动指数',
                'category': '适宜',
                'text': '天气较好，适宜运动'
            }]
        }
        self.mock_realtime_data = {
            'code': '200',
            'now': {
                'temp': '15',
                'feelsLike': '14',
                'humidity': '45',
                'text': '晴'
            }
        }

    @patch('requests.get')
    def test_get_weather_warning(self, mock_get):
        """测试获取天气预警信息"""
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_warning_data
        mock_get.return_value = mock_response

        result = get_weather_warning()
        self.assertEqual(result, self.mock_warning_data['warning'])

    @patch('requests.get')
    def test_get_weather_forecast(self, mock_get):
        """测试获取天气预报信息"""
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_forecast_data
        mock_get.return_value = mock_response

        result = get_weather_forecast()
        self.assertEqual(result, self.mock_forecast_data['daily'])

    @patch('requests.get')
    def test_get_minutely_rain(self, mock_get):
        """测试获取分钟级降水预报"""
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_rain_data
        mock_get.return_value = mock_response

        result = get_minutely_rain()
        self.assertEqual(result['summary'], self.mock_rain_data['summary'])
        self.assertEqual(result['minutely'], self.mock_rain_data['minutely'])

    @patch('requests.get')
    def test_get_life_indices(self, mock_get):
        """测试获取生活指数"""
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_indices_data
        mock_get.return_value = mock_response

        result = get_life_indices()
        self.assertEqual(result, self.mock_indices_data['daily'])

    @patch('requests.get')
    def test_get_realtime_weather(self, mock_get):
        """测试获取实时天气"""
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_realtime_data
        mock_get.return_value = mock_response

        result = get_realtime_weather()
        self.assertEqual(result, self.mock_realtime_data['now'])

    @patch('requests.post')
    def test_send_wechat_message(self, mock_post):
        """测试发送企业微信消息"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'errcode': 0}
        mock_post.return_value = mock_response

        result = send_wechat_message('测试消息')
        self.assertTrue(result)

    def test_format_weather_message(self):
        """测试天气信息格式化"""
        # 测试降水模式
        rain_message = format_weather_message(rain_data=self.mock_rain_data, mode='rain')
        self.assertIn('分钟级降水预报', rain_message)
        self.assertIn(self.mock_rain_data['summary'], rain_message)

        # 测试实时天气模式
        now_message = format_weather_message(realtime_weather=self.mock_realtime_data['now'], mode='now')
        self.assertIn('实时天气', now_message)
        self.assertIn(self.mock_realtime_data['now']['temp'], now_message)

        # 测试天气预报模式
        forecast_message = format_weather_message(weather_data=self.mock_forecast_data['daily'], mode='forecast')
        self.assertIn('三日天气预报', forecast_message)
        self.assertIn(self.mock_forecast_data['daily'][0]['textDay'], forecast_message)

        # 测试生活指数模式
        life_message = format_weather_message(life_indices=self.mock_indices_data['daily'], mode='life')
        self.assertIn('生活指数', life_message)
        self.assertIn(self.mock_indices_data['daily'][0]['name'], life_message)

if __name__ == '__main__':
    unittest.main()