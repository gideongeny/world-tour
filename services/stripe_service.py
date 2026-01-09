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

    # Premium Membership Methods
    @staticmethod
    def create_customer(email, name):
        """Create a Stripe customer for subscriptions"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={'source': 'worldtour'}
            )
            return customer.id
        except Exception as e:
            print(f"Stripe Error: {str(e)}")
            return None
    
    @staticmethod
    def create_subscription_checkout(customer_id, plan='monthly'):
        """Create checkout session for subscription"""
        try:
            # Get price ID from environment
            price_id = os.environ.get(
                'STRIPE_MONTHLY_PRICE_ID' if plan == 'monthly' else 'STRIPE_YEARLY_PRICE_ID'
            )
            
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{'price': price_id, 'quantity': 1}],
                mode='subscription',
                success_url='http://localhost:5173/subscription/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='http://localhost:5173/pricing',
            )
            return session.url, session.id
        except Exception as e:
            print(f"Stripe Error: {str(e)}")
            return None, None
    
    @staticmethod
    def cancel_subscription(subscription_id):
        """Cancel subscription at period end"""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            return True
        except Exception as e:
            print(f"Stripe Error: {str(e)}")
            return False
