import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

    # Create 'customer_name' column
    df['customer_name'] = df['first_name'] + ' ' + df['last_name']
    return df

def fetch_order_data(conn):
    query = 'SELECT * FROM public."Orders"'
    return pd.read_sql(query, conn)

def main():
    # Connect to the database
    conn = psycopg2.connect(**DB_PARAMS)

    # Fetch data
    customer_data = fetch_customer_data(conn)
    order_data = fetch_order_data(conn)

    # Print fetched data for understanding
    print("Customer Data:", customer_data.head())
    print("Order Data:", order_data.head())

    # Data Preprocessing
    customer_data['total_spent'] = customer_data['total_spent'].astype(float)
    customer_data['orders_count'] = customer_data['orders_count'].astype(int)

    # Ensure datetime columns are parsed correctly
    order_data['created_at'] = pd.to_datetime(order_data['created_at'])

    # Step 1: High Spenders
    high_spenders = customer_data.sort_values(by='total_spent', ascending=False).head(10)
    print("High Spenders:", high_spenders)

    # Step 2: Frequent Shoppers
    frequent_shoppers = customer_data.sort_values(by='orders_count', ascending=False).head(10)
    print("Frequent Shoppers:", frequent_shoppers)

    # Step 3: Best Selling Products
    # Inspect the structure of the items column
    print("Items column structure:", order_data['items'].head())

    # Extracting product names assuming items is a list of dictionaries
    def extract_product_names(items):
        if isinstance(items, list):
            return [item.get('name', '') for item in items if isinstance(item, dict) and 'COD-Fees' not in item.get('name', '')]
        return []

    order_data['items'] = order_data['items'].apply(extract_product_names)

    # Explode 'items' column and group by 'name' to find best-selling products
    order_data_exploded = order_data.explode('items')
    print("Exploded Order Data:", order_data_exploded.head())

    best_selling_products = order_data_exploded['items'].value_counts().head(5).reset_index()
    best_selling_products.columns = ['name', 'quantity_sold']
    print("Best Selling Products:", best_selling_products)

    while True:
        user_input = input("Enter 1 to view High Spenders, 2 to view Frequent Shoppers, 3 to view Best Selling Products, or N to exit: ").strip().upper()
        if user_input == '1':
            visualize_high_spenders(high_spenders)
        elif user_input == '2':
            visualize_frequent_shoppers(frequent_shoppers)
        elif user_input == '3':
            visualize_best_selling_products(best_selling_products)
        elif user_input == 'N':
            break
        else:
            print("Invalid input. Please enter 1, 2, 3, or N.")

    # Close the connection
    conn.close()

def visualize_high_spenders(high_spenders):
    print("\nData points for High Spenders:")
    print(high_spenders[['customer_name', 'total_spent']])
    
    plt.figure(figsize=(8, 6))
    sns.barplot(x='customer_name', y='total_spent', data=high_spenders, palette='viridis')
    plt.title('Top 10 High Spenders')
    plt.xlabel('Customer Name')
    plt.ylabel('Total Spent')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def visualize_frequent_shoppers(frequent_shoppers):
    print("\nData points for Frequent Shoppers:")
    print(frequent_shoppers[['customer_name', 'orders_count']])
    
    plt.figure(figsize=(8, 6))
    sns.barplot(x='customer_name', y='orders_count', data=frequent_shoppers, palette='viridis')
    plt.title('Top 10 Frequent Shoppers')
    plt.xlabel('Customer Name')
    plt.ylabel('Orders Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def visualize_best_selling_products(best_selling_products):
    print("\nData points for Best Selling Products:")
    print(best_selling_products[['name', 'quantity_sold']])
    
    plt.figure(figsize=(8, 6))
    sns.barplot(x='name', y='quantity_sold', data=best_selling_products, palette='viridis')
    plt.title('Top 5 Best Selling Products')
    plt.xlabel('Product Name')
    plt.ylabel('Quantity Sold')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
