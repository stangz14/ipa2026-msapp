FROM python
WORKDIR /home/myapp
COPY ./templates/* /home/myapp/templates/
COPY ./static/* /home/myapp/static/
COPY ./app.py /home/myapp/
COPY ./requirements.txt /home/myapp/
RUN pip install -r /home/myapp/requirements.txt
CMD ["python", "/home/myapp/app.py"]
EXPOSE 8080