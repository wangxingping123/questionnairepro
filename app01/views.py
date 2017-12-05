from django.shortcuts import render,HttpResponse
from app01 import models
import json

from django.forms import Form,widgets,fields

# Create your views here.

class QuestionForm(Form):
    caption=fields.CharField(widget=widgets.Textarea(attrs={"cols":"80","rows":"2"}))
    type=fields.ChoiceField(choices=models.Question.question_types,widget=widgets.Select(attrs={"class":"select_type"}))

def login(request):

    if request.is_ajax():
        username=request.POST.get("username")
        password=request.POST.get("password")
        data={"flag":False}
        user=models.Userifo.objects.filter(username=username,password=password)
        if user:
            data["flag"]=True

        return HttpResponse(json.dumps(data))


    return render(request,"login.html")

def index(request):


    question_naire_obj=models.Questionnaire.objects.all()
    return render(request,"index.html",{"question_naire_obj":question_naire_obj})


def editor_ques(request,questionnaire_id):
    '''编辑问卷调查表问题'''


    questions=models.Question.objects.filter(questionnaire_id=questionnaire_id)

    form =QuestionForm()


    return render(request,"editor_ques.html",{"questions":questions,"form":form})

