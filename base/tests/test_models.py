from django.test import TestCase
from base.models import Topic, Room, Message
from django.contrib.auth.models import User
from django.utils import timezone


class TopicModelTest(TestCase):
    def setUp(self):
        self.topic = Topic.objects.create(name="Python")

    def test_topic_creation(self):
        self.assertEqual(str(self.topic), "Python")
        self.assertTrue(isinstance(self.topic, Topic))

    def test_topic_string_representation(self):
        self.assertEqual(str(self.topic), "Python")


class RoomModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.topic = Topic.objects.create(name="Python")
        self.room = Room.objects.create(
            host=self.user,
            topic=self.topic,
            name="Django Room",
            description="A room to discuss Django.",
        )

    def test_room_creation(self):
        self.assertEqual(str(self.room), "Django Room")
        self.assertEqual(self.room.host.username, "testuser")
        self.assertEqual(self.room.topic.name, "Python")
        self.assertIsNotNone(self.room.updated)
        self.assertIsNotNone(self.room.created)

    def test_room_ordering(self):
        # Create two rooms with different timestamps
        room1 = Room.objects.create(
            host=self.user,
            topic=self.topic,
            name="Room 1",
            description="Description for Room 1.",
        )
        room2 = Room.objects.create(
            host=self.user,
            topic=self.topic,
            name="Room 2",
            description="Description for Room 2.",
        )
        # Ensure ordering is by updated and created fields
        rooms = Room.objects.all()
        self.assertEqual(rooms[0], room2)
        self.assertEqual(rooms[1], room1)

    def test_room_participants(self):
        user2 = User.objects.create_user(username="testuser2", password="testpassword")
        self.room.participants.add(user2)
        self.assertIn(user2, self.room.participants.all())


class MessageModelTest(TestCase):
    def setUp(self):
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

    def test_message_creation(self):
        self.assertEqual(str(self.message), "This is a test message.")
        self.assertEqual(self.message.user.username, "testuser")
        self.assertEqual(self.message.room.name, "Django Room")
        self.assertIsNotNone(self.message.updated)
        self.assertIsNotNone(self.message.created)

    def test_message_ordering(self):
        # Create two messages with different timestamps
        message1 = Message.objects.create(
            user=self.user,
            room=self.room,
            body="Message 1",
        )
        message2 = Message.objects.create(
            user=self.user,
            room=self.room,
            body="Message 2",
        )
        # Ensure ordering is by updated and created fields
        messages = Message.objects.all()
        self.assertEqual(messages[0], message2)
        self.assertEqual(messages[1], message1)