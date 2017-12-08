from django.shortcuts import render, HttpResponse, redirect
from app01 import models
import json

from django.forms import ModelForm
from django.forms import widgets as wd
from django.forms import ValidationError
def func(val):
    '''判断学生输入的评论内容是否够15字'''
    if len(val)<15:
        raise ValidationError("不能少于15字")

# Create your views here.
class QuestionForm(ModelForm):
    class Meta:
        model = models.Question
        fields = ["caption", "type"]
        widgets = {
            "caption": wd.Textarea(attrs={"rows": "2", "cols": "80", "class": "form-control"}),
            "type": wd.Select(attrs={"class": "select_type"})
        }


class OptionForm(ModelForm):
    class Meta:
        model = models.Option
        fields = ["name", "score"]


class QuestionnaireForm(ModelForm):
    class Meta:
        model = models.Questionnaire
        fields = "__all__"
        widgets = {
            "title": wd.TextInput(attrs={"class": "form-control"}),
            "cls": wd.Select(attrs={"class": "form-control"}),
            "creator": wd.Select(attrs={"class": "form-control"}),
        }


def login(request):
    if request.is_ajax():
        username = request.POST.get("username")
        password = request.POST.get("password")
        data = {"flag": False}
        user = models.Userifo.objects.filter(username=username, password=password)
        if user:
            data["flag"] = True

        return HttpResponse(json.dumps(data))

    return render(request, "login.html")


def stu_login(request):
    if request.is_ajax():
        username = request.POST.get("username")
        password = request.POST.get("password")
        data = {"flag": False}
        user = models.Student.objects.filter(user=username, pwd=password).first()
        if user:
            request.session["student_info"] = {"stu": user.user, "stu_id": user.id}
            data["flag"] = True

        return HttpResponse(json.dumps(data))

    return render(request, "stu_login.html")


def stu_index(request):
    return render(request, "stu_index.html")


def index(request):
    if request.method == "POST":
        data = {"flag": False}
        form = QuestionnaireForm(data=request.POST)
        if form.is_valid():
            form.save()
            data["flag"] = True
            return HttpResponse(json.dumps(data))
        else:
            data["error"] = form.errors
            return HttpResponse(json.dumps(data))

    question_naire_obj = models.Questionnaire.objects.all()
    for i in question_naire_obj:
        count=models.Answer.objects.filter(question__questionnaire=i).values("student_id").distinct().count()
        i.count=count

    return render(request, "index.html", {"question_naire_obj": question_naire_obj })


def editor_ques(request, questionnaire_id):
    '''编辑问卷调查表问题'''
    question_objs = models.Question.objects.filter(questionnaire_id=questionnaire_id)
    question_id_list = [obj.id for obj in question_objs]
    if request.is_ajax():
        questions_list = json.loads(request.body.decode("utf8"))

        for question in questions_list:
            # 判断问题是在更新还是在添加
            if question.get("qid") != 'None' and question.get("qid") and int(question.get("qid")) in question_id_list:
                models.Question.objects.filter(id=int(question.get("qid"))).update(
                    caption=question.get("qtitle"),
                    type=int(question.get("qtype")))
                for option in question.get("options", ''):
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
                question_obj = models.Question.objects.create(questionnaire_id=questionnaire_id,
                                                              caption=question.get("qtitle"),
                                                              type=int(question.get("qtype")))

                for option in question.get("options", ''):
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

    # get请求 ，获取数据传到页面进行渲染
    def inner():
        if question_objs:
            for obj in question_objs:
                form = QuestionForm(instance=obj)
                data = {"form": form, "qid": obj.id, "options": None, "class": "hide"}
                if obj.type == 2:
                    data["class"] = ''

                    def inner_loop(id):
                        options = models.Option.objects.filter(question_id=id)
                        for option in options:
                            form = OptionForm(instance=option)
                            yield {"form": form, "option_id": option.id}

                    data["options"] = inner_loop(obj.id)

                yield data

        else:
            yield {"form": QuestionForm(), "qid": None, "options": None, "class": "hide"}

    return render(request, "editor_ques.html", {"data": inner(), "questionnaire_id": questionnaire_id})


def del_question(request):
    data = {"flag": False}
    qid = request.GET.get("qid")
    if models.Question.objects.filter(id=qid).delete():
        data["flag"] = True
    return HttpResponse(json.dumps(data))


def fill_naire(request, class_id, naire_id):
    if not request.session["student_info"].get("stu_id"):
        return redirect("/stu_login/")
    student_id = request.session["student_info"].get("stu_id")
    s1 = models.Student.objects.filter(id=student_id, cls_id=class_id).count()
    if not s1:  # 判断是否是本次问卷班级的学生
        return HttpResponse("你只能填写你所在班级的问卷")
    s2 = models.Answer.objects.filter(student_id=student_id, question__questionnaire_id=naire_id).count()
    if s2:  # 判断是否已经提交过了
        return HttpResponse("你已经填写过了")

    # 所有判断都通过的情况下就显示当前问卷的问题
    from django.forms import widgets, Form, fields
    question_list = models.Question.objects.filter(questionnaire_id=naire_id)
    fields_dic = {}  # 创建一个字典用来存字段
    for question in question_list:
        if question.type == 1:
            fields_dic['val_%s' % question.id] = fields.ChoiceField(
                choices=[(i, i) for i in range(1, 11)],
                widget=widgets.RadioSelect(),
                label=question.caption,
                error_messages={"required": "此字段补不能为空"})
        elif question.type == 2:
            fields_dic['oid_%s' % question.id] = fields.ChoiceField(
                choices=models.Option.objects.filter(question_id=question.id).values_list("id","name"),
                widget=widgets.RadioSelect(),
                label=question.caption,
                error_messages={"required": "此字段补不能为空"})
        elif question.type == 3:
            fields_dic['content_%s' % question.id] = fields.CharField(
                widget=widgets.Textarea(attrs={"rows":"5","cols":"80"}),
                validators=[func,],
                label=question.caption,
                error_messages={"required": "此字段补不能为空"})

    MytestForm = type("MytestForm", (Form,), fields_dic)

    if request.method=="GET":
        form = MytestForm()

    else:
        print(request.POST)
        form=MytestForm(request.POST)
        if form.is_valid():
            objs=[]
            for i,v in form.cleaned_data.items():
                name,id=i.split('_',1)
                answer_dic={"student_id":student_id,"question_id":id,
                            name:v}
                obj=models.Answer(**answer_dic)
                objs.append(obj)
            models.Answer.objects.bulk_create(objs)
            return HttpResponse("你已成功提交，感谢的你反馈")



    return render(request, "question_naire.html", {"forms": form})
