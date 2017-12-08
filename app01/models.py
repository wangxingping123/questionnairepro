from django.db import models

# Create your models here.

class Userifo(models.Model):
    '''用户表'''
    username=models.CharField(max_length=32)
    password=models.CharField(max_length=32)

    def __str__(self):
        return self.username

class ClassList(models.Model):
    """
    班级表
    """
    title = models.CharField(max_length=32)

    def __str__(self):
        return self.title


class Student(models.Model):
    """
    学生表
    """
    user = models.CharField(max_length=32)
    pwd = models.CharField(max_length=32)
    cls = models.ForeignKey(to="ClassList")

    def __str__(self):
        return self.user


class Questionnaire(models.Model):
    """
    问卷表
    """
    title = models.CharField(max_length=64)
    cls = models.ForeignKey(to="ClassList")
    creator = models.ForeignKey(to="Userifo")

    def __str__(self):
        return self.title


class Question(models.Model):
    """
    问题
    """
    questionnaire=models.ForeignKey(to="Questionnaire")
    caption = models.CharField(max_length=64)
    question_types = (
        (1,'打分(1~10)'),
        (2,'单选'),
        (3,'评价'),
    )
    type = models.IntegerField(choices=question_types)

    def __str__(self):
        return self.caption


class Option(models.Model):
    """
    单选题的选项
    """
    name = models.CharField(verbose_name='选项名称',max_length=32)
    score = models.IntegerField(verbose_name='选项对应的分值')
    question = models.ForeignKey(to="Question")

    def __str__(self):
        return self.name


class Answer(models.Model):
    """
    回答
    """
    student = models.ForeignKey(to="Student")
    question = models.ForeignKey(to="Question")


    val = models.IntegerField(null=True,blank=True)
    oid=models.IntegerField(null=True,blank=True)
    content = models.CharField(max_length=255,null=True,blank=True)

