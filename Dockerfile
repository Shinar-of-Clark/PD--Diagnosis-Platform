# ==========================================
# 阶段一：Nuitka 编译环境
# ==========================================
FROM python:3.10-slim AS builder

WORKDIR /app

# 安装必要的编译工具
RUN apt-get update && apt-get install -y \
    gcc g++ binutils patchelf ccache zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 先安装基础环境工具
RUN pip install --no-cache-dir setuptools ordered-set zstandard

# 复制依赖并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir nuitka

# 复制源代码
COPY . .

# 执行编译
# 移除了所有无效的 --plugin-enable 指令（Nuitka 不再将 dash/pandas 作为独立插件名）
# 使用 --include-package-data 确保静态资源被打包
RUN python -m nuitka \
    --standalone \
    --onefile \
    --follow-imports \
    --include-package-data=dash \
    --include-package-data=dash_bootstrap_components \
    --include-package-data=plotly \
    --include-package-data=pandas \
    --include-data-dir=assets=assets \
    --output-dir=dist \
    --output-filename=he_pda_engine \
    --show-progress \
    --show-memory \
    diagnosis.py

# ==========================================
# 阶段二：部署环境 (体积最小化)
# ==========================================
FROM debian:bullseye-slim
WORKDIR /app
COPY --from=builder /app/dist/he_pda_engine .
EXPOSE 8052
RUN chmod +x he_pda_engine
CMD ["./he_pda_engine"]