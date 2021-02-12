FROM python:3.7

RUN apt-get install -y libcurl4-openssl-dev \
    && apt-get install -y libssl-dev \
    && apt-get update -y \
    && apt-get install -y ffmpeg
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt
RUN apt-get install -y locales locales-all
ENV PYTHONPATH "/root/openpilot"

CMD ["/bin/bash"]