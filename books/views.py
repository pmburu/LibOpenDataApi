from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from rest_framework import exceptions as drf_exceptions, viewsets
from rest_framework_jwt.settings import api_settings
from rest_framework import permissions
from rest_framework import generics
from rest_framework.response import Response

from .models import *
from .serializers import *
# from .permissions import IsAuthed
# from rest_framework.permissions import IsAuthenticated

# Getting the JWT settings
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class AuthorViewSet(viewsets.ModelViewSet):
    """ This is an API endpoint that allows authors to be viewed. """
    queryset = Author.objects.all().order_by('birth_year')
    serializer_class = AuthorSerializer
    permission_classes = (permissions.IsAuthenticated,)

class BookViewSet(viewsets.ModelViewSet):
    """ This is an API endpoint that allows books to be viewed. """

    lookup_field = 'gutenberg_id'

    queryset = Book.objects.all()
    queryset = queryset.order_by('-download_count')
    queryset = queryset.exclude(download_count__isnull=True)

    serializer_class = BookSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset

        author_year_end = self.request.GET.get('author_year_end')
        if author_year_end is not None:
            queryset = queryset.filter(
                Q(authors__birth_year__lte=author_year_end) |
                Q(authors__death_year__lte=author_year_end)
            )

        author_year_start = self.request.GET.get('author_year_start')
        if author_year_start is not None:
            queryset = queryset.filter(
                Q(authors__birth_year__gte=author_year_start) |
                Q(authors__death_year__gte=author_year_start)
            )

        copyright_parameter = self.request.GET.get('copyright')
        if copyright_parameter is not None:
            copyright_strings = copyright_parameter.split(',')
            copyright_values = set()
            for copyright_string in copyright_strings:
                if copyright_string == 'true':
                    copyright_values.add(True)
                elif copyright_string == 'false':
                    copyright_values.add(False)
                elif copyright_string == 'null':
                    copyright_values.add(None)
            for value in [True, False, None]:
                if value not in copyright_values:
                    queryset = queryset.exclude(copyright=value)

        id_string = self.request.GET.get('ids')
        if id_string is not None:
            ids = id_string.split(',')

            try:
                ids = [int(id) for id in ids]
            except ValueError:
                pass
            else:
                queryset = queryset.filter(gutenberg_id__in=ids)

        language_string = self.request.GET.get('languages')
        if language_string is not None:
            language_codes = [code.lower() for code in language_string.split(',')]
            queryset = queryset.filter(languages__code__in=language_codes)

        mime_type = self.request.GET.get('mime_type')
        if mime_type is not None:
            queryset = queryset.filter(format__mime_type__startswith=mime_type)

        search_string = self.request.GET.get('search')
        if search_string is not None:
            search_terms = search_string.split(' ')
            for term in search_terms:
                queryset = queryset.filter(
                    Q(authors__name__icontains=term) | Q(title__icontains=term)
                )

        topic = self.request.GET.get('topic')
        if topic is not None:
            queryset = queryset.filter(
                Q(bookshelves__name__icontains=topic) | Q(subjects__name__icontains=topic)
            )

        return queryset.distinct()


class BookshelfViewSet(viewsets.ModelViewSet):
    """ This is an API endpoint that allows book shelves to be viewed. """
    queryset = Bookshelf.objects.all().order_by('name')
    serializer_class = BookshelfSerializer
    permission_classes = (permissions.IsAuthenticated,)
    

class FormatViewSet(viewsets.ModelViewSet):
    """ This is an API endpoint that allows book formats to be viewed. """
    queryset = Format.objects.all().order_by('book__download_count')
    serializer_class = FormatSerializer
    permission_classes = (permissions.IsAuthenticated,)
    

class LanguageViewSet(viewsets.ModelViewSet):
    """ This is an API endpoint that allows languages to be viewed. """
    queryset = Language.objects.all().order_by('code')
    serializer_class = LanguageSerializer
    permission_classes = (permissions.IsAuthenticated,)
    

class SubjectViewSet(viewsets.ModelViewSet):
    """ This is an API endpoint that allows book subjects to be viewed. """
    queryset = Subject.objects.all().order_by('name')
    serializer_class = SubjectSerializer
    permission_classes = (permissions.IsAuthenticated,)


class LoginView(generics.CreateAPIView):
    """
    POST auth/login/
    """
    # This permission class will overide the global permission
    # class setting
    permission_classes = (permissions.AllowAny,)

    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # login saves the user’s ID in the session,
            # using Django’s session framework.
            login(request, user)
            serializer = TokenSerializer(data={
                # using drf jwt utility functions to generate a token
                "token": jwt_encode_handler(
                    jwt_payload_handler(user)
                )})
            serializer.is_valid()
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class RegisterUsersView(generics.CreateAPIView):
    """
    POST auth/register/
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get("username", "")
        first_name = request.data.get('firstname', '')
        last_name = request.data.get('lastname', '')
        password = request.data.get("password", "")
        email = request.data.get("email", "")
        if not username and not password and not email:
            return Response(
                data={
                    "message": "username, password and email is required to register a user"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        new_user = User.objects.create_user(
            username=username, first_name=first_name, last_name=last_name, password=password, email=email
        )
        return Response()
