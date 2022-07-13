from django.db import models
from django.conf import settings

# Create your models here.
class Course(models.Model):
  name = models.CharField(max_length=30)
  description = models.CharField(max_length=255)
  members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="course_member")
  author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="course_author")
  enrollment_key = models.CharField(max_length=30, null=True, blank=True)

class EnrollmentRequest(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  course = models.ForeignKey(Course, on_delete=models.CASCADE)

class Content(models.Model):
  body = models.CharField(max_length=255)
  course = models.ForeignKey(Course, on_delete=models.CASCADE)