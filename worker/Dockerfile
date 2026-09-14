FROM python
WORKDIR /home/myapp
COPY ./callback.py /home/myapp/
COPY ./consumer.py /home/myapp/
COPY ./database.py /home/myapp/
COPY ./router_client.py /home/myapp/
COPY ./requirements.txt /home/myapp/
RUN pip install --no-cache-dir -r /home/myapp/requirements.txt
CMD ["python", "/home/myapp/consumer.py"]
