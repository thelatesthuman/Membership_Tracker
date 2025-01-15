import psycopg2


class Database:
    def __init__(self, dbname, user, password, host='localhost', port='5432'):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port


    def connect(self):
        return psycopg2.connect(
            database=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )


    def search_members(self, first_name, last_name, phone_number):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""SELECT * FROM members 
                WHERE first_name = %s 
                OR last_name = %s 
                OR phone_number = %s;""", (first_name, last_name, phone_number))
        data = cur.fetchall()
        conn.close()
        return data


    def add_member(
            self, 
            first_name, 
            last_name, 
            phone_number, 
            member_start,
            member_expire,
            store_credit):
        conn = self.connect()
        cur = conn.cursor()
        sql = """
    WITH new_member AS (
        INSERT INTO members (
            first_name, 
            last_name, 
            phone_number, 
            member_start, 
            member_expire, 
            store_credit
        ) 
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING member_id
    )
    INSERT INTO store_credit_transactions (member_id, amount, description)
    SELECT member_id, %s, 'Membership start'
    FROM new_member;
    """
        cur.execute(sql,
            (
                first_name, 
                last_name, 
                phone_number, 
                member_start, 
                member_expire, 
                store_credit,
                store_credit)
        )
        conn.commit()
        conn.close()


    def update_member(
            self, 
            member_id,
            first_name, 
            last_name, 
            phone_number, 
            member_start, 
            member_expire):
        query = """
            UPDATE members
            SET first_name = %s,
                last_name = %s,
                phone_number = %s,
                member_start = %s,
                member_expire = %s
            WHERE member_id = %s
        """
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(query, (
            first_name, 
            last_name, 
            phone_number, 
            member_start, 
            member_expire,  
            member_id))
        conn.commit()


    def delete_member(self, member_id):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM members WHERE member_id = %s", (member_id,))
        conn.commit()
        conn.close()


    def show_store_credit_transactions(self, member_id):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""SELECT * FROM store_credit_transactions 
                WHERE member_id = %s
                ORDER BY transaction_date DESC;""", 
                (member_id,))
        transactions = cur.fetchall()
        conn.close()

        return transactions


    def update_store_credit_transactions(self, member_id, amount, description):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""UPDATE members 
        SET store_credit = store_credit + %s 
        WHERE member_id = %s;""", (amount,  member_id))
        cur.execute("""INSERT INTO store_credit_transactions (member_id, amount, description)
        VALUES (%s, %s, %s);""", (member_id, amount, description))
        conn.commit()
        conn.close()
