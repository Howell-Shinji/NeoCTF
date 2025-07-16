#!/bin/bash

# Neon CTF Platform Setup Script

echo "🌃 Neon CTF Platform 安装脚本"
echo "====================================="

# 检查Python版本
echo "检查Python版本..."
python3 --version

# 创建虚拟环境
echo "创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo "安装Python依赖..."
pip install -r requirements.txt

# 数据库配置提示
echo ""
echo "📊 数据库配置"
echo "=============="
echo "请确保MySQL已安装并运行"
echo "1. 创建数据库: CREATE DATABASE ctf_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
echo "2. 创建用户: CREATE USER 'ctf_user'@'localhost' IDENTIFIED BY 'ctf_password';"
echo "3. 授权: GRANT ALL PRIVILEGES ON ctf_platform.* TO 'ctf_user'@'localhost';"
echo "4. 刷新权限: FLUSH PRIVILEGES;"
echo ""

# 询问是否继续
read -p "数据库配置完成后按回车继续... " -n1 -s

# 初始化数据库
echo ""
echo "初始化数据库..."
python3 app.py &
SERVER_PID=$!
sleep 3
kill $SERVER_PID

echo ""
echo "🎉 安装完成！"
echo ""
echo "启动说明："
echo "1. 激活虚拟环境: source venv/bin/activate"
echo "2. 启动应用: python3 app.py"
echo "3. 访问: http://localhost:5000"
echo ""
echo "默认管理员账户："
echo "用户名: admin"
echo "密码: admin123"
echo ""
echo "请及时修改默认密码！"
