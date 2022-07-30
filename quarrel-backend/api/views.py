from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.utils import json
import json
import logging
import random
import threading
from .Websocket import *
from rest_framework.response import Response

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
        obj = Quarreler.objects.get(username=user)
        serializer = UserSerializer(obj)
        return JsonResponse(data={"status": 200, "data": serializer.data}, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        obj = Quarreler.objects.get(username=user)
        serializer = UserSerializer(data=data, instance=obj, partial=True)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(data={'status': 201, 'message': 'Success!'}, status=201)

        return JsonResponse(data={"status": 400, "data": serializer.error_messages}, status=400)

    elif request.method == 'DELETE':
        obj = Quarreler.objects.get(username=user)
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
        return JsonResponse(status=200, data={'message': "pong"})


def read_words():
    # words = json.load(open(os.path.join(os.getcwd(), "quarrel-backend/api/dictionary.json")))
    words = json.load(open(os.path.join(os.getcwd(), 'api\\dictionary.json')))
    return words


@csrf_exempt
def choose_word(request):
    if request.method == 'GET':
        try:
            words = read_words()
            choices = random.sample(words, k=15)
            # serializer = GameSerializer(words, many=True)
            return JsonResponse(data={"status": 200, "data": choices}, safe=False)
        except BaseException as err:
            return JsonResponse(data={"status": 400, "data": err}, safe=False)


@csrf_exempt
def is_word_valid(request):
    data = JSONParser().parse(request)
    if request.method == 'POST':
        words = read_words()
        is_valid = data["word"] in words
        return JsonResponse(data={"status": 200, "data": is_valid}, safe=False)


is_socket_running = False
@csrf_exempt
def start_websocket(request):
    global is_socket_running
    if not is_socket_running:
        sock = Websocket()
        t = threading.Thread(target=sock.run, daemon=True)
        t.start()
        is_socket_running = True
        return JsonResponse(data={"message": "Socket started."}, status=200)
    return JsonResponse(data={"message": "Socket is running."}, status=202)


@csrf_exempt
def get_previous_game_data(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        primary_user = data['guestId']
        game_id = data['gameId']
        try:
            cur_game = Game.objects.get(primary_guest=primary_user, game_id=game_id)
            guess_list = [cur_game.guess1, cur_game.guess2, cur_game.guess3, cur_game.guess4, cur_game.guess5, cur_game.guess6]
            previous_guesses = [json.loads(guess) for guess in guess_list if guess is not None]
            return JsonResponse(data=previous_guesses, safe=False)
        except:
            return JsonResponse(status=400, data=[], safe=False)


def check_guesses(obj, previous_guesses):
    guess_list = [obj.guess1, obj.guess2, obj.guess3, obj.guess4, obj.guess5, obj.guess6]
    for inc, saved in zip(previous_guesses, guess_list):
        if inc != json.loads(saved):
            return JsonResponse(status=400, data={"status": 400, "data": {"message": "guess doesnt match"}}, safe=False)
    return len(previous_guesses) + 1

@csrf_exempt
def normal_game(request):
    obj = False
    if request.method == 'GET':
        serializer = GameSerializer(obj, many=True)
        return JsonResponse(data={"status": 200, "data": serializer.data}, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        primary_user = data['guestId']
        game_id = data['gameId']
        answer = data['answer']
        try:
            cur_game = Game.objects.get(primary_guest=primary_user, game_id=game_id)
            previous_guesses = data.get('previousGuesses')
            guess = json.dumps(data.get('guessState'))
            if cur_game.answer is None:
                cur_game.answer = data["answer"]
            if cur_game.guess1 is None or json.loads(cur_game.guess1) is None:
                cur_game.guess1 = guess
            else:
                update_guess = check_guesses(cur_game, previous_guesses)
                if update_guess == 2:
                    cur_game.guess2 = guess
                if update_guess == 3:
                    cur_game.guess3 = guess
                if update_guess == 4:
                    cur_game.guess4 = guess
                if update_guess == 5:
                    cur_game.guess5 = guess
                if update_guess == 6:
                    cur_game.guess6 = guess
            if json.loads(guess) == answer:
                cur_game.correct_guess = len(previous_guesses)
                cur_game.save()
                return JsonResponse(data={"status": 200, "data": {"message": "winner"}}, safe=False)
            cur_game.save()
            if len(previous_guesses) == 5:
                return JsonResponse(data={"status": 200, "data": {"message": "loser"}}, safe=False)
            return JsonResponse(data={"status": 200, "data": {"message": "continue"}}, status=200)
        except:
            Game.objects.create(
                primary_guest=primary_user,
                game_id=game_id,
            )
            return JsonResponse(data={"status": 200, "data": {"message": "game created"}}, status=200)







@csrf_exempt
def ranked_game(request):
    obj = False
    if request.method == 'GET':
        serializer = GameSerializer(obj, many=True)
        return JsonResponse(data={"status": 200, "data": serializer.data}, safe=False)




