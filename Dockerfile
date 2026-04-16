# ==========================================
# 直接使用运行环境，解决 GLIBC 版本不匹配问题
# ==========================================
# 使用 python:3.10-slim 镜像，它包含了较新的 GLIBC 库
FROM python:3.10-slim

WORKDIR /app

# 1. 拷贝已经编译好的二进制文件
# 此时 Docker 会把当前目录下的 he_pda_engine 放入容器
COPY he_pda_engine .

# 2. 拷贝静态资源文件夹（Dash 平台运行必需）
COPY assets ./assets

# 3. 赋予执行权限
RUN chmod +x he_pda_engine

# 4. 暴露你的看板端口
EXPOSE 8052

# 5. 启动程序
CMD ["./he_pda_engine"]