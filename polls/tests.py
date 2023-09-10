import datetime
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from .models import Question


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class IsPublishedTests(TestCase):

    def test_questions_with_future_pub_date(self):
        """ Questions in the future isn't published yet. """
        future_question = create_question('future question', 30)
        self.assertFalse(future_question.is_published())

    def test_questions_with_default_pub_date(self):
        """ Questions have default pub_date as today's date. """
        present_question = create_question('present question', 0)
        self.assertTrue(present_question.is_published())

    def test_questions_with_past_pub_date(self):
        """ Questions in the past is already published. """
        past_question = create_question('past question', -30)
        self.assertTrue(past_question.is_published())


def can_vote_test_create_question(question_text, pub_days, end_days):
    """ A copy of create_question to use in CanVoteTests """
    pub_time = timezone.now() + datetime.timedelta(days=pub_days)
    end_time = timezone.now() + datetime.timedelta(days=end_days)
    return Question.objects.create(question_text=question_text, pub_date=pub_time, end_date=end_time)


class CanVoteTests(TestCase):

    def test_cannot_vote_after_end_date(self):
        """ Cannot vote if the end_date is in the past. """
        past_question = can_vote_test_create_question('past question', -30, -20)
        self.assertFalse(past_question.can_vote())

    def test_cannot_vote_future_question(self):
        """ Cannot vote if the question is in the future. """
        future_question = can_vote_test_create_question('future question', 20, 30)
        self.assertFalse(future_question.can_vote())

    def test_can_vote_if_end_date_is_null(self):
        """ Can vote if the end_date is None. """
        no_end_question = can_vote_test_create_question('no end question', 0, 0)
        no_end_question.end_date = None
        self.assertTrue(no_end_question.can_vote())

    def test_can_vote_unexpired_questions(self):
        """ Can vote on questions that are active. """
        active_question = can_vote_test_create_question('active question', -10, 10)
        self.assertTrue(active_question.can_vote())
