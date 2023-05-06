from django.db import models


class User(models.Model):
	"""Represents user model"""

	username = models.CharField(verbose_name="username", max_length=512)

	def __str__(self):
		return f"<{self.id}:{self.username}>"

	def __repr__(self):
		return self.__str__()

	def get_friends(self):
		"""Returns list with friends of user (self)"""
		friends = []
		for req in FriendRequest.objects.filter(from_user=self):
			if FriendRequest.objects.filter(from_user=req.to_user, to_user=req.from_user):
				friends.append(req.to_user)

		return friends


class FriendRequest(models.Model):
	"""Represents relationship between users: outgoing friend requests"""

	from_user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		verbose_name="from_user",
		related_name="from_user")
	to_user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		verbose_name="to_user",
		related_name="to_user")

	def __str__(self):
		return f"<{self.from_user.__str__()}->{self.to_user.__str__()}>"

	def __repr__(self):
		return self.__str__()
