from django.urls import path, include
from rest_framework import routers
from api.views.hello import HelloView
from api.views import users, courses

router = routers.DefaultRouter()
router.register(r'users', users.UserViewSet)
router.register(r'groups', users.GroupViewSet)
router.register(r'register', users.RegisterViewSet)
router.register(r'courses', courses.CourseViewSet)
router.register(r'enroll-request', courses.EnrollmentRequestViewSet)

urlpatterns = [
	path('', include(router.urls)),
	path('hello/', HelloView.as_view(), name ='hello'),
]
