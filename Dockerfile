FROM python:3.9-slim

# 设置容器的时区为中国北京时间
ENV TZ=Asia/Shanghai

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 在容器启动时检查配置文件的存在，并运行main.py
CMD ["sh", "-c", "\
if [ -f /mnt/config_bili.ini ]; then \
    cp -f /mnt/config_bili.ini /app/config_bili.ini; \
    python -u main.py; \
else \
    echo 'Error: /mnt/config_bili.ini file not found. Please mount the /mnt/config_bili.ini file and try again.'; \
    exit 1; \
fi"]
