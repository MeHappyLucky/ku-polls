import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('date ended', null=True)

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    
    def is_published(self) -> bool:
        """ Checking if the question is published.
        returns True if the current date is on or after the 'date published'
        """
        now = timezone.now()
        return now >= self.pub_date

    def can_vote(self) -> bool:
        """ Checking if the question is able to be voted.
        returns True if voting is allowed for this question.
        That means, the current date/time is between the pub_date and end_date.
        If end_date is null then can vote anytime after pub_date.
        """
        now = timezone.now()
        if self.end_date is None:
            return self.is_published()
        if self.is_published():
            return now <= self.end_date


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
