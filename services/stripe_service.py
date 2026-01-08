import stripe
import os

# Set Stripe API Key from environment variables
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

class StripeService:
    @staticmethod
    def create_checkout_session(item_name, amount_usd, success_url, cancel_url):
        try:
            # Stripe expects amounts in cents
            amount_cents = int(float(amount_usd) * 100)
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': item_name,
                            },
                            'unit_amount': amount_cents,
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return checkout_session.url, checkout_session.id
        except Exception as e:
            print(f"Stripe Error: {str(e)}")
            return None, None

stripe_service = StripeService()
