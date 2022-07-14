from django.contrib.auth.models import User, Group
from rest_framework import serializers, viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from api.permissions import ActionViewPermission


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'url', 'username', 'email',
                  'groups', 'first_name', "last_name"]

class ChangeUserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['groups']

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password_repeat = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password_repeat',
                  'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_repeat']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @action(detail=False, methods=['get'])
    def me(self, request):
        return Response({
            'user': UserSerializer(
                request.user,
                context={'request': request}).data
        }, status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        self.serializer_class = ChangeUserRoleSerializer
        return super().partial_update(request, pk)


class GroupViewSet(mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (ActionViewPermission,)
    list_rules = [
        [["Officer"], ["list"]],
    ]


class RegisterViewSet(mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer
