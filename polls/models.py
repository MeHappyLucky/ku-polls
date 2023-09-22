import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Question(models.Model):
    """ Represents a question in the poll application.

        Attributes:
        question_text (str): The text of the question.
        pub_date (datetime.datetime): The date and time when the question was published.
        end_date (datetime.datetime, optional): The date and time when the question ends (if set).
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('date ended', null=True)

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        """ Checks if the question was published recently. """
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
    """ Represents a choice associated with a question in the poll application.

        Attributes:
        question (Question): The question to which this choice belongs.
        choice_text (str): The text of the choice.
        votes (int): The number of votes received for this choice.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    # votes = models.IntegerField(default=0)

    @property
    def votes(self) -> int:
        """ Count the votes for this choice. """
        # count = Vote.objects.filter(choice=self).count()
        # count = self.vote_set.count()
        return self.vote_set.count()

    def __str__(self):
        return self.choice_text


class Vote(models.Model):
    """ Records a Vote of a Choice by a User. """
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
