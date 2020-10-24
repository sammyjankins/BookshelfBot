from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from shelf.models import Shelf, BookCase, Author, Book, Novel, Profile

shelf_titles = {
    1: 'первая полка',
    2: 'вторая полка',
    3: 'третья полка',
    4: 'четвертая полка',
    5: 'пятая полка',
    6: 'шестая полка',
    7: 'седьмая полка',
    8: 'восьмая полка',
    9: 'девятая полка',
    10: 'десятая полка',
}
row_titles = {
    1: 'Первый',
    2: 'Второй',
    3: 'Третий',
    4: 'Четвертый',
}

sections_titles = {
    1: 'левая',
    2: 'правая',
}


# title serializers

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


# bookcase serializers ++++++++++++++++++++++++++++++++++++++


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
        print(bookcase, bookcase.shelf_count, bookcase.row_count, bookcase.section_count)
        for shelf_number in range(bookcase.shelf_count):
            for row_number in range(bookcase.row_count):
                for sections_number in range(bookcase.section_count):
                    Shelf.objects.create(
                        title=f'{shelf_titles[shelf_number + 1]} {"слева" if sections_number + 1 == 1 else "справа"}',
                        row=row_titles[row_number + 1],
                        bookcase=bookcase,
                        owner=bookcase.owner)
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


# profil*e serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', ]


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
