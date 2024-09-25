import os
import stripe
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import sys

# Load environment variables from .env file
load_dotenv()

# Get Stripe API key from environment variable
stripe.api_key = os.getenv('STRIPE_API_KEY')

def process_customer(customer):
    try:
        removed_count = 0

        # Remove default source if it's a card
        if customer.default_source:
            source = stripe.Customer.retrieve_source(customer.id, customer.default_source)
            if source.object == 'card':
                stripe.Customer.modify(
                    customer.id,
                    default_source=None
                )
                removed_count += 1

        # Remove all card sources
        sources = stripe.Customer.list_sources(customer.id, object='card', limit=100)
        for source in sources.auto_paging_iter():
            stripe.Customer.delete_source(
                customer.id,
                source.id
            )
            removed_count += 1

        # Remove all card payment methods
        payment_methods = stripe.PaymentMethod.list(
            customer=customer.id,
            type='card',
            limit=100
        )
        for payment_method in payment_methods:
            stripe.PaymentMethod.detach(payment_method.id)
            removed_count += 1

        if removed_count > 0:
            return f"Processed customer {customer.id}: Removed {removed_count} payment method(s)"
        else:
            return f"Customer {customer.id}: No active cards to remove"

    except stripe.error.StripeError as e:
        return f"Error processing customer {customer.id}: {str(e)}"

def remove_payment_info():
    if not stripe.api_key:
        print("Error: Stripe API key not found. Make sure it's set in your .env file.")
        return

    print("Starting to process customers...")
    start_time = time.time()

    # Count total customers
    print("Counting total customers...")
    total_customers = 0
    for customer in stripe.Customer.list(limit=100).auto_paging_iter():
        total_customers += 1
    print(f"Total customers to process: {total_customers}")

    processed_customers = 0
    customers_with_removed_cards = 0
    processing_times = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_customer = {executor.submit(process_customer, customer): customer for customer in stripe.Customer.list(limit=100).auto_paging_iter()}
        for future in as_completed(future_to_customer):
            customer_start_time = time.time()
            result = future.result()
            customer_processing_time = time.time() - customer_start_time
            processing_times.append(customer_processing_time)
            
            processed_customers += 1
            
            if "Removed" in result:
                customers_with_removed_cards += 1

            # Update progress
            progress = (processed_customers / total_customers) * 100
            elapsed_time = time.time() - start_time
            avg_time_per_customer = sum(processing_times) / len(processing_times)
            estimated_remaining_time = avg_time_per_customer * (total_customers - processed_customers)
            
            sys.stdout.write(f"\rProgress: {progress:.2f}% ({processed_customers}/{total_customers}) | "
                             f"Elapsed: {elapsed_time:.2f}s | "
                             f"Est. Remaining: {estimated_remaining_time:.2f}s | "
                             f"Last: {result}")
            sys.stdout.flush()

            # Print full status every 1000 customers
            if processed_customers % 1000 == 0:
                print(f"\nProcessed {processed_customers} out of {total_customers} customers.")
                print(f"Customers with cards removed: {customers_with_removed_cards}")
                print(f"Elapsed time: {elapsed_time:.2f} seconds")
                print(f"Estimated remaining time: {estimated_remaining_time:.2f} seconds")

    end_time = time.time()
    total_time = end_time - start_time
    print(f"\n\nCompleted. Processed {processed_customers} out of {total_customers} customers.")
    print(f"Customers with cards removed: {customers_with_removed_cards}")
    print(f"Total time taken: {total_time:.2f} seconds ({total_time/3600:.2f} hours)")

if __name__ == "__main__":
    confirm = input("This will remove all card payment information from your Stripe customers. Are you sure? (yes/no): ")
    if confirm.lower() == 'yes':
        print("Confirmation received. Starting process...")
        remove_payment_info()
    else:
        print("Operation cancelled.")