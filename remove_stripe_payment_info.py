import os
import stripe
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Load environment variables from .env file
load_dotenv()

# Get Stripe API key from environment variable
stripe.api_key = os.getenv('STRIPE_API_KEY')

def process_customer(customer):
    try:
        # Remove default source
        if customer.default_source:
            stripe.Customer.modify(
                customer.id,
                default_source=None
            )

        # Remove all sources (cards and bank accounts)
        sources = stripe.Customer.list_sources(customer.id, object="card", limit=100)
        for source in sources.auto_paging_iter():
            stripe.Customer.delete_source(
                customer.id,
                source.id
            )

        # Remove all payment methods
        payment_methods = stripe.PaymentMethod.list(
            customer=customer.id,
            type="card",
            limit=100
        )
        for payment_method in payment_methods:
            stripe.PaymentMethod.detach(payment_method.id)

        return f"Processed payment information for customer: {customer.id} ({customer.email})"
    except stripe.error.StripeError as e:
        return f"Error processing customer {customer.id}: {str(e)}"

def remove_payment_info():
    if not stripe.api_key:
        print("Error: Stripe API key not found. Make sure it's set in your .env file.")
        return

    start_time = time.time()
    customers = stripe.Customer.list(limit=100)
    total_customers = 0
    processed_customers = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_customer = {executor.submit(process_customer, customer): customer for customer in customers.auto_paging_iter()}
        for future in as_completed(future_to_customer):
            result = future.result()
            print(result)
            total_customers += 1
            if "Error" not in result:
                processed_customers += 1

    end_time = time.time()
    print(f"\nProcessed {processed_customers} out of {total_customers} customers.")
    print(f"Total time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    confirm = input("This will remove all payment information from your Stripe customers. Are you sure? (yes/no): ")
    if confirm.lower() == 'yes':
        remove_payment_info()
    else:
        print("Operation cancelled.")