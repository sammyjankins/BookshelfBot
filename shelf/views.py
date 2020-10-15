from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Model, Q
from django.http import HttpResponseRedirect, QueryDict
from rest_framework import generics
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.serializers import Serializer, BaseSerializer
from rest_framework.views import APIView

from shelf import serializers
from shelf.models import BookCase, Shelf, Author, Book, Novel


def book_status(book):
    if len(book.novels.all()) == len(book.novels.filter(read=True)):
        book.read = True
        book.save()
    else:
        book.read = False
        book.save()


# My views ===================================


class MyCreateView(generics.CreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    create_serializer_class = Serializer
    fill_serializer_class = BaseSerializer
    prefix = ''
    fields = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_name = f'{self.prefix}_create.html'

    def get(self, request):
        queries = {key: obj_class.objects.filter(owner=request.user) for key, obj_class in self.fields.items()}
        resp_dict = {'serializer': self.fill_serializer_class}
        resp_dict.update(queries)
        return Response(resp_dict)

    def post(self, request, *args, **kwargs):
        serializer = self.create_serializer_class(data=request.data, context={'request': request})
        if not serializer.is_valid():
            queries = {key: obj_class.objects.filter(owner=request.user) for key, obj_class in self.fields.items()}
            resp_dict = {'serializer': self.fill_serializer_class,
                         'errors': serializer.errors}
            resp_dict.update(queries)
            return Response(resp_dict)
        serializer.save(owner=request.user)
        if self.prefix == 'novel':
            book_status(serializer.validated_data['book'])
        return HttpResponseRedirect(reverse(f'shelves:{self.prefix}/', args=[serializer.data["id"]]))


class MyUpdateView(generics.RetrieveUpdateDestroyAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    in_class = Model
    prefix = ''
    format_kwarg = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_name = f'{self.prefix}_update.html'

    def get_queryset(self):
        return self.in_class.objects.filter(owner__username=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        method = self.request.POST.get('_method', '').lower()
        if method == 'put':
            return self.put(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        obj = get_object_or_404(self.in_class, pk=kwargs['pk'])
        serializer = self.serializer_class(obj)
        resp_dict = {'serializer': serializer, self.prefix: obj}
        return Response(resp_dict)

    def put(self, request, *args, **kwargs):
        put_dict = {k: v[0] if len(v) == 1 else v for k, v in QueryDict(request.body).lists()}
        request.data = put_dict
        super().put(request, *args, **kwargs)
        return HttpResponseRedirect(reverse(f'shelves:{self.prefix}/', args=[kwargs['pk']]))


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

    # def get(self, request, *args, **kwargs):
    #     resp = super(MyListView, self).get(request, *args, **kwargs)
    #     print(resp.data)
    #     return resp


class MyDetailView(generics.RetrieveAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    prefix = ''
    in_class = Model

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_name = f'{self.prefix}_detail.html'

    def get(self, request, *args, **kwargs):
        obj = get_object_or_404(self.in_class, pk=kwargs['pk'])
        return Response({f'{self.prefix}': obj})


class MyDeleteView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    prefix = ''
    in_class = Model
    template_name = 'delete_template.html'

    def get(self, request, *args, **kwargs):
        obj = get_object_or_404(self.in_class, pk=kwargs['pk'])
        return Response({'obj': obj, 'prefix': self.prefix})

    def post(self, *args, **kwargs):
        obj = self.in_class.objects.get(pk=kwargs['pk'])
        obj.delete()
        return HttpResponseRedirect(reverse(f'shelves:{self.prefix}/all/'))


# BookCase views ===================================


class BookCaseCreateView(MyCreateView):
    create_serializer_class = serializers.BookCaseCreateSerializer
    fill_serializer_class = serializers.BookCaseCreateSerializer
    prefix = 'bookcase'


class BookCaseUpdateView(MyUpdateView):
    serializer_class = serializers.BookCaseUpdateSerializer
    prefix = 'bookcase'
    in_class = BookCase


class BookCaseListView(MyListView):
    in_class = BookCase
    template_name = 'bookcase_all.html'
    serializer_class = serializers.BookCaseListSerializer


class BookCaseDetailView(MyDetailView):
    prefix = 'bookcase'
    in_class = BookCase


class BookCaseDeleteView(MyDeleteView):
    prefix = 'bookcase'
    in_class = BookCase


# Shelf views ===================================

class ShelfCreateView(MyCreateView):
    create_serializer_class = serializers.ShelfCreateSerializer
    fill_serializer_class = serializers.ShelfFillSerializer
    prefix = 'shelf'
    fields = {'bookcase': BookCase}


class ShelfUpdateView(MyUpdateView):
    serializer_class = serializers.ShelfUpdateSerializer
    prefix = 'shelf'
    in_class = Shelf


class ShelfListView(MyListView):
    template_name = 'shelf_all.html'
    in_class = Shelf
    serializer_class = serializers.ShelfListSerializer


class ShelfDetailView(MyDetailView):
    prefix = 'shelf'
    in_class = Shelf


class ShelfDeleteView(MyDeleteView):
    prefix = 'shelf'
    in_class = Shelf


# Author views ===================================

class AuthorCreateView(MyCreateView):
    create_serializer_class = serializers.AuthorCreateSerializer
    fill_serializer_class = serializers.AuthorCreateSerializer
    prefix = 'author'


class AuthorUpdateView(MyUpdateView):
    serializer_class = serializers.AuthorUpdateSerializer
    prefix = 'author'
    in_class = Author


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


class AuthorDetailView(MyDetailView):
    prefix = 'author'
    in_class = Author


class AuthorDeleteView(MyDeleteView):
    prefix = 'author'
    in_class = Author


# Book views ===================================


class BookCreateView(MyCreateView):
    create_serializer_class = serializers.BookCreateSerializer
    fill_serializer_class = serializers.BookFillSerializer
    prefix = 'book'
    fields = {'bookcase': BookCase, 'author': Author, 'shelf': Shelf}


class BookUpdateView(MyUpdateView):
    serializer_class = serializers.BookUpdateSerializer
    prefix = 'book'
    in_class = Book


class BookListView(MyListView):
    in_class = Book
    template_name = 'book_all.html'
    serializer_class = serializers.BookListSerializer


class BookDetailView(MyDetailView):
    prefix = 'book'
    in_class = Book


class BookDeleteView(MyDeleteView):
    prefix = 'book'
    in_class = Book


# Novel views ===================================


class NovelCreateView(MyCreateView):
    create_serializer_class = serializers.NovelCreateSerializer
    fill_serializer_class = serializers.NovelFillSerializer
    prefix = 'novel'
    fields = {'book': Book, 'author': Author}


class NovelUpdateView(MyUpdateView):
    serializer_class = serializers.NovelUpdateSerializer
    prefix = 'novel'
    in_class = Novel


class NovelListView(MyListView):
    in_class = Novel
    template_name = 'novel_all.html'
    serializer_class = serializers.NovelListSerializer


class NovelDetailView(MyDetailView):
    prefix = 'novel'
    in_class = Novel


class NovelDeleteView(MyDeleteView):
    prefix = 'novel'
    in_class = Novel


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
