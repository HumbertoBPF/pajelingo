from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from languageschool.models import Article, Category, Conjugation, Language, Meaning, Score, Word, Game, AppUser
from languageschool.utils import send_reset_account_email, get_base_64_encoded_image
from pajelingo.validators.validators import validate_email, validate_username


class GameSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    image_uri = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = '__all__'

    def get_image(self, obj):
        return get_base_64_encoded_image(obj.image)

    def get_image_uri(self, obj):
        if obj.image:
            return obj.image.url


class LanguageSerializer(serializers.ModelSerializer):
    flag_image = serializers.SerializerMethodField()
    flag_image_uri = serializers.SerializerMethodField()

    class Meta:
        model = Language
        fields = '__all__'

    def get_flag_image(self, obj):
        return get_base_64_encoded_image(obj.flag_image)

    def get_flag_image_uri(self, obj):
        if obj.flag_image:
            return obj.flag_image.url


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    language = serializers.ReadOnlyField(source='language.language_name')

    class Meta:
        model = Article
        fields = '__all__'


class WordSerializer(serializers.ModelSerializer):
    language = serializers.ReadOnlyField(source='language.language_name')
    category = serializers.ReadOnlyField(source='category.category_name')
    image = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Word
        fields = '__all__'

    def get_is_favorite(self, obj):
        user = self.context["request"].user

        if user.is_anonymous:
            return None

        app_user = AppUser.objects.filter(user__id=user.id).first()

        if app_user is None:
            return None

        return obj in app_user.favorite_words.all()

    def get_image(self, obj):
        if obj.image:
            return obj.image.url


class MeaningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meaning
        fields = '__all__'


class ConjugationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conjugation
        fields = '__all__'


class RankingsSerializer(serializers.Serializer):
    position = serializers.IntegerField()
    user = serializers.CharField(source="user__username")
    score = serializers.IntegerField()


class ListScoreSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    language = serializers.ReadOnlyField(source='language.language_name')
    game = serializers.ReadOnlyField(source='game.game_name')

    class Meta:
        model = Score
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    class Meta:
        model = User
        fields = ("email", "username", "password")

    def validate_email(self, value):
        validate_email(value, self.instance)
        return value

    def validate_username(self, value):
        validate_username(value)
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        username = validated_data.get("username")
        email = validated_data.get("email")
        password = validated_data.get("password")

        user = User.objects.create_user(email=email, username=username, password=password)
        user.is_active = False
        user.save()

        return user

    def update(self, instance, validated_data):
        username = validated_data.get("username")
        email = validated_data.get("email")
        password = validated_data.get("password")

        instance.username = username
        instance.email = email
        instance.set_password(password)
        instance.save()

        return instance


class ScoreSerializer(serializers.Serializer):
    language = serializers.CharField()
    game = serializers.IntegerField()

    def create(self, validated_data):
        language = get_object_or_404(Language, language_name=validated_data.get("language"))
        game = get_object_or_404(Game, pk=validated_data.get("game"))
        score = Score(user=self.context.get("user"), language=language, game=game, score=1)
        score.save()
        return score

    def update(self, instance, validated_data):
        instance.score += 1
        instance.save()
        return instance


class ArticleGameAnswerSerializer(serializers.Serializer):
    word_id = serializers.IntegerField()
    answer = serializers.CharField(allow_blank=True)

    def save(self, **kwargs):
        request = self.context["request"]
        word_id = self.validated_data.get("word_id")
        answer = self.validated_data.get("answer")

        word = get_object_or_404(Word, pk=word_id)

        is_correct_answer = (word.article.article_name == answer)

        score = None

        if (not request.user.is_anonymous) and is_correct_answer:
            score = Score.increment_score(request, word.language, get_object_or_404(Game, id=2))
            score = score.score

        return is_correct_answer, str(word), score


class VocabularyGameAnswerSerializer(serializers.Serializer):
    word_id = serializers.IntegerField()
    base_language = serializers.CharField()
    answer = serializers.CharField(allow_blank=True)

    def validate(self, data):
        word_id = data.get("word_id")
        base_language = data.get("base_language")

        word_to_translate = get_object_or_404(Word, pk=word_id)

        if word_to_translate.language.language_name == base_language:
            raise ValidationError("Base and target languages must not be equal.")

        return data

    def save(self, **kwargs):
        request = self.context["request"]
        word_id = self.validated_data.get("word_id")
        base_language = self.validated_data.get("base_language")
        answer = self.validated_data.get("answer")

        base_language = get_object_or_404(Language, language_name=base_language)
        word_to_translate = get_object_or_404(Word, pk=word_id)

        correct_translation = ""

        for synonym in word_to_translate.synonyms.all():
            if synonym.language == base_language:
                # Getting the correct answer
                if len(correct_translation) != 0:
                    correct_translation += ", "
                correct_translation += synonym.word_name

        is_correct_answer = (correct_translation == answer)

        score = None

        if (not request.user.is_anonymous) and is_correct_answer:
            score = Score.increment_score(request, word_to_translate.language, get_object_or_404(Game, id=1))
            score = score.score

        return is_correct_answer, correct_translation, score


class ConjugationGameAnswerSerializer(serializers.Serializer):
    word_id = serializers.IntegerField()
    tense = serializers.CharField()
    conjugation_1 = serializers.CharField(allow_blank=True)
    conjugation_2 = serializers.CharField(allow_blank=True)
    conjugation_3 = serializers.CharField(allow_blank=True)
    conjugation_4 = serializers.CharField(allow_blank=True)
    conjugation_5 = serializers.CharField(allow_blank=True)
    conjugation_6 = serializers.CharField(allow_blank=True)

    def save(self, **kwargs):
        request = self.context["request"]
        word_id = self.validated_data.get("word_id")
        tense = self.validated_data.get("tense")
        conjugation_1 = self.validated_data.get("conjugation_1")
        conjugation_2 = self.validated_data.get("conjugation_2")
        conjugation_3 = self.validated_data.get("conjugation_3")
        conjugation_4 = self.validated_data.get("conjugation_4")
        conjugation_5 = self.validated_data.get("conjugation_5")
        conjugation_6 = self.validated_data.get("conjugation_6")

        verb = get_object_or_404(Word, category__category_name="verbs", pk=word_id)
        conjugation = get_object_or_404(Conjugation, word=verb, tense=tense)
        language = verb.language

        correct_answer = language.personal_pronoun_1 + " " + conjugation.conjugation_1 + "\n" + \
                         language.personal_pronoun_2 + " " + conjugation.conjugation_2 + "\n" + \
                         language.personal_pronoun_3 + " " + conjugation.conjugation_3 + "\n" + \
                         language.personal_pronoun_4 + " " + conjugation.conjugation_4 + "\n" + \
                         language.personal_pronoun_5 + " " + conjugation.conjugation_5 + "\n" + \
                         language.personal_pronoun_6 + " " + conjugation.conjugation_6 + "\n"
        is_correct_answer = conjugation_1 == conjugation.conjugation_1 \
                            and conjugation_2 == conjugation.conjugation_2 \
                            and conjugation_3 == conjugation.conjugation_3 \
                            and conjugation_4 == conjugation.conjugation_4 \
                            and conjugation_5 == conjugation.conjugation_5 \
                            and conjugation_6 == conjugation.conjugation_6

        score = None

        if (not request.user.is_anonymous) and is_correct_answer:
            score = Score.increment_score(request, language, get_object_or_404(Game, id=3))
            score = score.score

        return is_correct_answer, correct_answer, score


class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ('picture',)


class RequestResetAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(self, **kwargs):
        email = self.validated_data.get("email")
        user = User.objects.filter(email=email, is_active=True).first()
        if user is not None:
            send_reset_account_email(user)


class ResetAccountSerializer(serializers.Serializer):
    password = serializers.CharField()

    def validate_password(self, value):
        validate_password(value)
        return value

    def save(self, **kwargs):
        pk = kwargs.get("pk")
        token = kwargs.get("token")
        password = self.validated_data.get("password")

        user = User.objects.filter(pk=pk, is_active=True).first()

        if (user is None) or not (default_token_generator.check_token(user, token)):
            return False

        user.set_password(password)
        user.save()
        return True


class FavoriteWordsSerializer(serializers.Serializer):
    is_favorite = serializers.BooleanField()

    def save(self, **kwargs):
        word_id = self.context["word_id"]
        user = self.context["user"]
        is_favorite = self.validated_data.get("is_favorite")

        word = get_object_or_404(Word, pk=word_id)
        app_user = get_object_or_404(AppUser, user=user)

        if is_favorite:
            app_user.favorite_words.add(word)
        else:
            app_user.favorite_words.remove(word)

        return get_object_or_404(Word, pk=word_id)