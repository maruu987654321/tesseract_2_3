FROM gcr.io/google-appengine/python
RUN apt-get update &&  apt-get install -y \
    tesseract-ocr \
    libtesseract-dev
# Create a virtualenv for dependencies. This isolates these packages from
# system-level packages.
RUN virtualenv /env -p python3.6
# Setting these environment variables are the same as running
# source /env/bin/activate.
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH
# Copy the application's requirements.txt and run pip to install all
# dependencies into the virtualenv.
ADD requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt
RUN pip3 install spacy
RUN python3 -m spacy download en_core_web_sm
# Add the application source code.
ADD . /app
# Run a WSGI server to serve the application. gunicorn must be declared as
# a dependency in requirements.txt.
CMD gunicorn -b :$PORT main:app
