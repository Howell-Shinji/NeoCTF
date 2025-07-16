#!/bin/bash

# Neon CTF Platform - 启动脚本
# 用于启动CTF平台的便捷脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 检查Python版本
check_python() {
    echo -e "${BLUE}检查Python版本...${NC}"
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        echo -e "${GREEN}Python版本: $PYTHON_VERSION${NC}"
    else
        echo -e "${RED}错误: 未找到Python3${NC}"
        exit 1
    fi
}

# 检查MySQL服务
check_mysql() {
    echo -e "${BLUE}检查MySQL服务...${NC}"
    if command -v mysql &> /dev/null; then
        echo -e "${GREEN}MySQL已安装${NC}"
    else
        echo -e "${YELLOW}警告: 未检测到MySQL，请确保已安装并运行${NC}"
    fi
}

# 安装依赖
install_dependencies() {
    echo -e "${BLUE}安装Python依赖...${NC}"
    
    # 检查是否存在虚拟环境
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}创建虚拟环境...${NC}"
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    echo -e "${BLUE}激活虚拟环境...${NC}"
    source venv/bin/activate
    
    # 安装依赖
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo -e "${GREEN}依赖安装完成${NC}"
}

# 初始化数据库
init_database() {
    echo -e "${BLUE}初始化数据库...${NC}"
    
    # 检查数据库配置
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}创建环境配置文件...${NC}"
        cat > .env << EOF
# 数据库配置
DB_USER=ctf_user
DB_PASSWORD=ctf_password
DB_HOST=localhost
DB_NAME=ctf_platform

# Flask配置
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this-in-production

# 文件上传
UPLOAD_FOLDER=uploads

# Redis配置（可选）
REDIS_URL=redis://localhost:6379/0
EOF
        echo -e "${GREEN}.env文件已创建，请根据需要修改配置${NC}"
    fi
    
    # 创建上传目录
    mkdir -p uploads
    chmod 755 uploads
    
    echo -e "${GREEN}数据库初始化准备完成${NC}"
}

# 启动应用
start_app() {
    echo -e "${BLUE}启动CTF平台...${NC}"
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 设置环境变量
    export FLASK_APP=app.py
    export FLASK_ENV=development
    
    # 启动应用
    echo -e "${CYAN}=== Neon CTF Platform ===${NC}"
    echo -e "${GREEN}平台启动中...${NC}"
    echo -e "${YELLOW}访问地址: http://localhost:5000${NC}"
    echo -e "${YELLOW}管理员账户: admin / admin123${NC}"
    echo -e "${PURPLE}按 Ctrl+C 停止服务${NC}"
    echo
    
    python app.py
}

# 生产环境启动
start_production() {
    echo -e "${BLUE}生产环境启动...${NC}"
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 使用gunicorn启动
    gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 --keep-alive 2 --max-requests 1000 app:app
}

# 显示帮助信息
show_help() {
    echo -e "${CYAN}Neon CTF Platform - 启动脚本${NC}"
    echo
    echo "用法: $0 [选项]"
    echo
    echo "选项:"
    echo "  start, run     启动开发服务器（默认）"
    echo "  production     生产环境启动"
    echo "  install        安装依赖"
    echo "  init           初始化数据库"
    echo "  setup          完整安装（install + init）"
    echo "  check          检查环境"
    echo "  help, -h       显示此帮助信息"
    echo
    echo "示例:"
    echo "  $0 setup      # 完整安装和配置"
    echo "  $0 start      # 启动开发服务器"
    echo "  $0 production # 生产环境启动"
}

# 完整安装
full_setup() {
    echo -e "${CYAN}=== Neon CTF Platform 完整安装 ===${NC}"
    echo
    check_python
    check_mysql
    install_dependencies
    init_database
    echo
    echo -e "${GREEN}安装完成！${NC}"
    echo -e "${YELLOW}请确保MySQL服务正在运行，然后执行：${NC}"
    echo -e "${BLUE}$0 start${NC}"
}

# 环境检查
check_environment() {
    echo -e "${CYAN}=== 环境检查 ===${NC}"
    check_python
    check_mysql
    
    echo -e "${BLUE}检查虚拟环境...${NC}"
    if [ -d "venv" ]; then
        echo -e "${GREEN}虚拟环境存在${NC}"
    else
        echo -e "${YELLOW}虚拟环境不存在${NC}"
    fi
    
    echo -e "${BLUE}检查依赖文件...${NC}"
    if [ -f "requirements.txt" ]; then
        echo -e "${GREEN}requirements.txt存在${NC}"
    else
        echo -e "${RED}requirements.txt不存在${NC}"
    fi
    
    echo -e "${BLUE}检查配置文件...${NC}"
    if [ -f ".env" ]; then
        echo -e "${GREEN}.env配置文件存在${NC}"
    else
        echo -e "${YELLOW}.env配置文件不存在${NC}"
    fi
    
    echo -e "${BLUE}检查上传目录...${NC}"
    if [ -d "uploads" ]; then
        echo -e "${GREEN}uploads目录存在${NC}"
    else
        echo -e "${YELLOW}uploads目录不存在${NC}"
    fi
}

# 主函数
main() {
    case "$1" in
        "start"|"run"|"")
            start_app
            ;;
        "production")
            start_production
            ;;
        "install")
            install_dependencies
            ;;
        "init")
            init_database
            ;;
        "setup")
            full_setup
            ;;
        "check")
            check_environment
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo -e "${RED}未知选项: $1${NC}"
            echo "使用 '$0 help' 查看帮助信息"
            exit 1
            ;;
    esac
}

# 脚本入口
main "$@"
