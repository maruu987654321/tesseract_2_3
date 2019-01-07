#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request
import pytesseract
import os
from collections import Counter
import time
import pprint
import cv2
from werkzeug.utils import secure_filename
from apiclient.discovery import build
import spacy
from flask import Flask, render_template

nlp = spacy.load('en_core_web_sm')

try:
    import Image
except ImportError:
    from PIL import Image

my_api_key = "AIzaSyDqLGTRpW5sdY1NTgQekhWFAu35vF8SExU"
my_cse_id = "004140793999849389858:jmh9-8crlce"


def recog(self, photopath):
    #data = pickle.loads(open("encodings-nip.pickle", "rb").read())
    filepath = 'static/img/IMG_3853.jpg'

    # photo = str(photo)
    image = cv2.imread(photopath)
    #print(image.shape)
    #rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


    return image

def create_image(photograph):
    #original_file = file
    image_array = []
    #photograph#'2.jpg'#
    # safe_join(directory, file)



    accepted_words = ""
    #for image in image_array:
    #    accepted_words += process_image(image)
    accepted_words += process_image(photograph)
    return accepted_words

def process_image(image):
    #create greyscale variant of the image, apply thresh

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255,
                         cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # TODO Matt Check performance when applying median blur compared to just thresh (directly below). blur seems advantageous
    gray = cv2.medianBlur(gray, 3)

    # write the grayscale image to disk as a temp file ready to apply ocr
    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, gray)

    # load img as PIL image, apply OCR, delete temp file
    text = pytesseract.image_to_string(Image.open(filename))
    #os.remove(filename)

    accepted_words = []
    incorrect_words = []

    words = text.replace('\n', ' ')
    #words = text.split(' ')
    words = text.splitlines()
    final_words = ' '.join(words)

    #words = filter(None,words)

    #[accepted_words.append(s) if d.check((s)) else incorrect_words.append(handle_spell_check(s)) for s in words]
    #accepted_words = words

   # final_words = accepted_words + incorrect_words #combine accepted and cleaned incorrect words
   # final_words = filter(lambda x: len(x) > 1 , final_words)  # remove 1 char length and removes words with no spelling corrections
    return final_words


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, dateRestrict='d14', cx=cse_id, **kwargs).execute()
    #print("RES111:",res)
    for item in res:
        pass#print ("item: ", item)
    time.sleep(1)
    #print("items in res, ",('items' in res))

    #links = [item['title'] for item in res['items']]
    #return links
    #print(res)
    #pprint.pprint(res)
    results = []
    if 'items' in res:
        results.append( res['items'])
    return res

def extended_is_stop(token):
    stop_words = nlp.Defaults.stop_words
    return token.is_stop or token.lower_ in stop_words or token.lemma_ in stop_words




def do_nlp(nlp_string):
    txt = nlp(nlp_string)
    #txt = nlp(u"""'DUP threat to abandon support for May in vote. PM faces struggle to survive in confidence motion. Theresa May was under fresh pressure last night as the DUP threatened to abandon her in a confidence vote if she failed to get her Brexit vote through parliament.""")
    txtnlp = ""

    words = [token.text for token in txt if token.is_stop != True and token.is_punct != True and extended_is_stop(
        token) != True and token.text.isalpha()]

    for ent in txt.ents:
        txtnlp += ent.text
    common_words = words
    persons = []
    for ent in txt.ents:
        if ent.label_ == 'PERSON' or ent.label_ == 'GPE':
            # print(ent.text, ent.start_char, ent.end_char, ent.label_)
            persons.append(ent.text)
    person_freq = Counter(persons)
    finalised_list = [0]
    for common in common_words:
        is_similar = False
        for person in persons:
            if common in person:
                is_similar = True
        if is_similar == False:
            finalised_list.append((common))
    finalised_list_freq = Counter(finalised_list)
    finalised_list_freq1 = finalised_list_freq.most_common(4)

    finalised_persons = person_freq.most_common(3)
    combined_for_search = ""

    for word in finalised_list_freq1:
        combined_for_search += str(word[0]) + ' '

    for word in finalised_persons:
        combined_for_search += word[0] + ' '
    return combined_for_search

app = Flask(__name__)

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def show():
    if request.method == 'POST':
        f = request.files['file']
        f.save('vor/' + secure_filename('a'+f.filename))
        image = cv2.imread('./vor/a'+f.filename)
        returner = create_image(image)
        accepted_words = ""
        search_string = do_nlp(returner)
        return search_string
        print("SEARCHH STRING: ",search_string)
        return jsonify(results)
   
   

if __name__ == '__main__':
    app.run(debug=True)
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
