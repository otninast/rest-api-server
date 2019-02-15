from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from rest_framework import (
    viewsets, permissions, status
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

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
            request.data['profile_image'] = b64_to_image(
                request.data['profile_image'])

        serializer = self.get_serializer(data=request.data)
        # print('------------>>>>>>>>>>>', serializer)
        serializer.is_valid(raise_exception=True)
        # print('------------>>>>>>>>>>>', serializer.validated_data)
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
            self.request.data['profile_image'] = b64_to_image(
                self.request.data['profile_image'])
        else:
            self.request.data['profile_image'] = instance.profile_image

        serializer = self.get_serializer(
            instance, data=self.request.data, partial=kwargs['partial'])
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
    serializer_class = TrainingProgramSerializer
    authentication_classes = (JSONWebTokenAuthentication,)
    # lookup_field = 'pk'

    def get_queryset(self):
        queryset = models.TrainingProgram.objects.all().order_by('-training_date')
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        # print('-------------------------------------')
        # qs_ = queryset
        # t_m_l = [list(a.trainingmenus.values())[0] for a in qs_]
        # t_m = [a.trainingmenus for a in qs_]
        # qs = [a.values('resulttimes') for a in t_m]
        #
        # print('viewset', qs)
        # # print('[0]', qs[0])
        # print('type', type(qs))
        # print('dir', dir(qs))
        # print(dir(self))
        # print('-------------------------------------')
        return queryset


class TrainingMenuViewSet(viewsets.ModelViewSet):

    queryset = models.TrainingMenu.objects.all()
    serializer_class = serializers.TrainingMenuSerializer

    def get_queryset(self):
        queryset = models.TrainingMenu.objects.all()
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset


class ResultTimeViewSet(viewsets.ModelViewSet):

    queryset = models.ResultTime.objects.all()
    serializer_class = serializers.ResultTimeSerializer

    def get_queryset(self):
        queryset = models.ResultTime.objects.all()
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset


class LapTimeViewSet(viewsets.ModelViewSet):

    queryset = models.LapTime.objects.all()
    serializer_class = serializers.LapTimeSerializer


@csrf_exempt
@api_view(['POST'])
def DataInput(request):

    request_json = json.loads(request.body)

    program = save_training_program(request, request_json['trainingData'])

    if program is False:
        return Response({"status": "failure to save training detail",
                         }, status=status.HTTP_400_BAD_REQUEST)

    menudata = save_training_menu(request_json['menuData'], program)
    if menudata is False:
        return Response({"status": "failure to save training detail",
                         }, status=status.HTTP_400_BAD_REQUEST)

    result, lap_time_list = save_result_time(
        request_json['resultTime'], menudata)
    if result is False:
        return Response({"status": "failure to save training detail",
                         }, status=status.HTTP_400_BAD_REQUEST)

    lap = save_lap_time(lap_time_list, result)

    return Response({"status": "success",
                     "status_message": "Training includeing Laptime Created Successfully"
                     }, status=status.HTTP_200_OK)


def save_training_program(request, program):
    try:
        if program['training_image']:
            b64data = program['training_image']
            image = b64_to_image(b64data)
            program['training_image'] = image

        program['username'] = request.user.id
        program['user_id'] = request.user.id

        serializer_training = TrainingProgramSerializer(data=program)

        if not serializer_training.is_valid():
            return False

        training_program = serializer_training.save()

        return training_program

    except:
        return False


def save_training_menu(data, training_program):
    try:
        data['training_program'] = training_program.id
        menu_name_str = data['menu_name']
        menu_name_obj = models.MenuName.objects.filter(menu_name=menu_name_str)
        data['menu_name'] = menu_name_obj[0].id
        data['menu_name_id'] = menu_name_obj[0].id
        serializer_menu = TrainingMenuSerializer(data=data)

        if not serializer_menu.is_valid():
            return False

        training_menu = serializer_menu.save()

        return training_menu

    except:
        return False


def save_result_time(result, training_menu):
    try:
        lap_time_list = []
        for data in result:
            data['training_menu'] = training_menu.id
            data['result_time'] = str_to_float(data['result_time_str'])
            lap_time_list.append(data['lapTime'])

        serializer_result = ResultTimeSerializer(data=result, many=True)

        if not serializer_result.is_valid():
            return False, False

        result_time = serializer_result.save()
        # print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        # print(lap_time_list)
        return result_time, lap_time_list

    except:
        return False, False


def save_lap_time(lap_time_list, result):

    try:
        for lap_time_set, result_time_set in zip(lap_time_list, result):

            list(map(lambda x: x.update(
                {'result_time': result_time_set.id}), lap_time_set))
            list(map(lambda x: x.update(
                {'lap_time': str_to_float(x['lap_time'])}), lap_time_set))
            serializer_lap = LapTimeSerializer(data=lap_time_set, many=True)

            if not serializer_lap.is_valid():
                return '------ serializer invalid'

            serializer_lap.save()

        return '------- serializer valid!!!'

    except TypeError:

        return '------- could not save lap time'


@api_view(['GET'])
def SchoolsName(request):
    from rest_api_app.utils import school16

    _, Team16 = school16()
    data = {}
    data['schools'] = sorted(list(Team16))
    data['years'] = [y for y in range(2008, 2018)]
    data['sex'] = ['Man', 'Woman']
    data['distances'] = [50, 100, 200, 400, 800]
    data['styles'] = ['Fr', 'Ba', 'Br', 'Fly', 'IM']

    return Response({"status": "success",
                     "status_message": "success",
                     "data": data
                     }, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def GraphAndTableData(request):
    from rest_api_app.utils import school16
    from io import BytesIO
    from base64 import b64encode
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    import seaborn as sns

    Df, _ = school16()
    rq_data = json.loads(request.body)

    sex_dic = {'Man': 'm', 'Woman': 'w'}

    school = rq_data['school']
    year = rq_data['year']
    style = [rq_data['style'].lower()]
    distance = [rq_data['distance']]
    sex = [sex_dic[s] for s in rq_data['sex']]

    col = ['Year', 'Name', 'Time', 'Rank', 'Team', 'Age', 'Sex', 'Style',
           'Distance', 'kyu']

    try:
        dfa = Df[Df.Competition == '16高']
        # print(dfa.head())
        # print(dfa[dfa.Team.isin(school)])

        dfc = dfa[(dfa.Team.isin(school)) &
                  (dfa.Year.isin(year)) &
                  (dfa.Style.isin(style)) &
                  (dfa.Distance.isin(distance)) &
                  (dfa.Sex.isin(sex))]
        # dfc = dfc[col]

        # print(dfc.head())
        rows = [r.to_dict() for i, r in dfc[col].iterrows()]

        header = [{'text': x, 'value': x} for x in dfc[col].columns]

        # table = dfc.to_html(index=False)
        plt.style.use('seaborn-deep')
        fig, ax = plt.subplots()
        ax = sns.boxplot(dfc.Year, dfc.kyu, hue='Sex', data=dfc)
        # ax = sns.boxplot(dfc.Year, dfc.Time_sec, hue='Team', data=dfc)
        canvas = FigureCanvasAgg(fig)

        png_output = BytesIO()
        canvas.print_png(png_output)
        bs64 = b64encode(png_output.getvalue())
        image = str(bs64)
        image = image[2:-1]
        img = 'data:image/png;base64,{}'.format(image)

        # table = dfc[col].to_html(index=False)

        dict = {
            'school': school,
            'image': img,
            'header': header,
            'rows': rows,
            # 'name': dfc.Name.tolist(),
            # 'time': dfc.Time.tolist(),
            # 'team': dfc.Team.tolist(),
            # 'style': dfc.Style.tolist(),
            # 'sex': dfc.Sex.tolist(),
            # 'distanse': dfc.Distance.tolist(),
            # 'kyu': dfc.kyu.tolist(),
            # 'rank': dfc.Rank.tolist()
            }
        plt.close()

        return Response({"status": "success",
                         "status_message": "",
                         "data": dict
                         }, status=status.HTTP_200_OK)

    except:
        dict = {'table': 'No Data...'}
        return Response({"status": "success",
                         "status_message": "",
                         "data": dict
                         }, status=status.HTTP_200_OK)


@api_view(['GET'])
def LoginUser(request):
    data = {}

    request_user_instance = User.objects.get(id=request.user.id)
    data['user'] = UserSerializer(request_user_instance).data

    request_user_profile_instance = models.Profile.objects.get(
        user=request.user)
    data['profile'] = ProfileSerializer(request_user_profile_instance).data

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
