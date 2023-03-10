from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, permissions

from goals.filters import GoalsFilter
from goals.models import Category, Goal, Comment, Board
from goals.permissions import BoardPermissions, IsOwnerOrWriter, IsCommentOwner
from goals.serializers import (
    CategoryCreateSerializer, CategoryListSerializer, GoalCreateSerializer, GoalListSerializer,
    CommentCreateSerializer, CommentListSerializer, BoardCreateSerializer, BoardUpdateSerializer, BoardListSerializer
)


class BoardViewSet(viewsets.ModelViewSet):
    """Представление для обработки запроса на эндпоинт /goals/board{/<id>}

    Действия над доской
    """
    queryset = Board.objects.all().filter(is_deleted=False)
    permission_classes = [BoardPermissions]

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['title', 'created']
    ordering = ['title']

    _serializers = {
        'create': BoardCreateSerializer,
        'list': BoardListSerializer,
    }
    _default_serializer = BoardUpdateSerializer

    #: Получение сериализатора
    def get_serializer_class(self):
        return self._serializers.get(self.action, self._default_serializer)

    #: Переопределяем метод для отображения досок с учетом полей user и is_deleted.
    def get_queryset(self):
        return super().get_queryset().prefetch_related('participants__user').filter(
            participants__user_id=self.request.user.id,
        )

    #: Переопределяем метод для добавления в serializer поля user (create).
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    #: Переопределяем метод для добавления в serializer поля user (retrieve, update).
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    #: Переопределяем метод для исключения удаления доски из базы.
    def perform_destroy(self, instance: Board) -> Board:
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=('is_deleted',))
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board_id=instance.id).update(status=Goal.Status.archived)
        return instance


class CategoryViewSet(viewsets.ModelViewSet):
    """Представление для обработки запроса на эндпоинт /goals/goal_category{/<id>}

    Действия над категориями.
    """
    queryset = Category.objects.all().filter(is_deleted=False)

    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['board']
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title']

    _serializers = {'create': CategoryCreateSerializer}
    _default_serializer = CategoryListSerializer

    _permissions = {'create': [permissions.IsAuthenticated()]}
    _default_permissions = [IsOwnerOrWriter()]

    def get_serializer_class(self):
        return self._serializers.get(self.action, self._default_serializer)

    def get_permissions(self):
        return self._permissions.get(self.action, self._default_permissions)

    #: Переопределяем метод для отображения категорий с учетом полей user и is_deleted.
    def get_queryset(self):
        return super().get_queryset().select_related('user', 'board').filter(
            board__participants__user_id=self.request.user.id
        )

    #: Переопределяем метод для добавления в serializer поля user.
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    #: Переопределяем метод для исключения удаления категории из базы.
    def perform_destroy(self, instance: Category) -> Category:
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=('is_deleted',))
            instance.goals.update(status=Goal.Status.archived)
        return instance


class GoalViewSet(viewsets.ModelViewSet):
    """Представление для обработки запроса на эндпоинт /goals/goal{/<id>}

    Действия над целями.
    """
    queryset = Goal.objects.all().select_related('user', 'category')

    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    filterset_class = GoalsFilter
    ordering_fields = ['priority', 'due_date']
    ordering = ['priority']
    search_fields = ['title', 'description']

    _serializers = {'create': GoalCreateSerializer}
    _default_serializer = GoalListSerializer

    _permissions = {'create': [permissions.IsAuthenticated()]}
    _default_permissions = [IsOwnerOrWriter()]

    def get_serializer_class(self):
        return self._serializers.get(self.action, self._default_serializer)

    def get_permissions(self):
        return self._permissions.get(self.action, self._default_permissions)

    #: Переопределяем метод для отображения целей с учетом полей user и status.
    def get_queryset(self):
        return super().get_queryset().filter(
            category__board__participants__user_id=self.request.user.id,
            category__is_deleted=False,
            status__lt=Goal.Status.archived,
        )

    #: Переопределяем метод для добавления в serializer поля user.
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    #: Переопределяем метод для исключения удаления целей из базы.
    def perform_destroy(self, instance: Goal) -> Goal:
        with transaction.atomic():
            instance.status = Goal.Status.archived
            instance.save(update_fields=('status',))
        return instance


class CommentViewSet(viewsets.ModelViewSet):
    """Представление для обработки запроса на эндпоинт /goals/goal_comment{/<id>}

    Действия над комментариями.
    """
    queryset = Comment.objects.all().select_related('goal')

    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['goal']
    ordering_fields = ['created']
    ordering = ['-created']

    _serializers = {'create': CommentCreateSerializer}
    _default_serializer = CommentListSerializer

    _permissions = {'create': [permissions.IsAuthenticated()]}
    _default_permissions = [IsCommentOwner()]

    def get_serializer_class(self):
        return self._serializers.get(self.action, self._default_serializer)

    def get_permissions(self):
        return self._permissions.get(self.action, self._default_permissions)

    #: Переопределяем метод для отображения комментариев с учетом полей user и status.
    def get_queryset(self):
        return super().get_queryset().filter(
            goal__category__board__participants__user_id=self.request.user.id,
            goal__status__lt=Goal.Status.archived,
        )

    #: Переопределяем метод для добавления в serializer поля user.
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
