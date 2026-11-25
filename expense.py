from database import connect_db

def add_expense():
    amount=float(input("Enter amount :"))
    category=input("Enter category :")
    description=input("Enter description :")
    date=input("Enter date (YYYY-MM-DD): ")

    conn=connect_db()
    cursor=conn.cursor()

    cursor.execute(""" 
            INSERT INTO transactions
            (transaction_type, amount, category, description, date)
            VALUES(?, ?, ?, ?, ?)
            """,("Expense",amount, category, description, date))

    conn.commit()
    conn.close()

    print("expense is added successfully!")


def view_transactions():
    conn=connect_db()
    cursor=conn.cursor()

    cursor.execute(""" 
                SELECT * FROM transactions
                """)

    records=cursor.fetchall()

    if not records:
        print("No transactions found!")

    else:
        print("\n -------- All Transactions --------")

        for row in records:
            print(row)
    conn.close()


def filter_by_category():

    category=input("Enter category to search: ")
    conn=connect_db()
    cursor=conn.cursor()

    cursor.execute(""" 
                SELECT * FROM transactions
                WHERE category=?
            """,(category,))

    records=cursor.fetchall()

    if not records:
        print("No transactions found in this category!")

    else:
        print("\n--------- FILTERED TRANSACTIONS ---------")

        for row in records:
            print(row)

    conn.close()




def update_expense():


    expense_id=int(input("Enter transaction id: "))
    new_amount=float(input("Enter updated amount: "))

    conn=connect_db()
    cursor=conn.cursor()

    cursor.execute("""
            UPDATE transactions 
            SET amount = ?
            WHERE id = ? AND transaction_type = 'Expense'
             """,(new_amount, expense_id))

    conn.commit()


    if cursor.rowcount > 0:
        print("Expense updated successfully!")

    else:
        print("Expense ID not found!")

    conn.close()


def delete_expense():
    expense_id=int(input("Enter transaction ID to delete: "))

    conn=connect_db()
    cursor=conn.execute(""" 
        DELETE FROM transactions 
        WHERE id = ? AND transaction_type='Expense'
    """,(expense_id,))

    conn.commit()

    if cursor.rowcount > 0:
        print("Expense deleted successfully!")

    else:
        print("Expense ID not found!")

    conn.close()

def total_expense():
    conn=connect_db()
    cursor=conn.cursor()

    cursor.execute(""" 
        SELECT SUM(amount) FROM transactions
        WHERE transaction_type = 'Expense'
        """)

    result=cursor.fetchone()

    total=result[0] or 0

    print("Total Expense: ",total)

    conn.close()


def monthly_expense_report():
    conn=connect_db()
    cursor=conn.cursor()

    cursor.execute("""
            SELECT 
                strftime('%Y-%m' , date) AS month,
                SUM(amount) AS total_expense
            FROM transactions
            WHERE transaction_type='Expense'
            GROUP BY strftime('%Y-%m' , date)
            ORDER BY month ASC
        """)
    
    records=cursor.fetchall()

    if not records:
        print("No expense records found!")
    else:
        print("\n--- MONTHLY EXPENSE REPORT ---")

        for row in records:
            print("Month: ",row[0],"| Total: ",row[1])

    conn.close()



def add_income():
    amount = float(input("Enter income amount: "))
    category = input("Enter income source: ")
    description = input("Enter description: ")
    date = input("Enter date (YYYY-MM-DD): ")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions
        (transaction_type, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?)
    """, ("Income", amount, category, description, date))

    conn.commit()
    conn.close()

    print("Income added successfully!")

def total_income():
    conn=connect_db()
    cursor=conn.cursor()

    cursor.execute("""
        SELECT SUM(amount) AS total
        FROM transactions
        WHERE transaction_type='Income'
        """)

    result=cursor.fetchone()

    total=result[0] or 0


    print("Total Income: ",total)

    conn.close()

def income_expense_summary():
    conn=connect_db()
    cursor=conn.cursor()

    cursor.execute("""
            SELECT 

            COALESCE (SUM(CASE
                WHEN transaction_type = 'Income'
                THEN amount ELSE 0
            END), 0),

            COALESCE (SUM(CASE
                WHEN transaction_type = 'Expense'
                THEN amount ELSE 0
            END), 0)

            FROM transactions

            """)

    result=cursor.fetchone()

    total_income=result[0]
    total_expense=result[1]

    savings=total_income-total_expense

    print("\n----- Financial Summary -------")
    print("Total Income: ",total_income)    
    print("Total Expense: ",total_expense)    
    print("Remainning Savings: ",savings)    


    conn.close()


def monthly_income_expense():
    conn=connect_db()
    cursor=conn.cursor()

    cursor.execute("""
            SELECT 

            strftime('%Y-%m',date) AS month,

            SUM(CASE
                WHEN transaction_type = 'Income'
                THEN amount ELSE 0
            END) AS total_income,

            SUM(CASE
                WHEN transaction_type = 'Expense'
                THEN amount ELSE 0
                END) AS total_expense
            
            FROM transactions
            GROUP BY month
            ORDER BY month ;

            """)

    results=cursor.fetchall()
    print("\n--- Monthly Income vs Expense ---")

    for row in results:
        month=row[0]
        income=row[1]
        expense=row[2]
        savings=income-expense

        print(f"\nMonth: {month}")
        print(f"Income: ₹{income}")
        print(f"Expense: ₹{expense}")
        print(f"Savings: ₹{savings}")
       

    conn.close()