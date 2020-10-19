from pprint import pprint

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Model, Q
from django.http import HttpResponseRedirect, QueryDict
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.serializers import Serializer

from shelf import serializers
from shelf.models import BookCase, Shelf, Author, Book, Novel


def book_status(book_id):
    book = Book.objects.get(pk=book_id)
    if len(book.novels.all()) == len(book.novels.filter(read=True)):
        book.read = True
        book.save()
    else:
        book.read = False
        book.save()


# My views ===================================


class MyCreateView(generics.CreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    serializer_class = Serializer
    name = ''
    fields = {}

    def get(self, request, errors=None):
        resp_dict = {'serializer': self.serializer_class}
        queries = {key: self.fields[key].objects.filter(owner__username=request.user) for key in self.fields}
        if errors:
            resp_dict['errors'] = []
            for error in errors:
                resp_dict['errors'].append([error, errors[error][0]['message']])
        resp_dict.update(queries)
        return Response(resp_dict)

    def post(self, request, *args, **kwargs):
        try:
            resp = super().create(request, *args, **kwargs)
            if self.name == 'novel':
                book_status(resp.data['book'])
            return HttpResponseRedirect(reverse(f'shelves:{self.name}/', args=[resp.data['id']]))
        except ValidationError as e:
            errors = e.get_full_details()
            return self.get(request, errors=errors)


class MyUpdateDetailDeleteView(generics.RetrieveUpdateDestroyAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    in_class = Model
    name = ''
    template_name = ''
    fields = {}
    format_kwarg = None

    def get_queryset(self):
        return self.in_class.objects.filter(owner__username=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        method = self.request.POST.get('_method', '').lower()
        if method == 'put':
            return self.put(request, *args, **kwargs)
        if method == 'delete':
            return self.destroy(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        obj = get_object_or_404(self.in_class, pk=kwargs['pk'])
        serializer = self.serializer_class(obj)
        resp_dict = {'serializer': serializer}
        queries = {key: self.fields[key].objects.filter(owner__username=request.user) for key in self.fields}
        resp_dict.update({self.name: obj} if 'delete' not in self.template_name else {'obj': obj, 'name': self.name})
        resp_dict.update(queries)
        return Response(resp_dict)

    def put(self, request, *args, **kwargs):
        put_dict = {k: v[0] if len(v) == 1 else v for k, v in QueryDict(request.body).lists()}
        put_dict['read'] = str('read' in put_dict).lower()
        request.data = put_dict
        resp = super().put(request, *args, **kwargs)
        if self.name == 'novel':
            book_status(resp.data['book'])
        return HttpResponseRedirect(reverse(f'shelves:{self.name}/', args=[kwargs['pk']]))

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return HttpResponseRedirect(reverse(f'shelves:{self.name}/all/'))


class MyListView(ListAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    in_class = Model

    def get_queryset(self, *args, **kwargs):
        question = self.request.GET.get('q')
        objects = self.in_class.objects.filter(owner__username=self.request.user)
        if question is not None:
            objects = objects.filter(
                (Q(title__icontains=question) |
                 Q(title__in=question.split()) |
                 Q(title__icontains=question.title()) |
                 Q(title__in=question.title().split())))
        return objects.order_by('-id')


# BookCase views ===================================


class BookCaseCreateView(MyCreateView):
    serializer_class = serializers.BookCaseCreateSerializer
    name = 'bookcase'
    template_name = 'bookcase_create.html'


class BookCaseUpdateView(MyUpdateDetailDeleteView):
    serializer_class = serializers.BookCaseUpdateSerializer
    name = 'bookcase'
    in_class = BookCase
    template_name = 'bookcase_update.html'


class BookCaseListView(MyListView):
    in_class = BookCase
    template_name = 'bookcase_all.html'
    serializer_class = serializers.BookCaseListSerializer


class BookCaseDetailView(MyUpdateDetailDeleteView):
    serializer_class = serializers.BookCaseUpdateSerializer
    name = 'bookcase'
    in_class = BookCase
    template_name = 'bookcase_detail.html'


class BookCaseDeleteView(MyUpdateDetailDeleteView):
    serializer_class = serializers.BookCaseUpdateSerializer
    name = 'bookcase'
    in_class = BookCase
    template_name = 'delete_template.html'


# Shelf views ===================================


class ShelfCreateView(MyCreateView):
    serializer_class = serializers.ShelfCreateSerializer
    name = 'shelf'
    template_name = 'shelf_create.html'
    fields = {'bookcase': BookCase, }


class ShelfUpdateView(MyUpdateDetailDeleteView):
    serializer_class = serializers.ShelfUpdateSerializer
    name = 'shelf'
    in_class = Shelf
    template_name = 'shelf_update.html'
    fields = {'bookcase': BookCase, }


class ShelfListView(MyListView):
    template_name = 'shelf_all.html'
    in_class = Shelf
    serializer_class = serializers.ShelfListSerializer


class ShelfDetailView(MyUpdateDetailDeleteView):
    serializer_class = serializers.ShelfUpdateSerializer
    name = 'shelf'
    in_class = Shelf
    template_name = 'shelf_detail.html'


class ShelfDeleteView(MyUpdateDetailDeleteView):
    serializer_class = serializers.ShelfUpdateSerializer
    name = 'shelf'
    in_class = Shelf
    template_name = 'delete_template.html'


# Author views ===================================


class AuthorCreateView(MyCreateView):
    serializer_class = serializers.AuthorCreateSerializer
    name = 'author'
    template_name = 'author_create.html'


class AuthorUpdateView(MyUpdateDetailDeleteView):
    serializer_class = serializers.AuthorUpdateSerializer
    name = 'author'
    in_class = Author
    template_name = 'author_update.html'


class AuthorListView(ListAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'author_all.html'
    serializer_class = serializers.AuthorListSerializer

    def get_queryset(self, *args, **kwargs):
        question = self.request.GET.get('q')
        objects = Author.objects.filter(owner__username=self.request.user)
        if question is not None:
            objects = objects.filter(
                (Q(name__icontains=question) |
                 Q(name__in=question.split())))
        return objects.order_by('-id')


class AuthorDetailView(MyUpdateDetailDeleteView):
    serializer_class = serializers.AuthorUpdateSerializer
    name = 'author'
    in_class = Author
    template_name = 'author_detail.html'


class AuthorDeleteView(MyUpdateDetailDeleteView):
    serializer_class = serializers.AuthorUpdateSerializer
    name = 'author'
    in_class = Author
    template_name = 'delete_template.html'


# Book views ===================================


class BookCreateView(MyCreateView):
    serializer_class = serializers.BookCreateSerializer
    name = 'book'
    template_name = 'book_create.html'
    fields = {'bookcase': BookCase, 'shelf': Shelf, 'author': Author, }


class BookUpdateView(MyUpdateDetailDeleteView):
    serializer_class = serializers.BookUpdateSerializer
    name = 'book'
    in_class = Book
    template_name = 'book_update.html'
    fields = {'bookcase': BookCase, 'shelf': Shelf, 'author': Author, }


class BookDetailView(MyUpdateDetailDeleteView):
    serializer_class = serializers.BookUpdateSerializer
    name = 'book'
    in_class = Book
    template_name = 'book_detail.html'


class BookListView(MyListView):
    in_class = Book
    template_name = 'book_all.html'
    serializer_class = serializers.BookListSerializer


class BookDeleteView(MyUpdateDetailDeleteView):
    serializer_class = serializers.BookUpdateSerializer
    name = 'book'
    in_class = Book
    template_name = 'delete_template.html'


# Novel views ===================================


class NovelCreateView(MyCreateView):
    serializer_class = serializers.NovelCreateSerializer
    name = 'novel'
    template_name = 'novel_create.html'
    fields = {'author': Author, 'book': Book, }


class NovelUpdateView(MyUpdateDetailDeleteView):
    serializer_class = serializers.NovelUpdateSerializer
    name = 'novel'
    in_class = Novel
    template_name = 'novel_update.html'
    fields = {'author': Author, 'book': Book, }


class NovelListView(MyListView):
    in_class = Novel
    template_name = 'novel_all.html'
    serializer_class = serializers.NovelListSerializer


class NovelDetailView(MyUpdateDetailDeleteView):
    serializer_class = serializers.NovelUpdateSerializer
    name = 'novel'
    in_class = Novel
    template_name = 'novel_detail.html'


class NovelDeleteView(MyUpdateDetailDeleteView):
    serializer_class = serializers.NovelUpdateSerializer
    name = 'novel'
    in_class = Novel
    template_name = 'delete_template.html'


# user auth stuff


class UserRegisterView(generics.CreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    queryset = User.objects.all()
    serializer_class = serializers.UserRegisterSerializer
    template_name = 'register.html'

    def get(self, pk):
        return Response({'serializer': self.serializer_class})

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({'serializer': self.serializer_class,
                             'message': 'Invalid data, please read following error messages',
                             'errors': serializer.errors})
        serializer.save()
        messages.success(request, f'Account created for {serializer.data["username"]}')
        return HttpResponseRedirect(reverse('login'))


class UserDetailView(generics.RetrieveAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'profile.html'

    def get(self, request, *args, **kwargs):
        return Response()
