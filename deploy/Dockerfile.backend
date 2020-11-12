FROM python:3.7.3

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
COPY ./ .
RUN rm -rf output

CMD [ "python", "www/manage.py", "runserver", "0.0.0.0:8000"]
