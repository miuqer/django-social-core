from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import MyUser
from direct.models import ChatRoom, DirectMessage


class DirectViewsTestCase(TestCase):
    def setUp(self):
        self.user1 = MyUser.objects.create_user(
            username="astronaut1",
            phone_number="09121111111",
            password="testpassword123",
        )
        self.user2 = MyUser.objects.create_user(
            username="astronaut2",
            phone_number="09122222222",
            password="testpassword123",
        )
        self.user3 = MyUser.objects.create_user(
            username="astronaut3",
            phone_number="09123333333",
            password="testpassword123",
        )
        self.client1 = Client()
        self.client1.force_login(self.user1)

    def test_inbox_empty_state(self):
        """وقتی کاربر اتاقی ندارد، صفحه خالی با وضعیت مناسب نمایش داده می‌شود"""
        response = self.client1.get(reverse("direct:inbox"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "direct/chat_room.html")
        self.assertContains(response, "مرکز ارتباطات و پیام‌رسانی مداری")

    def test_start_chat_and_redirect(self):
        """آغاز گفتگو با کاربر دیگر، اتاق را ساخته و کاربر را هدایت می‌کند"""
        response = self.client1.get(reverse("direct:start_chat", args=[self.user2.id]))
        self.assertEqual(response.status_code, 302)
        room = (
            ChatRoom.objects.filter(users=self.user1).filter(users=self.user2).first()
        )
        self.assertIsNotNone(room)
        self.assertRedirects(response, reverse("direct:chat_room", args=[room.id]))

    def test_chat_room_accessible_by_participant(self):
        """فضانورد عضو اتاق باید بتواند به اتاق دسترسی داشته باشد"""
        room = ChatRoom.objects.create()
        room.users.add(self.user1, self.user2)
        DirectMessage.objects.create(
            chatroom=room, sender=self.user2, text="سلام بر مدار کیهانی"
        )

        response = self.client1.get(reverse("direct:chat_room", args=[room.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "direct/chat_room.html")
        self.assertContains(response, "astronaut2")
        self.assertContains(response, "سلام بر مدار کیهانی")

    def test_chat_room_unauthorized_shows_403(self):
        """کاربری که عضو اتاق نیست باید با خطای ۴۰۳ و قالب oh_no.html مواجه شود"""
        room = ChatRoom.objects.create()
        room.users.add(self.user2, self.user3)

        response = self.client1.get(reverse("direct:chat_room", args=[room.id]))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "direct/oh_no.html")
        self.assertContains(response, "خطای دسترسی امنیتی ۴۰۳", status_code=403)
