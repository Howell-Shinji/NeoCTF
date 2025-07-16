# Neon CTF Platform

一个基于Flask的现代化CTF（Capture The Flag）竞赛平台，采用了霓虹夜主题的界面设计，集成了AI安全助手功能。

## 功能特性

### 核心功能
- 🎯 **题目管理**: 支持Web、Crypto、Reverse、Pwn、Forensics、Misc等多种题目类型
- 👥 **用户管理**: 完整的用户注册、登录、权限管理系统
- 🏆 **排行榜**: 实时显示用户得分和排名
- 📊 **统计面板**: 提供详细的用户和题目统计信息
- 💡 **提示系统**: 分级提示功能，消耗积分解锁
- 📎 **附件管理**: 支持题目附件上传和下载
- 🔐 **Flag验证**: 安全的Flag提交和验证机制

### AI安全助手功能
- 🤖 **动态场景生成**: 基于AI生成个性化CTF挑战
- ⚔️ **攻击模拟**: 模拟各种网络攻击场景
- 🛡️ **防御策略**: 智能生成防御建议和解决方案
- 📋 **能力评估**: 自动分析用户安全技能水平
- 🎓 **学习资料**: 个性化的安全学习内容推荐

## 技术栈

### 后端
- **Flask**: 轻量级Web框架
- **SQLAlchemy**: ORM数据库操作
- **Flask-Login**: 用户认证管理
- **Flask-Bcrypt**: 密码加密
- **PyMySQL**: MySQL数据库连接器

### 前端
- **HTML5/CSS3**: 现代化界面设计
- **JavaScript**: 交互功能实现
- **Tokyo Night主题**: 霓虹夜色彩搭配

### 数据库
- **MySQL**: 主数据库
- **Redis**: 缓存和会话存储（可选）

### AI集成
- **OpenAI API**: 支持多种AI模型
- **DeepSeek API**: 国产AI模型支持
- **Qwen API**: 通义千问模型
- **本地模型**: 支持本地部署的AI模型

## 安装部署

### 环境要求
- Python 3.8+
- MySQL 8.0+
- Redis 6.0+（可选）

### 快速安装

1. **克隆项目**
```bash
git clone <repository-url>
cd ctf-platform
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入您的配置信息
```

5. **配置数据库**
```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE ctf_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 导入数据库结构
mysql -u root -p ctf_platform < ctf_platform.sql
```

6. **启动应用**
```bash
python app.py
```

### 使用脚本安装

项目提供了自动化安装脚本：

```bash
chmod +x setup.sh
./setup.sh
```

## 配置说明

### 基础配置

编辑 [config.py](config.py) 文件中的配置项：

```python
# 数据库配置
DATABASE_USER = 'your_db_user'
DATABASE_PASSWORD = 'your_db_password'
DATABASE_HOST = 'localhost'
DATABASE_NAME = 'ctf_platform'

# 安全配置
SECRET_KEY = 'your-secret-key-here'

# 文件上传配置
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
```

### AI功能配置

在 `.env` 文件中配置AI API密钥：

```env
# DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_api_key

# Qwen API
QWEN_API_KEY=your_qwen_api_key

# 本地模型URL
LOCAL_MODEL_URL=http://127.0.0.1:1234/v1/chat/completions
LAN_MODEL_URL=http://192.168.1.108:1234/v1/chat/completions
```

## 使用指南

### 管理员功能

1. **默认管理员账户**
   - 用户名: `admin`
   - 密码: `admin123`

2. **题目管理**
   - 访问 `/admin/challenges` 管理题目
   - 支持添加、编辑、删除题目
   - 支持附件上传和提示管理

3. **用户管理**
   - 访问 `/admin/users` 管理用户
   - 设置管理员权限
   - 查看用户详细信息

4. **AI管理面板**
   - 访问 `/admin_ai` 查看AI功能统计
   - 管理攻击模拟和防御策略

### 普通用户功能

1. **注册登录**
   - 访问 `/register` 注册新账户
   - 访问 `/login` 登录系统

2. **解题流程**
   - 浏览 `/challenges` 查看题目
   - 点击题目查看详情
   - 提交Flag获得积分

3. **AI训练场**
   - 访问 `/ai-arena` 使用AI安全助手
   - 获取防御建议和学习资料
   - 进行能力评估

## 目录结构

```
ctf-platform/
├── app.py                 # 主应用文件
├── config.py             # 配置文件
├── requirements.txt      # 依赖包列表
├── ctf_platform.sql      # 数据库结构
├── .env.example         # 环境变量模板
├── setup.sh             # 自动安装脚本
├── start.sh             # 启动脚本
├── static/              # 静态文件
│   ├── css/            # 样式文件
│   └── js/             # JavaScript文件
├── templates/           # HTML模板
│   ├── admin/          # 管理员模板
│   └── *.html          # 页面模板
├── uploads/            # 上传文件目录
└── utils/              # 工具模块
    └── ai_api.py       # AI接口封装
```

## 数据库设计

### 主要表结构

- **users**: 用户信息表
- **challenges**: 题目信息表
- **categories**: 题目分类表
- **submissions**: 提交记录表
- **hints**: 提示信息表
- **attachments**: 附件信息表
- **attack_simulations**: 攻击模拟表
- **defense_strategies**: 防御策略表
- **user_evaluations**: 用户评估表

详细的数据库结构请参考 [ctf_platform.sql](ctf_platform.sql)

## API文档

### 主要API端点

```
GET  /api/stats                    # 获取平台统计信息
POST /api/generate_scenario        # 生成AI场景
POST /api/simulate_attack/{id}     # 模拟攻击
POST /api/generate_defense/{id}    # 生成防御策略
POST /api/evaluate_user/{id}       # 用户能力评估
POST /api/user_defense_advice      # 获取防御建议
POST /api/security_learning        # 获取学习资料
```

## 部署建议

### 生产环境部署

1. **使用WSGI服务器**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. **配置反向代理**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **安全配置**
```bash
# 设置环境变量
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key

# 启用HTTPS
export SESSION_COOKIE_SECURE=true
```

### Docker部署

项目支持Docker容器化部署：

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MySQL服务是否启动
   - 验证数据库用户权限
   - 确认防火墙设置

2. **文件上传失败**
   - 检查 `uploads` 目录权限
   - 验证文件大小限制
   - 确认文件类型允许

3. **AI功能无法使用**
   - 检查API密钥配置
   - 验证网络连接
   - 查看模型服务状态

### 日志调试

启用调试模式：

```python
# config.py
DEBUG = True
SQLALCHEMY_ECHO = True  # 显示SQL语句
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目基于 MIT 许可证开源。详情请参阅 `LICENSE` 文件。

## 联系方式

- 项目主页: [GitHub Repository](https://github.com/Howell-Shinji/NeoCTF.git)
- 问题反馈: [GitHub Issues](https://github.com/Howell-Shinji/NeoCTF/issues)
- 邮箱: Howell-Bear@outlook.com

## 更新日志

### v1.0.0
- 初始版本发布
- 基础CTF平台功能
- AI安全助手集成
- 霓虹夜主题界面

---

**注意**: 本项目仅用于教育和学习目的，请遵循相关法律法规，不得用于非法用途。