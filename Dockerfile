# using ubuntu LTS version
FROM ubuntu:20.04 AS builder-image

# avoid stuck build due to user prompt
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install --no-install-recommends -y python3.9 python3.9-dev python3.9-venv python3-pip python3-wheel build-essential && \
	apt-get clean && rm -rf /var/lib/apt/lists/*

# create and activate virtual environment
# using final folder name to avoid path issues with packages
RUN python3.9 -m venv /home/myuser/venv
ENV PATH="/home/myuser/venv/bin:$PATH"

# install requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir wheel
RUN pip3 install --no-cache-dir -r requirements.txt

FROM ubuntu:20.04 AS runner-image
RUN apt-get update && apt-get install --no-install-recommends -y python3.9 python3-venv && \
	apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home myuser
COPY --from=builder-image /home/myuser/venv /home/myuser/venv
USER myuser
RUN mkdir /home/myuser/code
WORKDIR /home/myuser/code/
COPY . .
EXPOSE 5000
# make sure all messages always reach console
ENV PYTHONUNBUFFERED=1

# configurations
ENV MYSQL_DATABASE=assignment
ENV RAW_API_KEY=CGCXS9L8HHGAH0YC
ENV DB_PASS=dbpass
ENV DB_USER=dbuser
ENV DB=assignment
ENV DB_HOST=host.docker.internal

# activate virtual environment
ENV VIRTUAL_ENV=/home/myuser/venv
ENV PATH="/home/myuser/venv/bin:$PATH"
ENV PYTHONPATH=/home/myuser/code/financial/module:${PYTHONPATH}
#RUN ["python","get_raw_data.py"]

CMD ["python", "financial/app.py"]