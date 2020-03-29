FROM python:3.8.2
WORKDIR /app
RUN pip3 install pipenv --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . .
RUN pipenv install
CMD ["pipenv", "run", "flask", "run", "--host", "0.0.0.0", "--port", "80"]
