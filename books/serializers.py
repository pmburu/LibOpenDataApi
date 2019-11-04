from rest_framework import serializers

from .models import *


class AuthorSerializer(serializers.ModelSerializer):
    # authed = serializers.HiddenField(
    #     default=serializers.CurrentUserDefault()
    # )
    class Meta:
        model = Author
        fields = ('name', 'birth_year', 'death_year')


class BookshelfSerializer(serializers.ModelSerializer):
    # authed = serializers.HiddenField(
    #     default=serializers.CurrentUserDefault()
    # )    
    class Meta:
        model = Bookshelf
        fields = ('name',)


class FormatSerializer(serializers.ModelSerializer):
    # authed = serializers.HiddenField(
    #     default=serializers.CurrentUserDefault()
    # )    
    class Meta:
        model = Format
        fields = ('book', 'mime_type', 'url')


class LanguageSerializer(serializers.ModelSerializer):
    # authed = serializers.HiddenField(
    #     default=serializers.CurrentUserDefault()
    # )    
    class Meta:
        model = Language
        fields = ('code',)


class SubjectSerializer(serializers.ModelSerializer):
    # authed = serializers.HiddenField(
    #     default=serializers.CurrentUserDefault()
    # )    
    class Meta:
        model = Subject
        fields = ('name',)


class BookSerializer(serializers.ModelSerializer):
    # authed = serializers.HiddenField(
    #     default=serializers.CurrentUserDefault()
    # )    
    id = serializers.SerializerMethodField()
    authors = AuthorSerializer(many=True)
    bookshelves = serializers.SerializerMethodField()
    formats = serializers.SerializerMethodField()
    languages = serializers.SerializerMethodField()
    subjects = serializers.SerializerMethodField()

    lookup_field = 'gutenberg_id'

    class Meta:
        model = Book
        fields = (
            'id',
            'title',
            'authors',
            'subjects',
            'bookshelves',
            'languages',
            'copyright',
            'media_type',
            'formats',
            'download_count'
        )

    def get_bookshelves(self, book):
        bookshelves = [bookshelf.name for bookshelf in book.bookshelves.all()]
        bookshelves.sort()
        return bookshelves

    def get_formats(self, book):
        return {f.mime_type: f.url for f in book.get_formats()}

    def get_id(self, book):
        return book.gutenberg_id

    def get_languages(self, book):
        languages = [language.code for language in book.languages.all()]
        languages.sort()
        return languages

    def get_subjects(self, book):
        subjects = [subject.name for subject in book.subjects.all()]
        subjects.sort()
        return subjects


class TokenSerializer(serializers.Serializer):
    """
    This serializer serializes the token data
    """
    token = serializers.CharField(max_length=255)
