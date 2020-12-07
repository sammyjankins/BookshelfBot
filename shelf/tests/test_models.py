from django.contrib.auth.models import User
from django.test import TestCase
from shelf.models import Profile


class ProfileModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        User.objects.create_user(username='test_user')
        print(User.objects.all())
        Profile.objects.create(user=User.objects.first(), tele_id='1234567890')

    def setUp(self):
        self.profile = Profile.objects.get(id=1)

    def test_last_book(self):
        self.assertEqual(self.profile.last_book, None)

    def test_last_shelf(self):
        self.assertEqual(self.profile.last_shelf, None)

    def test_state(self):
        self.assertEqual(self.profile.state, 0)

    def test_tele_id_length(self):
        max_length = self.profile._meta.get_field('tele_id').max_length
        self.assertEquals(max_length, 15)
