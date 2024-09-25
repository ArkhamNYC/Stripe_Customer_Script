import os
import stripe
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Stripe API key from environment variable
stripe.api_key = os.getenv('STRIPE_API_KEY')

def list_customers():
    if not stripe.api_key:
        print("Error: Stripe API key not found. Make sure it's set in your .env file.")
        return

    try:
        # Retrieve all customers
        customers = stripe.Customer.list()

        # Log each customer's ID and email
        total_customers = 0
        for customer in customers.auto_paging_iter():
            print(f"Customer ID: {customer.id}, Email: {customer.email}")
            total_customers += 1

        print(f"\nTotal customers: {total_customers}")

    except stripe.error.StripeError as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    list_customers()