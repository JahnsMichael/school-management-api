from django.contrib.auth.models import User, Group
from django.db.models import Q
from rest_framework import serializers, viewsets, permissions, mixins, status
from rest_framework.fields import CurrentUserDefault
from rest_framework.decorators import action
from rest_framework.response import Response
from api.permissions import ActionViewPermission
from api.models import Course, Content, EnrollmentRequest
from api.views.users import UserSerializer


class CourseSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    members = UserSerializer(read_only=True, many=True)
    owned = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'url', 'name', 'description',
                  'enrollment_key', 'author', 'members', 'owned']

    def create(self, validated_data):
        return Course.objects.create(
            author=self.context['request'].user,
            **validated_data
        )

    def get_owned(self, obj):
        return self.context['request'].user in obj.members.all()


class EnrollmentRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = EnrollmentRequest
        fields = ['id', 'user', 'course']

    def create(self, validated_data):
        course_id = int(self.context['request'].query_params.get("course-id"))
        course = Course.objects.get(pk=course_id)
        return EnrollmentRequest.objects.create(
            user=self.context['request'].user,
            course=course,
        )


class EnrollmentKeySerializer(serializers.Serializer):
    enrollment_key = serializers.CharField(max_length=255)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (ActionViewPermission,)
    list_rules = [
        [["Officer", "Teacher"], ["list", "retrieve", "destroy",
                                  "create", "update", "partial_update", "owned"]],
        [["Student"], ["list", "retrieve", "owned"]]
    ]

    @action(detail=False, methods=['get'])
    def owned(self, request):
        self.queryset = self.queryset.filter(
            Q(members__in=[request.user]) |
            Q(author=request.user),
        )
        return super().list(request)


class EnrollmentRequestViewSet(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    queryset = EnrollmentRequest.objects.all()
    serializer_class = EnrollmentRequestSerializer
    permission_classes = (ActionViewPermission,)
    list_rules = [
        [["Officer", "Teacher"], ["list", "retrieve", "destroy",
                                  "create", "update", "partial_update"]],
        [["Student"], ["list", "retrieve", "create", 'bykey']]
    ]

    def list(self, request):
        param = request.query_params.get("course-id")
        if param:
            self.queryset = self.queryset.filter(course__id=param)
        return super().list(request)

    def destroy(self, request, pk=None):
        instance = self.get_object()
        instance.course.members.add(instance.user)
        instance.save()
        return super().destroy(request, pk)

    @action(detail=False, methods=['post'])
    def bykey(self, request):
        serializer = EnrollmentKeySerializer(data=request.data)
        param = request.query_params.get("course-id")
        course = Course.objects.filter(pk=param).first()
        if not course:
            return Response('courses not found',
                            status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            if course.enrollment_key == serializer.validated_data['enrollment_key']:
                course.members.add(request.user)
                course.save()
                return Response(CourseSerializer(course, context={'request': request}).data,
                                status=status.HTTP_200_OK)
            return Response('key doesn\'t match',
                            status=status.HTTP_400_BAD_REQUEST)
