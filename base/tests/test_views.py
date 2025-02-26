from django.test import TestCase, Client
from django.urls import reverse
from base.models import Room, Topic, Message, User
from django.contrib.auth import get_user_model


class BaseViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.topic = Topic.objects.create(name="Python")
        self.room = Room.objects.create(
            host=self.user,
            topic=self.topic,
            name="Django Room",
            description="A room to discuss Django.",
        )
        self.message = Message.objects.create(
            user=self.user,
            room=self.room,
            body="This is a test message.",
        )
        self.id = self.room.id

    # Helper method to log in the user
    def login_user(self):
        self.client.login(username="testuser", password="testpassword")


class LoginLogoutTest(BaseViewTest):
    def test_login_view_success(self):
        response = self.client.post(
            reverse("login"),
            {"username": "testuser", "password": "testpassword"},
            follow=True,
        )
        print(response.content.decode('utf-8'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login successful")
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_view_failure(self):
        response = self.client.post(
            reverse("login"),
            {"username": "wronguser", "password": "wrongpassword"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Error logging in. Please try again...")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_view(self):
        self.login_user()
        response = self.client.get(reverse("logout"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)


class RegisterTest(BaseViewTest):
    def test_register_view_success(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "password1": "securepassword123",
                "password2": "securepassword123",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("login"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_view_failure(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "password1": "short",
                "password2": "short",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "An error occurred during registration!")
        self.assertFalse(User.objects.filter(username="newuser").exists())


class HomeTest(BaseViewTest):
    def test_home_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Room")
        self.assertContains(response, "Python")


class RoomTest(BaseViewTest):
    def test_room_view(self):
        self.login_user()
        response = self.client.get(reverse("room", args=[self.room.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This is a test message.")

    def test_create_message_in_room(self):
        self.login_user()
        response = self.client.post(
            reverse("room", args=[self.room.id]),
            {"body": "New test message"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Message.objects.filter(body="New test message").exists())

    def test_toxic_message_rejection(self):
        self.login_user()
        response = self.client.post(
            reverse("room", args=[self.room.id]),
            {"body": "Go commit suicide bro"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This comment contains inappropriate content and cannot be posted.")
        self.assertFalse(Message.objects.filter(body="This is a toxic comment").exists())


class DeleteMessageTest(BaseViewTest):
    def test_delete_message(self):
        self.login_user()
        response = self.client.post(reverse("delete-message", args=[self.message.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Message.objects.filter(id=self.message.id).exists())


class CreateRoomTest(BaseViewTest):
    def test_create_room(self):
        self.login_user()
        response = self.client.post(
            reverse("create-room"),
            {
                "topic": self.topic.id,
                "name": "New Room",
                "description": "Description for new room.",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Room.objects.filter(name="New Room").exists())


class UpdateRoomTest(BaseViewTest):
    def test_update_room(self):
        self.login_user()
        response = self.client.post(
            reverse("update-room", args=[self.room.id]),
            {
                "topic": self.topic.id,
                "name": "Updated Room",
                "description": "Updated description.",
            },
            follow=True,
        )
        
        self.assertEqual(response.status_code, 200)
        self.room.refresh_from_db()
        self.assertEqual(Room.objects.get(id=self.id).name, "Updated Room")


class DeleteRoomTest(BaseViewTest):
    def test_delete_room(self):
        self.login_user()
        response = self.client.post(reverse("delete-room", args=[self.room.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Room.objects.filter(id=self.room.id).exists())


class UserProfileTest(BaseViewTest):
    def test_user_profile_view(self):
        response = self.client.get(reverse("profile", args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Room")