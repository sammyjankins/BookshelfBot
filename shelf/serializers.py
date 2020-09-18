from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from shelf.models import Shelf, BookCase, Author, Book, Novel, Profile


# novel serializers +++++++++++++++++++++++++++++++++++++++++++++

class NovelFillSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Novel
        exclude = ('book', 'author',)


class NovelCreateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Novel
        fields = '__all__'


class NovelUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Novel
        exclude = ['owner', ]


# bookcase serializers ++++++++++++++++++++++++++++++++++++++

class BookFillSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Book
        exclude = ('bookcase', 'author', 'shelf')


class BookCreateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Book
        fields = '__all__'


class BookUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        exclude = ['owner', ]


# author serializers ++++++++++++++++++++++++++++++++++++++


class AuthorCreateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Author
        fields = '__all__'


class AuthorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        exclude = ['owner', ]


# bookcase serializers ++++++++++++++++++++++++++++++++++++++


class BookCaseCreateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = BookCase
        fields = '__all__'


class BookCaseUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCase
        exclude = ['owner', ]


# shelf serializers ++++++++++++++++++++++++++++++++++++++

class ShelfFillSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Shelf
        exclude = ('bookcase',)


class ShelfCreateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Shelf
        fields = '__all__'


class ShelfUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelf
        exclude = ['owner', ]


# profile serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'tele_id']


class UserRegisterSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=True)

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        max_length=32,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(min_length=8,
                                     write_only=True,
                                     required=True,
                                     style={'input_type': 'password', 'placeholder': 'Password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'profile', ]

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'],
                                        validated_data['password'])

        profile_data = validated_data.pop('profile')
        Profile.objects.create(user=user, tele_id=profile_data['tele_id'])

        return user
