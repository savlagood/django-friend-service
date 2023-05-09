from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import User, FriendRequest


class UserListViewTest(APITestCase):

	def setUp(self):
		self.url = reverse('socnet:user-list')

	def test_get_method_empty_list(self):
		"""Tests GET method - returns list of users - empty list"""
		response = self.client.get(self.url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.json(), [])

	def test_get_method_list_of_multiple_users(self):
		"""Tests GET method on non e,pty list"""
		User(username="Andrew").save()
		User(username="Pavel").save()

		data = [{"id": user.id, "username": user.username} for user in User.objects.all()]

		response = self.client.get(self.url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.json(), data)

	def test_post_method(self):
		"""Tests POST method - must returns non empty list"""
		response = self.client.post(self.url, {"username": "Maxim"}, format='json')

		self.assertEqual(User.objects.count(), 1)

		user = User.objects.all()[0]

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.json(), {
			"id": user.id,
			"friends": [],
			"outgoing_requests": [],
			"incoming_requests": [],
			"username": "Maxim",
		})

	def test_post_method_bad_request(self):
		"""Tests wrong POST method"""
		response = self.client.post(self.url, {"name": "Maxim"}, format='json')

		self.assertEqual(User.objects.count(), 0)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(list(response.json().keys()), ['detail'])


class UserDetailViewTest(APITestCase):

	def get_url(self, user_id):
		return reverse('socnet:user-detail', kwargs={'user_id': user_id})

	def test_get_method(self):
		""""""
		user = User(username="Andrew")
		user.save()

		response = self.client.get(self.get_url(user.id))

		self.assertEqual(User.objects.count(), 1)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.json(), {
			"id": user.id,
			"friends": [],
			"outgoing_requests": [],
			"incoming_requests": [],
			"username": user.username,
		})

	def test_get_method_without_users(self):
		""""""
		response = self.client.get(self.get_url(1))

		self.assertEqual(User.objects.count(), 0)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(list(response.json().keys()), ['detail'])

	def test_delete_method(self):
		""""""
		user = User(username="Andrew")
		user.save()

		response = self.client.delete(self.get_url(user.id))

		self.assertEqual(User.objects.count(), 0)
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(response.data, None)

	def test_delete_method_empty_user(self):
		""""""
		user = User(username="Andrew")
		user.save()

		response = self.client.delete(self.get_url(user.id + 1))

		self.assertEqual(User.objects.count(), 1)
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(list(response.json().keys()), ['detail'])


class FriendListViewTest(APITestCase):

	def get_url(self, user_id):
		return reverse('socnet:friend-list', kwargs={'user_id': user_id})

	def create_users_and_requests(self):
		self.user1 = User(username="Andrew")
		self.user2 = User(username="Pavel")
		self.user3 = User(username="Elon")

		self.user1.save()
		self.user2.save()
		self.user3.save()

		FriendRequest(from_user=self.user1, to_user=self.user2).save()
		FriendRequest(from_user=self.user2, to_user=self.user1).save()
		FriendRequest(from_user=self.user2, to_user=self.user1).save()

	def test_get_method_no_friends(self):
		user = User(username="Andrew")
		user.save()

		response = self.client.get(self.get_url(user.id))

		self.assertEqual(User.objects.count(), 1)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.json(), [])

	def test_get_method_with_friends(self):
		self.create_users_and_requests()

		response = self.client.get(self.get_url(self.user1.id))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.json(), [{
			'id': self.user2.id,
			'username': self.user2.username,
		}])

	def test_get_method_empty_user(self):
		""""""
		response = self.client.get(self.get_url(1))

		self.assertEqual(User.objects.count(), 0)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(list(response.json().keys()), ['detail'])


class FriendDeleteViewTest(APITestCase):

	def get_url(self, user_id, friend_id):
		return reverse('socnet:firend-delete',
						kwargs={'user_id': user_id, 'friend_id': friend_id})

	def create_users_and_requests(self):
		self.user1 = User(username="Andrew")
		self.user2 = User(username="Pavel")
		self.user3 = User(username="Elon")

		self.user1.save()
		self.user2.save()
		self.user3.save()

		FriendRequest(from_user=self.user1, to_user=self.user2).save()
		FriendRequest(from_user=self.user2, to_user=self.user1).save()
		FriendRequest(from_user=self.user2, to_user=self.user3).save()

	def test_delete_method(self):
		self.create_users_and_requests()

		response = self.client.delete(self.get_url(self.user1.id, self.user1.get_friends()[0].id))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 2)

		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(response.data, None)

	def test_delete_method_empty_user(self):
		self.create_users_and_requests()

		response = self.client.delete(self.get_url(self.user1.id, 122))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(list(response.json().keys()), ['detail'])

	def test_delete_method_non_friend(self):
		self.create_users_and_requests()

		response = self.client.delete(self.get_url(self.user1.id, self.user3.id))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(list(response.json().keys()), ['detail'])


class OutgoingRequestListViewTest(APITestCase):

	def get_url(self, user_id):
		return reverse('socnet:outgoing-request-list', kwargs={'user_id': user_id})

	def create_users_and_requests(self):
		self.user1 = User(username="Andrew")
		self.user2 = User(username="Pavel")
		self.user3 = User(username="Elon")

		self.user1.save()
		self.user2.save()
		self.user3.save()

		FriendRequest(from_user=self.user1, to_user=self.user2).save()
		FriendRequest(from_user=self.user2, to_user=self.user1).save()
		FriendRequest(from_user=self.user2, to_user=self.user3).save()

	def test_get_method(self):
		self.create_users_and_requests()

		response = self.client.get(self.get_url(self.user2.id))
		friend_request = FriendRequest.objects.get(from_user=self.user2, to_user=self.user3)

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.json(), [{
			'id': friend_request.id,
			'from_user': friend_request.from_user.id,
			'to_user': friend_request.to_user.id,
		}])

	def test_get_method_no_requests(self):
		self.create_users_and_requests()

		response = self.client.get(self.get_url(self.user1.id))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.json(), [])

	def test_get_method_no_user(self):
		self.create_users_and_requests()

		response = self.client.get(self.get_url(self.user3.id + 256))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(list(response.json().keys()), ['detail'])

	def test_post_method(self):
		self.create_users_and_requests()

		response = self.client.post(self.get_url(self.user1.id), {'user_id': self.user3.id}, format='json')
		friend_request = FriendRequest.objects.get(from_user=self.user1, to_user=self.user3)

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 4)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.json(), {
			'id': friend_request.id,
			'from_user': friend_request.from_user.id,
			'to_user': friend_request.to_user.id,
		})

	def test_post_method_user1_with_user1(self):
		self.create_users_and_requests()

		response = self.client.post(self.get_url(self.user1.id), {'user_id': self.user1.id}, format='json')

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(list(response.json().keys()), ['detail'])

	def test_post_method_no_user(self):
		self.create_users_and_requests()

		response = self.client.post(self.get_url(self.user3.id + 256), {'user_id': self.user3.id}, format='json')

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(list(response.json().keys()), ['detail'])


class OutgoingRequestDeleteViewTest(APITestCase):

	def get_url(self, user_id, request_id):
		return reverse('socnet:outgoing-request-delete', kwargs={'user_id': user_id, 'request_id': request_id})

	def create_users_and_requests(self):
		self.user1 = User(username="Andrew")
		self.user2 = User(username="Pavel")
		self.user3 = User(username="Elon")

		self.user1.save()
		self.user2.save()
		self.user3.save()

		FriendRequest(from_user=self.user1, to_user=self.user2).save()
		FriendRequest(from_user=self.user2, to_user=self.user1).save()
		FriendRequest(from_user=self.user2, to_user=self.user3).save()

	def test_delete_method(self):
		self.create_users_and_requests()

		friend_request = FriendRequest.objects.get(from_user=self.user2, to_user=self.user3)
		response = self.client.delete(self.get_url(self.user1.id, friend_request.id))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 2)

		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(response.data, None)

	def test_delete_method_no_request(self):
		self.create_users_and_requests()

		response = self.client.delete(self.get_url(self.user1.id, 256))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(list(response.json().keys()), ['detail'])

	def test_delete_method_no_user(self):
		self.create_users_and_requests()

		response = self.client.delete(self.get_url(256, 256))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(list(response.json().keys()), ['detail'])


class IncomingRequestListViewTest(APITestCase):

	def get_url(self, user_id):
		return reverse('socnet:incoming-request-list', kwargs={'user_id': user_id})

	def create_users_and_requests(self):
		self.user1 = User(username="Andrew")
		self.user2 = User(username="Pavel")
		self.user3 = User(username="Elon")

		self.user1.save()
		self.user2.save()
		self.user3.save()

		FriendRequest(from_user=self.user1, to_user=self.user2).save()
		FriendRequest(from_user=self.user2, to_user=self.user1).save()
		FriendRequest(from_user=self.user2, to_user=self.user3).save()

	def test_get_method(self):
		self.create_users_and_requests()

		response = self.client.get(self.get_url(self.user3.id))
		friend_request = FriendRequest.objects.get(from_user=self.user2, to_user=self.user3)

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.json(), [{
			'id': friend_request.id,
			'from_user': friend_request.from_user.id,
			'to_user': friend_request.to_user.id,
		}])

	def test_get_method_no_requests(self):
		self.create_users_and_requests()

		response = self.client.get(self.get_url(self.user1.id))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.json(), [])

	def test_get_method_no_user(self):
		self.create_users_and_requests()

		response = self.client.get(self.get_url(self.user3.id + 256))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(list(response.json().keys()), ['detail'])


class IncomingRequestDetailViewTest(APITestCase):

	def get_url(self, user_id, request_id):
		return reverse('socnet:incoming-request-detail', kwargs={'user_id': user_id, 'request_id': request_id})

	def create_users_and_requests(self):
		self.user1 = User(username="Andrew")
		self.user2 = User(username="Pavel")
		self.user3 = User(username="Elon")

		self.user1.save()
		self.user2.save()
		self.user3.save()

		FriendRequest(from_user=self.user1, to_user=self.user2).save()
		FriendRequest(from_user=self.user2, to_user=self.user1).save()
		FriendRequest(from_user=self.user2, to_user=self.user3).save()

	def test_put_method(self):
		self.create_users_and_requests()

		friend_request = FriendRequest.objects.get(from_user=self.user2, to_user=self.user3)
		response = self.client.put(self.get_url(self.user3.id, friend_request.id))
		accepted_friend_request = FriendRequest.objects.get(from_user=self.user3, to_user=self.user2)

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 4)

		self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
		self.assertEqual(response.json(), {
			'id': accepted_friend_request.id,
			'from_user': accepted_friend_request.from_user.id,
			'to_user': accepted_friend_request.to_user.id,
		})

	def test_put_method_no_request(self):
		self.create_users_and_requests()

		response = self.client.put(self.get_url(self.user3.id, 256))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(list(response.json().keys()), ['detail'])

	def test_put_method_no_user(self):
		self.create_users_and_requests()

		response = self.client.put(self.get_url(256, 256))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(list(response.json().keys()), ['detail'])

	def test_delete_method(self):
		self.create_users_and_requests()

		friend_request = FriendRequest.objects.get(from_user=self.user2, to_user=self.user3)
		response = self.client.delete(self.get_url(self.user3.id, friend_request.id))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 2)

		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(response.data, None)

	def test_delete_method_no_request(self):
		self.create_users_and_requests()

		response = self.client.delete(self.get_url(self.user3.id, 256))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(list(response.json().keys()), ['detail'])

	def test_delete_method_no_user(self):
		self.create_users_and_requests()

		response = self.client.delete(self.get_url(256, 256))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(list(response.json().keys()), ['detail'])


class FriendRelationViewTest(APITestCase):

	def get_url(self, user_id, oth_user_id):
		return reverse('socnet:friend-relation', kwargs={'user_id': user_id, 'oth_user_id': oth_user_id})

	def create_users_and_requests(self):
		self.user1 = User(username="Andrew")
		self.user2 = User(username="Pavel")
		self.user3 = User(username="Elon")

		self.user1.save()
		self.user2.save()
		self.user3.save()

		FriendRequest(from_user=self.user1, to_user=self.user2).save()
		FriendRequest(from_user=self.user2, to_user=self.user1).save()
		FriendRequest(from_user=self.user2, to_user=self.user3).save()

	def test_get_method_friends(self):
		self.create_users_and_requests()

		response = self.client.get(self.get_url(self.user1.id, self.user2.id))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.json(), {
			'status': 'friends'
		})

	def test_get_method_outgoing_request(self):
		self.create_users_and_requests()

		response = self.client.get(self.get_url(self.user2.id, self.user3.id))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.json(), {
			'status': 'outgoing request'
		})

	def test_get_method_incoming_request(self):
		self.create_users_and_requests()

		response = self.client.get(self.get_url(self.user3.id, self.user2.id))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.json(), {
			'status': 'incoming request'
		})

	def test_get_method_nothing(self):
		self.create_users_and_requests()

		response = self.client.get(self.get_url(self.user1.id, self.user3.id))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.json(), {
			'status': 'nothing'
		})

	def test_get_method_no_oth_user(self):
		self.create_users_and_requests()

		response = self.client.get(self.get_url(self.user1.id, 256))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(list(response.json().keys()), ['detail'])

	def test_get_method_no_user(self):
		self.create_users_and_requests()

		response = self.client.get(self.get_url(256, 256))

		self.assertEqual(User.objects.count(), 3)
		self.assertEqual(FriendRequest.objects.count(), 3)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(list(response.json().keys()), ['detail'])
