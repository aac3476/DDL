FROM python:3.6

WORKDIR  /

COPY requirements.txt ./
COPY . ./
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD ["gunicorn", "run:app", "-c", "/gunicorn.conf.py"]

EXPOSE 6667
