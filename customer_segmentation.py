import psycopg2
import pandas as pd
import json

# Database connection parameters
DB_PARAMS = {
    'dbname': 'shopify-reporting-app',
    'user': 'postgres',
    'password': 'Sairam_12345',
    'host': 'localhost',
    'port': '5432'
}

def fetch_customer_data(conn):
    query = 'SELECT * FROM public."Customer" WHERE is_deleted = FALSE'
    df = pd.read_sql(query, conn)
    df['customer_name'] = df['first_name'] + ' ' + df['last_name']
    return df

def fetch_order_data(conn):
    query = 'SELECT * FROM public."Orders"'
    return pd.read_sql(query, conn)

def update_high_spenders(conn, high_spenders):
    with conn.cursor() as cursor:
        for record in high_spenders:
            cursor.execute(
                '''
                INSERT INTO public."HighSpenders" (customer_id, customer_name, total_spent)
                VALUES (%s, %s, %s)
                ON CONFLICT (customer_id) 
                DO UPDATE SET total_spent = EXCLUDED.total_spent
                ''',
                [record['id'], record['customer_name'], record['total_spent']]
            )
    conn.commit()

def update_frequent_shoppers(conn, frequent_shoppers):
    with conn.cursor() as cursor:
        for record in frequent_shoppers:
            cursor.execute(
                '''
                INSERT INTO public."FrequentShoppers" (customer_id, customer_name, orders_count)
                VALUES (%s, %s, %s)
                ON CONFLICT (customer_id) 
                DO UPDATE SET orders_count = EXCLUDED.orders_count
                ''',
                [record['id'], record['customer_name'], record['orders_count']]
            )
    conn.commit()

def update_best_selling_products(conn, best_selling_products):
    with conn.cursor() as cursor:
        for record in best_selling_products:
            cursor.execute(
                '''
                INSERT INTO public."BestSellingProducts" (name, quantity_sold)
                VALUES (%s, %s)
                ON CONFLICT (name) 
                DO UPDATE SET quantity_sold = EXCLUDED.quantity_sold
                ''',
                [record['name'], record['quantity_sold']]
            )
    conn.commit()

def main():
    # Connect to the database
    conn = psycopg2.connect(**DB_PARAMS)

    # Fetch data
    customer_data = fetch_customer_data(conn)
    order_data = fetch_order_data(conn)

    # Data Preprocessing
    customer_data['total_spent'] = customer_data['total_spent'].astype(float)
    customer_data['orders_count'] = customer_data['orders_count'].astype(int)
    order_data['created_at'] = pd.to_datetime(order_data['created_at'])

    # High Spenders
    high_spenders = customer_data.sort_values(by='total_spent', ascending=False).head(10)

    # Frequent Shoppers
    frequent_shoppers = customer_data.sort_values(by='orders_count', ascending=False).head(10)

    # Best Selling Products
    def extract_product_names(items):
        if isinstance(items, list):
            return [item.get('name', '') for item in items if isinstance(item, dict) and 'COD-Fees' not in item.get('name', '')]
        return []

    order_data['items'] = order_data['items'].apply(extract_product_names)
    order_data_exploded = order_data.explode('items')
    best_selling_products = order_data_exploded['items'].value_counts().head(5).reset_index()
    best_selling_products.columns = ['name', 'quantity_sold']

    # Prepare the results
    results_customer = {
        'high_spenders': high_spenders.to_dict(orient='records'),
        'frequent_shoppers': frequent_shoppers.to_dict(orient='records')
    }
    results_order = {
        'best_selling_products': best_selling_products.to_dict(orient='records')
    }

    # Update the database
    update_high_spenders(conn, results_customer['high_spenders'])
    update_frequent_shoppers(conn, results_customer['frequent_shoppers'])
    update_best_selling_products(conn, results_order['best_selling_products'])

    # Close the connection
    conn.close()

if __name__ == '__main__':
    main()
