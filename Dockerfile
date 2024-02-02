FROM python:3-alpine

WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY . .
RUN pip install --trusted-host pypi.python.org -r requirements.txt

#ADD config.py .
#ADD auth.py .
#ADD main.py .
#ADD config.json .

CMD [ "python", "main.py" ]
