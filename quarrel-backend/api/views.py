from smtplib import SMTPException, SMTPDataError

from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.utils import json
import requests
from requests.auth import HTTPBasicAuth
import json
import logging
from rest_framework.response import Response

from django.contrib.auth.tokens import PasswordResetTokenGenerator

from .serializers import *
from .models import *


logger = logging.getLogger(__name__)


@csrf_exempt
def user_create(request):
    """
    Get or Post all information about a shop
    """
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = UserSerializer(data=data)

        if serializer.is_valid():
            return JsonResponse(data={"status": 200, "data": serializer.data, "message": "Account created"}, status=201)
        logger.info("There are errors in the user serializer: " + str(serializer.errors))
        return JsonResponse(data={"status": 400, "data": serializer.errors}, status=400)
    else:
        return JsonResponse(status=400, data={'status': 400, 'message': 'method not allowed'})


@csrf_exempt
def user_store(request):
    """
    Get or Post all information about users
    """
    '''
    :param serializer: serializer for the model_object
    :param model_object: the model class to be requested
    :param request: generic django config request object
    :param id: id of database instance
    :return:
    '''
    user_auth_tuple = TokenAuthentication().authenticate(request)
    if user_auth_tuple is None:
        return JsonResponse(status=404, data={'status': 404, 'message': 'invalid authentication'})
    else:
        (user, token) = user_auth_tuple

    if request.method == 'GET':
        obj = model_object.objects.get(username=user)
        serializer = UserSerializer(obj)
        return JsonResponse(data={"status": 200, "data": serializer.data}, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        obj = model_object.objects.get(username=user)
        serializer = UserSerializer(data=data, instance=obj, partial=True)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(data={'status': 201, 'message': 'Success!'}, status=201)

        return JsonResponse(data={"status": 400, "data": errors}, status=400)

    elif request.method == 'DELETE':
        obj = model_object.objects.get(username=user)
        logger.info(obj)
        obj.delete()
        serializer = UserSerializer(obj)
        return JsonResponse(data={"status": 204, "data": serializer.data}, status=204)




class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
        })


@csrf_exempt
def ping(request):
    if request.method == 'GET':
        return JsonResponse(status=200, data={'message': 'pong'})
