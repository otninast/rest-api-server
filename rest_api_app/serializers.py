from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from . import models
from . import utils
from .models import (
    TrainingMenu, TrainingProgram, MenuName, ResultTime, LapTime, ImageTest,
    Profile, Profile
)
from statistics import mean


class ProfileSerializer_(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = '__all__'


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = ProfileSerializer_(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'profile')
        # fields = ('id', 'username', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        password = validated_data.get('password')
        validated_data['password'] = make_password(password)
        username = validated_data.get('username')
        user = User(**validated_data)
        user.save()
        user_instance = User.objects.get(username=username)
        # print('>>>>>>>>>>>>>>>', user_instance)
        profile = Profile(user=user_instance)
        # print('>>>>>>>>>>>>>>>', profile)
        profile.save()
        return user


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class MenuNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MenuName
        fields = '__all__'


class LapTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LapTime
        fields = [
                'id',
                'result_time',
                'num_of_lap',
                'lap_time'
                ]


class ResultTimeSerializer(serializers.ModelSerializer):

    # lap_time = serializers.SerializerMethodField()
    lap_time = LapTimeSerializer(read_only=True, many=True, source='laptimes')

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related('laptimes')
        return queryset

    class Meta:
        model = models.ResultTime
        fields = [
                'id',
                'training_menu',
                'num_of_order',
                'result_time',
                'lap_time',
                ]

    def get_lap_time(self, obj):
        try:
            lap_time_abstruct_contents = LapTimeSerializer(
                LapTime.objects.all().filter(
                    result_time=ResultTime.objects.get(id=obj.id)
                    ), many=True
            ).data
            return lap_time_abstruct_contents

        except:
            lap_time_abstruct_contents = None
            return lap_time_abstruct_contents


class TrainingMenuSerializer(serializers.ModelSerializer):
    # menu_name = serializers.SerializerMethodField()
    menu_name = MenuNameSerializer(read_only=True)
    menu_name_id = serializers.PrimaryKeyRelatedField(
                            queryset=MenuName.objects.all(),
                            write_only=True
                            )
    # result_time = serializers.SerializerMethodField()
    result_time = ResultTimeSerializer(
        read_only=True, many=True, source='resulttimes')

    mean_time = serializers.SerializerMethodField()
    max_time = serializers.SerializerMethodField()
    min_time = serializers.SerializerMethodField()
    graph = serializers.SerializerMethodField()

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related(
            'resulttimes', 'resulttimes__laptimes')
        return queryset

    class Meta:
        model = TrainingMenu
        fields = [
                'id',
                'training_program',
                'menu_name',
                'menu_name_id',
                'distance',
                'style',
                'time_circle',
                'how_many_times',
                'result_time',
                'mean_time',
                'max_time',
                'min_time',
                'graph',
                ]

    def get_result_time(self, obj):
        try:
            result_time_abstruct_contents = ResultTimeSerializer(
                ResultTime.objects.all().filter(
                    training_menu=TrainingMenu.objects.get(id=obj.id)
                    ), many=True
            ).data
            return result_time_abstruct_contents

        except:
            result_time_abstruct_contents = None

            return result_time_abstruct_contents

    def create(self, validated_data):
        validated_data['menu_name'] = validated_data.get('menu_name_id', None)

        if validated_data['menu_name'] is None:
            raise serializers.ValidationError('menu name not found.')

        del validated_data['menu_name_id']

        return TrainingMenu.objects.create(**validated_data)

    def get_mean_time(self, obj):
        timelist = list(obj.resulttimes.values_list('result_time', flat=True))
        mean_time = round(mean(timelist), 2)
        return mean_time

    def get_max_time(self, obj):
        timelist = list(obj.resulttimes.values_list('result_time', flat=True))
        max_time = max(timelist)
        return max_time

    def get_min_time(self, obj):
        timelist = list(obj.resulttimes.values_list('result_time', flat=True))
        min_time = min(timelist)
        return min_time

    def get_graph(self, obj):
        # print('--------------------')
        y = list(obj.resulttimes.values_list('result_time', flat=True))
        # x = obj.resulttimes.values('laptimes')
        xx = obj.resulttimes.prefetch_related('laptimes')
        # print('------------------')
        # xxx = xx[0].laptimes
        # print(xxx)
        # print(type(xxx))
        # print(dir(xxx))
        # print('------------------')
        # xx = obj.resulttimes
        x = [list(i.laptimes.values_list('lap_time', flat=True)) for i in xx]
        # print('time', y)
        # print('lap', x)
        # print('type', type(x))
        # print('dir', dir(x))
        # print('--------------------')
        graph = utils.make_img(y, x)
        # return obj.make_graph()
        return graph


class TrainingProgramSerializer(serializers.ModelSerializer):
    # training_menu = serializers.SerializerMethodField()
    training_menu = TrainingMenuSerializer(
        read_only=True, many=True, source='trainingmenus')
    # username = UserSerializer()
    username = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
                        queryset=User.objects.all(),
                        write_only=True
                        )

    class Meta:
        model = models.TrainingProgram
        fields = [
                'id',
                'username',
                'training_date',
                'daily_reflection',
                'self_assessment_score',
                'training_image',
                'training_menu',
                'user_id',
        ]

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('username')
        queryset = queryset.prefetch_related(
            'trainingmenus',
            'trainingmenus__resulttimes',
            'trainingmenus__resulttimes__laptimes')
        return queryset

    def get_training_menu(self, obj):
        try:
            training_menu_abstruct_contents = TrainingMenuSerializer(
                TrainingMenu.objects.all().filter(
                    training_program=TrainingProgram.objects.get(id=obj.id)
                    ), many=True
            ).data
            return training_menu_abstruct_contents

        except:
            training_menu_abstruct_contents = None

            return training_menu_abstruct_contents

    # def perform_create(self, serializer):
    #     serializer.save(username=self.request.user)

    def create(self, validated_data):
        validated_data['username'] = validated_data.get('user_id', None)
        # print('-------------------------')
        # print(validated_data)

        if validated_data['username'] is None:
            raise serializers.ValidationError('user not found.')

        del validated_data['user_id']

        return TrainingProgram.objects.create(**validated_data)


class ImageTestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImageTest
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True)

    class Meta:
        model = Profile
        fields = ['id',
                  'user',
                  'user_id',
                  'first_name',
                  'family_name',
                  'birthday',
                  'sex',
                  'profile_image',
                  'style_one',
                  ]

    def create(self, validated_data):
        validated_data['user'] = validated_data.get('user_id', None)
        # print('-------------------------')
        # print(validated_data)

        if validated_data['user'] is None:
            raise serializers.ValidationError('user not found.')

        del validated_data['user_id']

        return TrainingProgram.objects.create(**validated_data)
