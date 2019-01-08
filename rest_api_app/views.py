from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from rest_framework import (
    viewsets, permissions, status
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, action

from rest_framework_jwt.authentication import JSONWebTokenAuthentication
import json

from .serializers import (
    UserSerializer, GroupSerializer,
    TrainingProgramSerializer, TrainingMenuSerializer,
    ResultTimeSerializer, LapTimeSerializer,
    ImageTestSerializer, ProfileSerializer,
)

from rest_api_app import models, serializers
from rest_api_app.utils import str_to_float, b64_to_image


class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProfileViewSet(viewsets.ModelViewSet):

    queryset = models.Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return models.Profile.objects.filter(user=self.request.user)

    @csrf_exempt
    def create(self, request, *args, **kwargs):
        # print('>>>>>>>>>>>>>>>>>', request.data['user'])
        # request.data['user'] = User.objects.filter(id=request.data['user'])[0]
        # print('>>>>>>>>>>>>>>>>>', type(request.data['user']))
        if 'base64' in request.data['profile_image']:
            base64_data = request.data['profile_image']
            request.data['profile_image'] = b64_to_image(request.data['profile_image'])

        serializer = self.get_serializer(data=request.data)
        print('------------>>>>>>>>>>>',serializer)
        serializer.is_valid(raise_exception=True)
        print('------------>>>>>>>>>>>',serializer.validated_data)
        # print('------------>>>>>>>>>>>',serializer.errors)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @csrf_exempt
    def update(self, request, pk=None, *args, **kwargs):
        kwargs['partial'] = True
        instance = self.get_object()
        if 'base64' in self.request.data['profile_image']:
            base64_data = self.request.data['profile_image']
            self.request.data['profile_image'] = b64_to_image(self.request.data['profile_image'])
        else:
            self.request.data['profile_image'] = instance.profile_image


        serializer = self.get_serializer(instance, data=self.request.data, partial=kwargs['partial'])
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class Logout(APIView):
    def get(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class GroupViewSet(viewsets.ModelViewSet):

    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class MenuNameViewSet(viewsets.ModelViewSet):

    queryset = models.MenuName.objects.all()
    serializer_class = serializers.MenuNameSerializer


class TrainingProgramViewSet(viewsets.ModelViewSet):

    queryset = models.TrainingProgram.objects.all().order_by('-training_date')
    serializer_class = serializers.TrainingProgramSerializer
    authentication_classes = (JSONWebTokenAuthentication,)
    lookup_field = 'pk'


class TrainingMenuViewSet(viewsets.ModelViewSet):

    queryset = models.TrainingMenu.objects.all()
    serializer_class = serializers.TrainingMenuSerializer


class ResultTimeViewSet(viewsets.ModelViewSet):

    queryset = models.ResultTime.objects.all()
    serializer_class = serializers.ResultTimeSerializer


class LapTimeViewSet(viewsets.ModelViewSet):

    queryset = models.LapTime.objects.all()
    serializer_class = serializers.LapTimeSerializer


@csrf_exempt
@api_view(['POST'])
def DataInput(request):

    request_json = json.loads(request.body)
    if request_json['trainingData']['training_image']:
        b64data = request_json['trainingData']['training_image']
        image = b64_to_image(b64data)

        request_json['trainingData']['training_image'] = image

    request_json['trainingData']['username'] = request.user.id
    request_json['trainingData']['user_id'] = request.user.id

    seri_training = TrainingProgramSerializer(
        data=request_json["trainingData"])

    if not seri_training.is_valid():
        return Response({
                        "status": "failure to save training",
                        "status_message": seri_training.errors,
                        "data": seri_training.data
                        }, status=status.HTTP_400_BAD_REQUEST)

    # else:
    training_program = seri_training.save()
    request_json['menuData']['training_program'] = training_program.id
    menu_name_str = request_json['menuData']['menu_name']
    menu_name_obj = models.MenuName.objects.filter(menu_name=menu_name_str)
    request_json['menuData']['menu_name'] = menu_name_obj[0].id
    request_json['menuData']['menu_name_id'] = menu_name_obj[0].id
    seri_menu = TrainingMenuSerializer(data=request_json["menuData"])

    if not seri_menu.is_valid():
        return Response({
                        "status": "failure to save training detail",
                        "status_message": seri_menu.errors
                        }, status=status.HTTP_400_BAD_REQUEST)

    # else:
    training_menu = seri_menu.save()

    lap_time_list = []

    for data in request_json['resultTime']:

        data['training_menu'] = training_menu.id
        data['result_time'] = str_to_float(data['result_time_str'])

        lap_time_list.append(data['lapTime'])

        # print('---------------->>>>>>>>>>>', [i['lap_time'] for i in data['lapTime']])

    seri_result = ResultTimeSerializer(
        data=request_json['resultTime'], many=True)
    # 複数を保存するための処理

    if not seri_result.is_valid():
        return Response({
                        "status": "failure to save result time",
                        "status_message": seri_menu.errors
                        }, status=status.HTTP_400_BAD_REQUEST)

    # else:
    # print(request_json)
    result_time = seri_result.save()
    for lap_time_set, result_time_set in zip(lap_time_list, result_time):
        # print('----------------------------------------')
        # lap_time_set['result_time'] = result_time_set.id
        # print(len(lap_time_set))

        list(map(lambda x: x.update({'result_time': result_time_set.id}), lap_time_set))
        list(map(lambda x: x.update({'lap_time': str_to_float(x['lap_time'])}), lap_time_set))
        seri_lap = LapTimeSerializer(data=lap_time_set, many=True)

        if not seri_lap.is_valid():
            return Response({
                            "status": "failure to save result time",
                            "status_message": seri_lap.errors
                            }, status=status.HTTP_400_BAD_REQUEST)
        seri_lap.save()
        # print(lap_time_set[0])
        # print(result_time_set.id)
    # print('---------------->>>>>>>>>>>', lap_time_list)
    # print('>>>>>>>>>>>>>>>>>>>', result_time)


    return Response({
                    "status": "success",
                    "status_message": "User Created Successfully"
                    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def LoginUser(request):
    data = {}

    request_user_instance = User.objects.get(id=request.user.id)
    data['user'] = UserSerializer(request_user_instance).data
    # print('User-----', data['user'])
    # print('----------------->>>>>', models.Profile.objects.get(user=request.user))

    # if data['user']['profile'] is not None:
    request_user_profile_instance = models.Profile.objects.get(user=request.user)
    data['profile'] = ProfileSerializer(request_user_profile_instance).data
        # print('Profile-----', data['profile'])

    # else:
    #     data['profile'] = {'birthday': None,
    #                         'family_name': None,
    #                         'first_name': None,
    #                         'profile_image': None,
    #                         'sex': None,
    #                         'style_one': None,
    #                         'user': request.user.id,
    #                         }


    return Response({
                    "data": data,
                    "status": "success",
                    "status_message": "User and Profile instance"
                    },
                    status=status.HTTP_200_OK,
                    )


@csrf_exempt
@api_view(['POST'])
def test_func(request):
    data = request.FILES.get('image_key')
    # print('dir-------------', dir(data))
    # print('type-------------@@@@@@@@', type(data))
    # print('data---------------@@@@@@@@@', data)
    dict = {'image': data}
    seri = ImageTestSerializer(data=dict)
    # print('seri----------------', seri)

    torf = seri.is_valid()
    # print('true or false', torf)
    # print('error----------------', seri.errors)
    seri.save()
    return Response({"status": "success",
                     "status_message": "User Created Successfully"
                     }, status=status.HTTP_200_OK)








#
#
# { "id": 5,
#   "username": { "id": 1,
#                 "username": "otninast" },
#   "training_date": "2019-01-01",
#   "daily_reflection": "@@@@@@@@",
#   "self_assessment_score": 5,
#   "training_image": "http://127.0.0.1:8000/image/image/temp_D5t5XS6.png",
#   "training_menu": null
#   }
#
#
#   {
#   "id": 5,
#   "username": { "id": 1, "username": "otninast" },
#   "training_date": "2019-01-01",
#   "daily_reflection": "@@@@@@@@",
#   "self_assessment_score": 5,
#   "training_image": "http://127.0.0.1:8000/image/image/temp_D5t5XS6.png",
#   "training_menu":
#     [{
#     "id": 39,
#     "training_program": 5,
#     "menu_name": { "id": 5, "menu_name": "All-Out" },
#     "distance": 100,
#     "style": "Fr",
#     "time_circle": 60,
#     "how_many_times": 3,
#     "result_time":
#         [{
#         "id": 36,
#         "training_menu": 39,
#         "num_of_order": 1,
#         "result_time": 60.8,
#         "rap_time": []
#         },
#         {
#         "id": 37,
#         "training_menu": 39,
#         "num_of_order": 2,
#         "result_time": 63.7,
#         "rap_time": []
#         },
#         { "id": 38,
#         "training_menu": 39,
#         "num_of_order": 3,
#         "result_time": 62.09,
#         "rap_time": []
#         }
#     ]}
# ]}
