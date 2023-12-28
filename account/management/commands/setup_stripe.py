from django.core.management.base import BaseCommand
from django.conf import settings
import stripe

class Command(BaseCommand):
    def handle(self, *args, **options):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            product = stripe.Product.create(name="Basic Plan")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR("Failed to create product!")
            )
            return
        try:
            price = stripe.Price.create(
                product=product.id,
                unit_amount=settings.MONTHLY_SUBSCRIPTION_FEE,
                currency="usd",
                recurring={"interval": "month"},
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR("Failed to set Price!")
            )
            return
        self.stdout.write(
            self.style.SUCCESS("Product and Price are created successfully.")
        )
        self.stdout.write(
            self.style.NOTICE(f"ProductID: {product.id}\nPriceID: {price.id}\n Write these in settings.py file.")
        )
