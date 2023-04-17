from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Position
from .serializers import PositionSerializer, TrackingPositionSerializer
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from rest_framework import status
from datetime import datetime, timedelta
import json


class PositionTrackingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, symbol_name='XBTUSDM'):
        # code to start position tracking for the authenticated user
        user = request.user
        user_kucoin_secret_items = {'kucoin_api_key': user.kucoin_api_key,
                                    'kucoin_api_secret': user.kucoin_api_secret,
                                    'kucoin_passphrase': user.kucoin_passphrase}

        my_app_name = 'position'
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=10,
            period=IntervalSchedule.SECONDS,
        )
        try:
            PeriodicTask.objects.create(
                interval=schedule,  # we created this above.
                name=f'{user.id}_{symbol_name}',  # simply describes this periodic task. (unique)
                task=f'{my_app_name}.tasks.tracking_task',  # name of task.
                kwargs=json.dumps(dict(user=user_kucoin_secret_items, context={'user_id': user.pk})),
                expires=datetime.utcnow() + timedelta(seconds=3600)  # expire time
            )
        except Exception as err:
            return Response({"message": f"Maybe you already set up tracking for symbol = {symbol_name}"},
                            status=status.HTTP_409_CONFLICT)
        return Response({'message': f'Position tracking started symbol {symbol_name}'}, status=status.HTTP_201_CREATED)


class OpenPositionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        positions = Position.objects.filter(user=user).order_by('created_at')
        serializer = PositionSerializer(positions, many=True)
        return Response(serializer.data)
