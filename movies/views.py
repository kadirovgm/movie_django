from django.db import models
from rest_framework import generics, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend
import logging
import json, datetime

from .models import Movie, Actor, Review
from .serializers import (
    MovieListSerializer,
    MovieDetailSerializer,
    ReviewCreateSerializer,
    CreateRatingSerializer,
    ActorListSerializer,
    ActorDetailSerializer,
)
from .service import get_client_ip, MovieFilter, PaginationMovies
from .permissions import IsOwnerOrReadOnly


from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """Вывод списка фильмов"""
    filter_backends = (DjangoFilterBackend,)
    filterset_class = MovieFilter
    pagination_class = PaginationMovies
    # permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly] # ограничения

    def get_queryset(self):
        movies = Movie.objects.filter(draft=False).annotate(
            rating_user=models.Count("ratings",
                                     filter=models.Q(ratings__ip=get_client_ip(self.request)))
        ).annotate(
            middle_star=models.Sum(models.F('ratings__star')) / models.Count(models.F('ratings'))
        )
        return movies

    def get_serializer_class(self):
        if self.action == 'list':
            return MovieListSerializer
        elif self.action == "retrieve":
            return MovieDetailSerializer


class ReviewCreateViewSet(viewsets.ModelViewSet):
    """Добавление отзыва к фильму"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReviewCreateSerializer


class AddStarRatingViewSet(viewsets.ModelViewSet):
    """Добавление рейтинга фильму"""
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateRatingSerializer

    def perform_create(self, serializer):
        serializer.save(ip=get_client_ip(self.request))


class ActorsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вывод актеров или режиссеров"""
    permission_classes = [permissions.IsAuthenticated]
    queryset = Actor.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ActorListSerializer
        elif self.action == "retrieve":
            return ActorDetailSerializer


###logging
@csrf_exempt
def save_client_log(request):
  """
  Сохраняет собранные данные с клиента в лог
  """
  logs = request.POST.get('logs', '[]')
  with open('request.log', 'a') as f:
     for log_str in json.loads(logs):
         f.write(json.dumps(log_str) + '\n')

  return HttpResponse()

def get_page_with_button(request):
   """
   Возвращает страницу с кнопкой
   """
   template = loader.get_template('movies/index.html')

   return HttpResponse(template.render({}, request))


def get_current_datetime(request):
   """
   Возвращает текущую дату и время
   """
   return HttpResponse(datetime.datetime.now())

# class MovieListView(generics.ListAPIView):
#     """Вывод списка фильмов"""
#     serializer_class = MovieListSerializer
#     filter_backends = (DjangoFilterBackend,)
#     filterset_class = MovieFilter
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_queryset(self):
#         movies = Movie.objects.filter(draft=False).annotate(
#             rating_user=models.Count("ratings",
#                                      filter=models.Q(ratings__ip=get_client_ip(self.request)))
#         ).annotate(
#             middle_star=models.Sum(models.F('ratings__star')) / models.Count(models.F('ratings'))
#         )
#         return movies

#
# class MovieDetailView(generics.RetrieveAPIView):
#     """Вывод фильма"""
#     queryset = Movie.objects.filter(draft=False)
#     serializer_class = MovieDetailSerializer


# class ReviewCreateView(generics.CreateAPIView):
#     """Добавление отзыва к фильму"""
#     serializer_class = ReviewCreateSerializer


# class AddStarRatingView(generics.CreateAPIView):
#     """Добавление рейтинга фильму"""
#     serializer_class = CreateRatingSerializer
#
#     def perform_create(self, serializer):
#         serializer.save(ip=get_client_ip(self.request))


# class ActorsListView(generics.ListAPIView):
#     """Вывод списка актеров"""
#     queryset = Actor.objects.all()
#     serializer_class = ActorListSerializer
#
#
# class ActorsDetailView(generics.RetrieveAPIView):
#     """Вывод актера или режиссера"""
#     queryset = Actor.objects.all()
#     serializer_class = ActorDetailSerializer