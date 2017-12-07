from django.shortcuts import render,HttpResponse
from app01 import models
import json

from django.forms import ModelForm
from django.forms import widgets as wd

# Create your views here.
class QuestionForm(ModelForm):
    class Meta:
        model = models.Question
        fields = ["caption","type"]
        widgets={
            "caption":wd.Textarea(attrs={"rows":"2","cols":"80","class":"form-control"}),
            "type":wd.Select(attrs={"class":"select_type"})
            }

class OptionForm(ModelForm):
    class Meta:
        model =models.Option
        fields=["name","score"]

class QuestionnaireForm(ModelForm):
    class Meta:
        model =models.Questionnaire
        fields ="__all__"
        widgets={
            "title":wd.TextInput(attrs={"class":"form-control"}),
            "cls":wd.Select(attrs={"class": "form-control"}),
            "creator": wd.Select(attrs={"class": "form-control"}),
        }


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
    if request.method=="POST":
        data={"flag":False}
        form=QuestionnaireForm(data=request.POST)
        if form.is_valid():
            form.save()
            data["flag"]=True
            return HttpResponse(json.dumps(data))
        else:
            data["error"]=form.errors
            return HttpResponse(json.dumps(data))


    question_naire_obj=models.Questionnaire.objects.all()
    form=QuestionnaireForm()
    return render(request,"index.html",{"question_naire_obj":question_naire_obj,"form":form})

def editor_ques(request,questionnaire_id):
    '''编辑问卷调查表问题'''
    question_objs = models.Question.objects.filter(questionnaire_id=questionnaire_id)

    if request.is_ajax():
        questions_list=json.loads(request.body.decode("utf8"))

        for question in questions_list:
            #判断问题是在更新还是在添加
            if question.get("qid") and question.get("qid") != 'None':
                models.Question.objects.filter(id=int(question.get("qid"))).update(questionnaire_id=questionnaire_id,
                                                         caption=question.get("qtitle"),
                                                         type=int(question.get("qtype")))
                for option in question.get("options",''):
                    if option.get("option_id"):
                        models.Option.objects.filter(id=int(option.get("option_id"))).update(
                            name=option.get("option_name"),
                            score=option.get("option_score"),
                            question_id=int(question.get("qid"))
                        )
                    else:
                        models.Option.objects.create(
                            name=option.get("option_name"),
                            score=option.get("option_score"),
                            question_id=int(int(question.get("qid")))
                        )
            else:
                question_obj=models.Question.objects.create(questionnaire_id=questionnaire_id,
                                               caption=question.get("qtitle"),
                                        type=int(question.get("qtype")))

                for option in question.get("options",''):
                    if option.get("option_id"):
                        models.Option.objects.filter(id=int(option.get("option_id"))).update(
                            name=option.get("option_name"),
                            score=option.get("option_score"),
                            question_id=int(question.get("qid"))
                        )
                    else:
                        models.Option.objects.create(
                            name=option.get("option_name"),
                            score=option.get("option_score"),
                            question_id=question_obj.id
                        )



        return HttpResponse(123)
    #get请求 ，获取数据传到页面进行渲染
    def inner():
        if question_objs:
            for obj in question_objs:
                form=QuestionForm(instance=obj)
                data= {"form":form,"qid":obj.id,"options":None,"class":"hide"}
                if obj.type==2:
                    data["class"]=''
                    def inner_loop(id):
                        options=models.Option.objects.filter(question_id=id)
                        for option in options:
                            form=OptionForm(instance=option)
                            yield {"form":form,"option_id":option.id}
                    data["options"]=inner_loop(obj.id)

                yield data

        else:
            yield {"form":QuestionForm(),"qid":None,"options":None,"class":"hide"}


    return render(request,"editor_ques.html",{"data":inner(),"questionnaire_id":questionnaire_id})


def del_question(request):
    data={"flag":False}
    qid=request.GET.get("qid")
    if models.Question.objects.filter(id=qid).delete():
        data["flag"]=True
    return HttpResponse(json.dumps(data))