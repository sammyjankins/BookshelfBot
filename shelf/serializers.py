from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from shelf.models import Shelf, BookCase, Author, Book, Novel, Profile


# title serializers
from shelf.utils import create_shelves


class NovelTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Novel
        fields = ['title', ]


class BookTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['title', ]


class AuthorTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', ]


class ShelfTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelf
        fields = ['title', 'row', ]


class BookCaseTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCase
        fields = ['title', ]


# novel serializers +++++++++++++++++++++++++++++++++++++++++++++


class NovelCreateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Novel
        fields = '__all__'


class NovelUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Novel
        exclude = ['owner', ]


class NovelListSerializer(serializers.ModelSerializer):
    author = AuthorTitleSerializer(read_only=True)

    class Meta:
        model = Novel
        fields = '__all__'


# book serializers ++++++++++++++++++++++++++++++++++++++


class BookCreateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Book
        fields = '__all__'


class BookUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        exclude = ['owner', ]


class BookListSerializer(serializers.ModelSerializer):
    author = AuthorTitleSerializer()
    shelf = ShelfTitleSerializer()
    bookcase = BookCaseTitleSerializer()

    class Meta:
        model = Book
        fields = '__all__'


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


class AuthorListSerializer(serializers.ModelSerializer):
    books = BookTitleSerializer(many=True, read_only=True)

    class Meta:
        model = Author
        fields = ['id', 'name', 'date_of_birth', 'books', ]


# bookcase serializers ++++++++++++++++++++++++++++++++++++++


class BookCaseCreateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = BookCase
        fields = '__all__'

    def create(self, validated_data):
        bookcase = BookCase.objects.create(**validated_data)
        create_shelves(bookcase=bookcase)
        return bookcase


class BookCaseUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCase
        exclude = ['owner', ]


class BookCaseListSerializer(serializers.ModelSerializer):
    books = BookTitleSerializer(many=True, read_only=True)

    class Meta:
        model = BookCase
        fields = ['id', 'title', 'books', ]


# shelf serializers ++++++++++++++++++++++++++++++++++++++

class ShelfCreateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Shelf
        fields = '__all__'


class ShelfUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelf
        exclude = ['owner', ]


class ShelfListSerializer(serializers.ModelSerializer):
    bookcase = BookCaseTitleSerializer(read_only=True)
    books = BookTitleSerializer(many=True, read_only=True)

    class Meta:
        model = Shelf
        fields = '__all__'


# profile serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', ]


class ProfileSerializer(serializers.ModelSerializer):
    tele_id = serializers.CharField(
        max_length=15,
        required=True,
        validators=[UniqueValidator(queryset=Profile.objects.all())]
    )

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
