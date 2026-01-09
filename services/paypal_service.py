"""
PayPal Service - Simple Payment Processing
"""
import os
import requests

class PayPalService:
    # PayPal API endpoints
    SANDBOX_API = "https://api-m.sandbox.paypal.com"
    LIVE_API = "https://api-m.paypal.com"
    
    @staticmethod
    def get_api_url():
        """Get API URL based on environment"""
        is_live = os.getenv('PAYPAL_MODE', 'sandbox') == 'live'
        return PayPalService.LIVE_API if is_live else PayPalService.SANDBOX_API
    
    @staticmethod
    def get_access_token():
        """Get PayPal access token"""
        client_id = os.getenv('PAYPAL_CLIENT_ID')
        client_secret = os.getenv('PAYPAL_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            return None
        
        url = f"{PayPalService.get_api_url()}/v1/oauth2/token"
        headers = {"Accept": "application/json"}
        data = {"grant_type": "client_credentials"}
        
        try:
            response = requests.post(
                url,
                headers=headers,
                data=data,
                auth=(client_id, client_secret)
            )
            return response.json().get('access_token')
        except Exception as e:
            print(f"PayPal Error: {e}")
            return None
    
    @staticmethod
    def create_payment(amount, description, return_url, cancel_url):
        """Create a PayPal payment"""
        access_token = PayPalService.get_access_token()
        if not access_token:
            return None, None
        
        url = f"{PayPalService.get_api_url()}/v2/checkout/orders"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": "USD",
                    "value": str(amount)
                },
                "description": description
            }],
            "application_context": {
                "return_url": return_url,
                "cancel_url": cancel_url
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()
            
            # Get approval URL
            approval_url = None
            for link in data.get('links', []):
                if link.get('rel') == 'approve':
                    approval_url = link.get('href')
                    break
            
            return approval_url, data.get('id')
        except Exception as e:
            print(f"PayPal Error: {e}")
            return None, None
    
    @staticmethod
    def capture_payment(order_id):
        """Capture/complete a PayPal payment"""
        access_token = PayPalService.get_access_token()
        if not access_token:
            return False
        
        url = f"{PayPalService.get_api_url()}/v2/checkout/orders/{order_id}/capture"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        try:
            response = requests.post(url, headers=headers)
            return response.status_code == 201
        except Exception as e:
            print(f"PayPal Error: {e}")
            return False
