import streamlit as st
import sqlite3
import requests
from bs4 import BeautifulSoup

# Establish a connection to SQLite database
conn = sqlite3.connect('stock_alert.db')
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS stock_data
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
             ticker TEXT UNIQUE, 
             exchange TEXT UNIQUE,
             highest_price REAL CHECK (highest_price >= 0),
             lowest_price REAL CHECK (lowest_price >= 0),
             notes TEXT)''')
conn.commit()

# Function to display the table
def display_records():
    st.subheader("Read Records")
    c.execute("SELECT * FROM stock_alert_data")
    result = c.fetchall()
    for row in result:
        st.write(row)

# Function to create a record
def create_record():
    st.subheader("Create a Record")
    ticker = st.text_input("Enter Ticker")
    exchange = st.text_input("Enter exchange")
    notes = st.text_input("Enter your notes")
    highest_price = st.text_input("Enter the resistance price")
    lowest_price = st.text_input("Enter the support price")
    if st.button("Create"):
        try:
            c.execute("INSERT INTO stock_data (ticker, exchange, notes, highest_price, lowest_price) VALUES (?, ?, ?, ?, ?)", (ticker, exchange, notes, highest_price, lowest_price))
            conn.commit()
            st.success("Record Created Successfully!!!")
        except sqlite3.IntegrityError:
            st.error("Ticker or Exchange already exists!")

# Function to update a record
def update_record():
    st.subheader("Update a Record")
    id = st.number_input("Enter ID", min_value=1)
    ticker = st.text_input("Enter Ticker")
    exchange = st.text_input("Enter exchange")
    notes = st.text_input("Enter your notes")
    highest_price = st.text_input("Enter the resistance price")
    lowest_price = st.text_input("Enter the support price")
    if st.button("Update"):
        try:
            c.execute("UPDATE stock_data SET ticker=?, exchange=?, notes=?, highest_price=?, lowest_price=? WHERE id=?", (ticker, exchange, notes, highest_price, lowest_price, id))
            conn.commit()
            st.success("Record Updated Successfully!!!")
        except sqlite3.IntegrityError:
            st.error("Ticker or Exchange already exists!")

# Function to delete a record
def delete_record():
    st.subheader("Delete a Record")
    id = st.number_input("Enter ID", min_value=1)
    if st.button("Delete"):
        c.execute("DELETE FROM stock_data WHERE id=?", (id,))
        conn.commit()
        st.success("Record Deleted Successfully!!!")

# Function to find stock prices
def find_stock_price():
    st.subheader("Check Prices")
    c.execute("SELECT id, ticker, exchange, highest_price, lowest_price FROM stock_data")
    rows = c.fetchall()

    below_lowest_messages = []  # Collect messages for stocks below the lowest price
    above_highest_messages = []  # Collect messages for stocks above the highest price

    for row in rows:
        id, ticker, exchange, highest_price, lowest_price = row
        url = f'https://www.google.com/finance/quote/{ticker}:{exchange}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        class1 = "YMlKec fxKbKc"
        found_element = soup.find(class_=class1)

        if found_element:
            try:
                price = float(found_element.text.strip()[1:].replace(",", ""))
            except ValueError:
                below_lowest_messages.append(f"Invalid price format for {ticker}:{exchange}")
                continue

            # Get current stock price and display it in the alert
            current_price_label = f" ({price})"
            if price > highest_price:
                above_highest_messages.append(f"{ticker}:{exchange} is above the support price {highest_price}! (Current Price:{current_price_label})")

            if price < lowest_price:
                below_lowest_messages.append(f"{ticker}:{exchange} is below the support price {lowest_price}! (Current Price:{current_price_label})")

        else:
            below_lowest_messages.append(f"Could not find stock data for {ticker}:{exchange}")

    # Display messages in separate sections
    if below_lowest_messages:
        st.info("Below Support Price Alerts:")
        st.text("\n".join(below_lowest_messages))

    if above_highest_messages:
        st.info("Above Resistance Price Alerts:")
        st.text("\n".join(above_highest_messages))

# Main function
def main():
    st.title("CRUD Operations With SQLite")

    # Display Options for CRUD Operations
    option = st.sidebar.selectbox("Select an Operation", ("Create", "Update", "Delete", "Find Stock Price"))

    if option == "Create":
        create_record()
    elif option == "Update":
        update_record()
    elif option == "Delete":
        delete_record()
    elif option == "Find Stock Price":
        find_stock_price()

    # Display records at all times
    display_records()

if __name__ == "__main__":
    main()
