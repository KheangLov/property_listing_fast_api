FROM python:3.8
ADD requirements.txt /requirements.txt
ADD main.py /main.py
ADD okteto-stack.yaml /okteto-stack.yaml
RUN pip install -r requirements.txt
EXPOSE 8080
COPY ./images images
COPY ./base64_to_file.py base64_to_file.py
COPY ./database.py database.py
COPY ./model.py model.py
COPY ./hash.py hash.py
COPY ./helper.py helper.py
COPY ./routes routes
COPY ./kh_address.py kh_address.py
COPY ./listing.py listing.py
COPY ./main.py main.py
COPY ./property.py property.py
COPY ./token_auth.py token_auth.py
COPY ./user.py user.py
CMD ["python3", "main.py"]