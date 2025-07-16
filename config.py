#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CTF Platform Configuration
"""
import os
from datetime import timedelta

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'neon-ctf-platform-secret-key-change-in-production'
    
    # 数据库配置
    DATABASE_USER = os.environ.get('DB_USER') or 'ctf_user'
    DATABASE_PASSWORD = os.environ.get('DB_PASSWORD') or 'ctf_password'
    DATABASE_HOST = os.environ.get('DB_HOST') or 'localhost'
    DATABASE_NAME = os.environ.get('DB_NAME') or 'ctf_platform'
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # 文件上传配置
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'rar', '7z', 'tar', 'gz', 'bin', 'exe', 'py', 'c', 'cpp', 'java', 'js', 'html', 'css', 'php', 'sql'}
    
    # Session配置
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 安全配置
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # 应用配置
    CHALLENGE_PER_PAGE = 20
    USERS_PER_PAGE = 50
    MAX_FLAG_ATTEMPTS = 10  # 每题最大尝试次数
    RATE_LIMIT_ENABLED = True
    
    # Redis配置（用于缓存和限流）
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # 邮件配置（用于找回密码等功能）
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # AI API配置
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
    QWEN_API_KEY = os.environ.get('QWEN_API_KEY')
    
    # 本地和局域网模型配置
    LOCAL_MODEL_URL = os.environ.get('LOCAL_MODEL_URL') or 'http://127.0.0.1:1234/v1/chat/completions'
    LAN_MODEL_URL = os.environ.get('LAN_MODEL_URL') or 'http://192.168.1.108:1234/v1/chat/completions'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False  # 设置为True可以打印SQL语句

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # 生产环境安全加固
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/var/log/ctf-platform/app.log'

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
