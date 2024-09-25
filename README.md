# Stripe Customer Management Scripts

This repository contains two Python scripts for managing Stripe customer data:

1. A script to list all customers (`list_stripe_customers.py`)
2. A script to remove payment information from all customers (`remove_stripe_payment_info.py`)

## Prerequisites

Before you begin, ensure you have met the following requirements:

- You have a Mac / Linux / Windows machine.
- You have installed Python 3.7 or later.
- You have a Stripe account and API key.

## Installing the Scripts

To install the scripts, follow these steps:

1. Clone this repository or download the script files.
2. Open a terminal/command prompt and navigate to the directory containing the scripts.
3. Create a virtual environment:
   ```
   python3 -m venv stripe_env
   ```
4. Activate the virtual environment:
   - On macOS and Linux:
     ```
     source stripe_env/bin/activate
     ```
   - On Windows:
     ```
     stripe_env\Scripts\activate
     ```
5. Install the required packages:
   ```
   pip install stripe python-dotenv
   ```

## Setting up the .env file

1. Create a new file named `.env` in the same directory as the scripts.
2. Add your Stripe API key to the `.env` file:
   ```
   STRIPE_API_KEY=your_stripe_api_key_here
   ```
   Replace `your_stripe_api_key_here` with your actual Stripe API key.

## Using the Scripts

### Listing Customers

To list all customers (recommended as a first step):

1. Ensure your virtual environment is activated.
2. Run the listing script:
   ```
   python list_stripe_customers.py
   ```
3. This will display all customers' IDs and email addresses, allowing you to verify your connection to Stripe and see the customers that will be affected by the removal script.

### Removing Payment Information

After verifying your setup with the listing script, you can proceed to remove payment information:

1. Ensure your virtual environment is activated.
2. Run the removal script:
   ```
   python remove_stripe_payment_info.py
   ```
3. When prompted, type `yes` to confirm that you want to remove all payment information.

## Performance Optimization

The removal script uses parallel processing to improve performance, especially for accounts with many customers. It processes customers in batches of 100 and uses up to 10 worker threads by default.

## Caution

The removal script will remove ALL payment information from ALL customers in your Stripe account. This action cannot be undone. Always test in a Stripe test environment first before running on live data.

## Troubleshooting

If you encounter any issues:

1. Make sure your Stripe API key is correctly set in the `.env` file.
2. Ensure you have activated the virtual environment before running the scripts.
3. Check that you have installed all required packages (`stripe` and `python-dotenv`).
4. If the removal script seems slow, try adjusting the `max_workers` parameter in the `ThreadPoolExecutor` initialization to match your system's capabilities.

## Testing and Verification

It's highly recommended to follow these steps:

1. Run `list_stripe_customers.py` first to verify your connection and see the list of customers.
2. If possible, test the removal script in a Stripe test environment.
3. After running the removal script, use the listing script again to verify that customers still exist (only payment info should be removed).

If problems persist, check the Stripe API documentation or seek assistance from a developer familiar with Python and Stripe.
