from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse
from django.utils.timezone import make_aware
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
    throttle_classes,
    parser_classes,
    )
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser
from .serializers import UserSerializer
import stripe
from stripe.error import SignatureVerificationError
import datetime
from .models import PaymentSession, User

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        create_stripe_customer(user)
        return Response(status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def success(request):
    try:
        session = PaymentSession.objects.get(session_id= request.query_params['session_id'])
    except PaymentSession.DoesNotExist:
        return Response()@throttle_classes()
    return Response({'msg': f"Hi {session.user} - Your subscription is active now."})

@api_view(['GET'])
@permission_classes([AllowAny])
def cancel(request):
    return Response({'msg': f"Subscription payment failed."})

@api_view(['GET'])
@throttle_classes([UserRateThrottle])
def pay_subscription(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if not request.user.stripe_customer_id:
        customer_created = create_stripe_customer(request.user)
        if not customer_created:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        session = stripe.checkout.Session.create(
            #success_url='http://localhost:8000/api/v1/success/?session_id={CHECKOUT_SESSION_ID}',
            #cancel_url = 'http://localhost:8000/api/v1/cancel/',
            success_url=settings.BASE_URL+reverse('payment_success')+'?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=settings.BASE_URL+reverse('payment_failed'),
            mode='subscription',
            line_items=[{
                'price': settings.STRIPE_PRICE_ID,
                'quantity': 1
            }],
            customer=request.user.stripe_customer_id
        )
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    session_record = PaymentSession(user=request.user, session_id = session.id)
    session_record.save()
    return Response({'message': "Please refer to provided url to pay your subscription fee.", 'link': session.url})

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@parser_classes([JSONParser])
def stripe_webhook(request):
    event = None
    payload = request.body.decode('utf-8')
    sig_header = request.headers['Stripe_Signature']
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        #print("ValueError")
        raise e
    except SignatureVerificationError as e:
        #print("SignatureVerificationError")
        raise e
    #print('+++++'+event['type'])
    if event['type'] == 'checkout.session.completed':
        #Payment is successfull
        # print('----------------------------------------------------------------')
        # print("Customer: "+event['data']['object']['customer'])
        # print("subscription: "+event['data']['object']['subscription'])
        #print(event)
        try:
            user = User.objects.get(stripe_customer_id=event['data']['object']['customer'])
        except User.DoesNotExist:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        user.subscription_id = event['data']['object']['subscription']
        user.save()
        # print('----------------------------------------------------------------')
    elif event['type'] == 'invoice.paid':
        # Subscription paid
        # print('----------------------------------------------------------------')
        # print('Invoice paid')
        # print('Customer: '+ event['data']['object']['customer'])
        # print("End epoch: :"+str(event['data']['object']['lines']['data'][0]['period']['end']))
        try:
            user = User.objects.get(stripe_customer_id=event['data']['object']['customer'])
        except User.DoesNotExist:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        user.subscription_due = make_aware(datetime.datetime.fromtimestamp(event['data']['object']['lines']['data'][0]['period']['end']))
        user.save()
        #print(event)
        # print('----------------------------------------------------------------')
    elif event['type'] == 'invoice.payment_failed':
        # Failed to pay, no longer subscribed
        # print('----------------------------------------------------------------')
        # print('Invoice failed - Not subscribed')
        # print(event)
        # print('----------------------------------------------------------------')
        pass
    return Response()

def create_stripe_customer(user):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        customer = stripe.Customer.create(email=user.email)
    except Exception as e:
        return False
    user.stripe_customer_id = customer.id
    user.save()
    return True
