from django.urls import path

from languageschool.views.api import SearchView, MeaningView, WordView, ArticleGameView, VocabularyGameView, \
    ConjugationGameView, ActivationView, ProfilePictureView, ResetAccountView
from languageschool.views.viewsets import GameViewSet, ArticleViewSet, CategoryViewSet, ConjugationViewSet, \
    LanguageViewSet, MeaningViewSet, ScoreListViewSet, ScoreViewSet, WordViewSet, UserViewSet, PublicImageViewSet, \
    RequestResetPasswordView, RankingsViewSet
from rest_framework.authtoken import views as rest_framework_views

urlpatterns = [
    path('api/games', GameViewSet.as_view(), name='games-api'),
    path('api/languages/', LanguageViewSet.as_view(), name='languages-api'),
    path('api/categories/', CategoryViewSet.as_view(), name='categories-api'),
    path('api/articles/', ArticleViewSet.as_view(), name='articles-api'),
    path('api/words/', WordViewSet.as_view(), name='words-api'),
    path('api/meanings/', MeaningViewSet.as_view(), name='meanings-api'),
    path('api/conjugations/', ConjugationViewSet.as_view(), name='conjugations-api'),
    path('api/user/', UserViewSet.as_view(), name='user-api'),
    path('api/score/', ScoreViewSet.as_view(), name='score-api'),
    path('api/score/<int:score_id>', ScoreViewSet.as_view(), name='update-score-api'),
    path('api/scores/', ScoreListViewSet.as_view(), name='scores-api'),
    path('api/rankings/', RankingsViewSet.as_view(), name='rankings-api'),
    path('api/public-images/', PublicImageViewSet.as_view(), name='public-images-api'),
    path('api/search', SearchView.as_view(), name='search-api'),
    path('api/meanings/<int:pk>', MeaningView.as_view(), name='meaning-api'),
    path('api/words/<int:pk>', WordView.as_view(), name='word-api'),
    path('api/article-game', ArticleGameView.as_view(), name='article-game-api'),
    path('api/vocabulary-game', VocabularyGameView.as_view(), name='vocabulary-game-api'),
    path('api/conjugation-game', ConjugationGameView.as_view(), name='conjugation-game-api'),
    path('api/activate/<uidb64>/<token>', ActivationView.as_view(), name='activate-api'),
    path('api/user-token', rest_framework_views.obtain_auth_token),
    path('api/user/picture', ProfilePictureView.as_view(), name='profile-picture-api'),
    path('api/reset-account/<uidb64>/<token>', ResetAccountView.as_view(), name='reset-account-api'),
    path('api/request-reset-account/', RequestResetPasswordView.as_view(), name='request-reset-account-api')
]
