from django.test import TestCase
from base.forms import RoomForm, SignUpForm
from base.models import Room, Topic, User


class RoomFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.topic = Topic.objects.create(name="Python")

    def test_room_form_valid_data(self):
        data = {
            "host": self.user.id,
            "topic": self.topic.id,
            "name": "Django Room",
            "description": "A room to discuss Django.",
        }
        form = RoomForm(data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_room_form_invalid_data(self):
        data = {
            "host": self.user.id,
            "topic": "",  # Missing topic
            "name": "",
            "description": "",
        }
        form = RoomForm(data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("topic", form.errors)
        self.assertIn("name", form.errors)

    def test_room_form_host_field_for_non_admin(self):
        form = RoomForm(user=self.user)
        self.assertTrue(form.fields["host"].disabled)  # Host field should be disabled for non-admin users

    def test_room_form_host_field_for_admin(self):
        admin_user = User.objects.create_superuser(username="admin", password="adminpassword")
        form = RoomForm(user=admin_user)
        self.assertFalse(form.fields["host"].disabled)  # Host field should not be disabled for admin users
        self.assertEqual(len(form.fields["host"].queryset), User.objects.count())  # Admin can choose any user


class SignUpFormTest(TestCase):
    def test_signup_form_valid_data(self):
        data = {
            "username": "newuser",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password1": "securepassword123",
            "password2": "securepassword123",
        }
        form = SignUpForm(data)
        self.assertTrue(form.is_valid())

    def test_signup_form_invalid_data(self):
        data = {
            "username": "",  # Missing username
            "first_name": "John",
            "last_name": "Doe",
            "email": "invalid-email",  # Invalid email
            "password1": "short",  # Short password
            "password2": "notmatching",  # Passwords don't match
        }
        form = SignUpForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertIn("email", form.errors)
        self.assertIn("password2", form.errors)

    def test_signup_form_password_mismatch(self):
        data = {
            "username": "newuser",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password1": "securepassword123",
            "password2": "differentpassword",  # Passwords don't match
        }
        form = SignUpForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_signup_form_help_text(self):
        form = SignUpForm()
        self.assertIn("Required. 150 characters or fewer.", form.fields["username"].help_text)
        self.assertIn("Your password can't be too similar to your other personal information.", form.fields["password1"].help_text)
        self.assertIn("Enter the same password as before, for verification.", form.fields["password2"].help_text)