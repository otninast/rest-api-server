from django.contrib.auth.middleware import get_user
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from django.conf import settings

from rest_framework_jwt.authentication import JSONWebTokenAuthentication

import base64
from django.core.files.base import ContentFile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg

import os
from io import BytesIO

import pandas as pd


SEX_CHOICES = (
    ('Man', 'Man'),
    ('Woman', 'Woman'),
    ('Other', 'Other')
)

STYLE_CHOICES = (
    ('Fr', 'Fr'),
    ('Ba', 'Ba'),
    ('Br', 'Br'),
    ('Fly', 'Fly'),
    ('IM', 'IM'),

)

DISTANCE_CHOICES = (
    (25, 25),
    (50, 50),
    (100, 100),
    (200, 200),
    (400, 400),
    (800, 800),
)

ONE_TO_FIVE_CHOICES = [
    (num, num) for num in range(0, 6)
]

ONE_TO_TEN_CHOICES = [
    (num, num) for num in range(0, 11)
]

ONE_TO_SIXTY_CHOICE = [
    (num, num) for num in range(0, 60)
]

# PATH = os.path.join(os.path.join(os.path.dirname(__file__), 'Result_all.csv'))


def school16():
    PATH = os.path.join(settings.STATIC_URL, 'Result_all.csv')
    #
    Df = pd.read_csv(PATH)
    Team16 = set(Df[Df.Competition == '16高'].Team)
    Df16 = Df[Df.Team.isin(Team16)]
    return Df16, Team16

# TIME_CIRCLE = [
#     (circle)
# ]


# def get_user_jwt(request):
#     user = get_user(request)
#     if user.is_authenticated():
#         return user
#     try:
#         user_jwt = JSONWebTokenAuthentication().authenticate(Request(request))
#         if user_jwt is not None:
#             return user_jwt[0]
#     except:
#         pass
#     return user
#
#
# class AuthenticationMiddlewareJWT(object):
#     def process_request(self, request):
#         assert hasattr(request, 'session'), "The Django authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
#
#         request.user = SimpleLazyObject(lambda: get_user_jwt(request))


# from django.utils.functional import SimpleLazyObject
# from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
# from rest_framework.exceptions import ValidationError
#
# #from rest_framework.request from Request
# class AuthenticationMiddlewareJWT(object):
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#
#     def __call__(self, request):
#         request.user = SimpleLazyObject(lambda: self.__class__.get_jwt_user(request))
#         if not request.user.is_authenticated:
#             token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
#             print(token)
#             data = {'token': token}
#             try:
#                 valid_data = VerifyJSONWebTokenSerializer().validate(data)
#                 user = valid_data['user']
#                 request.user = user
#             except ValidationError as v:
#                 print("validation error", v)
#
#
#         return self.get_response(request)

class AuthenticationMiddlewareJWT(MiddlewareMixin):
    """
    Middleware for auth django and jwt
    https://martinpeveri.wordpress.com/2018/01/
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = SimpleLazyObject(
            lambda: self.__class__.get_jwt_user(request)
        )
        return self.get_response(request)

    @staticmethod
    def get_jwt_user(request):
        user = get_user(request)
        if user.is_authenticated:
            return user
        jwt_authentication = JSONWebTokenAuthentication()
        if jwt_authentication.get_jwt_value(request):
            user, jwt = jwt_authentication.authenticate(request)
        return user


def str_to_float(data):

    # data_list = data.split(':')
    min = int(data[0:2]) * 60
    sec = int(data[2:4])
    msec = float(data[4:6])/100

    float_data = min + sec + msec

    return float_data


def b64_to_image(b64data):
    """
    https://gist.github.com/yprez/7704036#file-fields-py
    """
    format, imgstr = b64data.split(';base64,')  # format ~= data:image/X,
    ext = format.split('/')[-1]  # guess file extension

    data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
    return data


def make_img_b64_from_dataframe(df, laplist):
    plt.style.use('seaborn-deep')
    order = list(df.index+1)

    fig = plt.figure(figsize=(10, 4))
    ax1 = fig.add_subplot(111)
    ax1.plot(df.index + 1, df['time'], 'ok-', label='Result Time')
    # print(laplist)

    if laplist[0]:
        ax2 = ax1.twinx()
        bar_width = 0.4 / (len(laplist[0])+1)
        width_between_order = 0

        for index in range(0, len(laplist)):
            last_lap = df.time[index] - sum(laplist[index])
            laplist[index].append(last_lap)

        for index, lap in enumerate(zip(*laplist)):
            ax2.bar([x+width_between_order for x in order], lap,
                    label='lap time{}'.format(index+1), alpha=0.5, width=bar_width)
            width_between_order += bar_width

        ax2.set_ylim(min(laplist[0])/1.2, max(laplist[-1])*1.1)

    ax1.set_xlim(min(order)-1, max(order)+1)

    ax1.set_xticks(range(min(order)-1, max(order)+1, 1))

    ax1.set_title('Result Time & Lap Time')
    ax1.set_xlabel('Order')
    ax1.set_ylabel('Time[sec]')
    fig.legend()

    canvas = FigureCanvasAgg(fig)
    png_output = BytesIO()
    canvas.print_png(png_output)
    bs64 = base64.b64encode(png_output.getvalue())
    image = str(bs64)
    image = image[2:-1]
    img_html_tag = 'data:image/png;base64,{}'.format(image)
    plt.close()

    return img_html_tag


def make_img(time_list, laplist):
    # t = Result_Time.objects.filter(trainingmenu=self)
    # time_list = [i.time for i in t]
    df = pd.DataFrame({'time': time_list})
    src_b64 = make_img_b64_from_dataframe(df, laplist)
    # img = '<img src="{}" class="img-fluid img-thumbnail"/>'.format(img_tag)
    return src_b64
