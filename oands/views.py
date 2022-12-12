from django.shortcuts import render

# import pytesseract to convert text in image to string
import pytesseract

# import summarize to summarize the ocred text
#from summarizer import summarizer

from .forms import ImageUpload
import os

# import Image from PIL to read image
from PIL import Image
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import urllib.request

import base64
import sys
# Create your views here.
@csrf_exempt
def index(request):
    text = ""
    message = ""
    eng_to_kor=""
    mode=""
    if request.method == 'POST':
        form = ImageUpload(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                image = request.FILES['image'].decode('urf-8')
                image = image.name
                path = settings.MEDIA_ROOT
                pathz = path + "/images/" + image

                mode=request.data.get('mode')
                text = pytesseract.image_to_string(Image.open(pathz), lang='kor+eng')
                text = text.encode("ascii", "ignore")
                text = text.decode()

                # translate eng to kor through Papago API
                client_id = "7cyuDLUY3kSNzmFs_i88" # 개발자센터에서 발급받은 Client ID 값
                client_secret = "NMYcZYMSNp" # 개발자센터에서 발급받은 Client Secret 값
                encText = urllib.parse.quote(text)
                data = "source=en&target=ko&text=" + encText
                url = "https://openapi.naver.com/v1/papago/n2mt"
                request = urllib.request.Request(url)
                request.add_header("X-Naver-Client-Id",client_id)
                request.add_header("X-Naver-Client-Secret",client_secret)
                response = urllib.request.urlopen(request, data=data.encode("utf-8"))
                rescode = response.getcode()

                if(rescode==200):
                    response_body = response.read()
                    result=response_body.decode('utf-8')
                    d=json.loads(result)
                    eng_to_kor = d['message']['result']['translatedText']
                    # print(response_body)
                    # print(eng_to_kor)
                else:
                    eng_to_kor = "error code: "+rescode

                # Summary (0.1% of the original content).
                # summarized_text = summarizer.summarize('',text, count=2)
                # os.remove(pathz)
            except:
                message = "check your filename and ensure it doesn't have any space or check if it has any text"

    context = {
        'text': text,
        'message': message,
        'eng_to_kor': eng_to_kor,
        'mode': mode
    }
    # get(context)
    # return render(request, 'formpage.html', context)
    return JsonResponse(context)
# def get(context):
#     return JsonResponse(context)

