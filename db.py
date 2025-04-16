import os
import csv
import sys
import platform
import psycopg2
import base64
from crypto import KeyManage, Crypto


class Database:
    # Initialize the database
    def __init__(self):
        self.system_info = platform.uname()
        self.user_login = os.getlogin()

        key_man = KeyManage()
        if self.system_info[0] == "Linux":
            file_path = "/home/" + self.user_login + "/.member_track/"
        elif self.system_info[0] == "Windows":
            file_path = "C:/Users/" + self.user_login + "/AppData/Local/MembershipTracker/"
        else:
            file_path = ""

        key = key_man.load_key(file_path + "encryption.key")
        crypto = Crypto()


        self.dbname = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = crypto.decrypt_password(os.getenv("DB_PASS"), key)
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")

    
    # Connect to the database
    def connect(self):
        return psycopg2.connect(
            database=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )

    
    # Search for members
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

    
    # Add a new member
    def add_member(
            self, 
            first_name, 
            last_name, 
            phone_number,
            email,
            member_start,
            member_expire,
            store_credit,
            membership_type):
        conn = self.connect()
        cur = conn.cursor()
        sql = """
    WITH new_member AS (
        INSERT INTO members (
            first_name, 
            last_name, 
            phone_number,
            email,
            member_start, 
            member_expire, 
            store_credit,
            membership_type
        ) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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
                email,
                member_start, 
                member_expire, 
                store_credit,
                membership_type,
                store_credit)
        )
        conn.commit()
        conn.close()

    
    # Change member profile info
    def update_member(
            self, 
            member_id,
            first_name, 
            last_name, 
            phone_number,
            email,
            member_start, 
            member_expire,
            membership_type):
        query = """
            UPDATE members
            SET first_name = %s,
                last_name = %s,
                phone_number = %s,
                email = %s,
                member_start = %s,
                member_expire = %s,
                membership_type = %s
            WHERE member_id = %s
        """
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(query, (
            first_name, 
            last_name, 
            phone_number,
            email,
            member_start, 
            member_expire,
            membership_type,
            member_id))
        conn.commit()


    # Delete all data for member, including their transaction history
    def delete_member(self, member_id):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM members WHERE member_id = %s", (member_id,))
        conn.commit()
        conn.close()

    
    # Show member's transaction history
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


    # Change store credit for member
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

    
    # Search for user by username
    def get_user_by_username(self, username):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s;", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user
    

    # Create a new user
    def create_user(self, username, hashed_password, salt, role):
        conn = self.connect()
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO users (username, pass_hash, salt, role)
                VALUES (%s, %s, %s, %s);
            """, (username, hashed_password.decode('utf-8'), salt.decode('utf-8'), role))

            conn.commit()
        except psycopg2.IntegrityError:
            conn.rollback()
            print("Error: Username already exists!")
        finally:
            cur.close()
            conn.close()
    

    # Check if there are users in the table
    def are_users_exist(self):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users;")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return count > 0

    
    # Get the user's role for authorization purposes
    def get_user_role(self, username):
            conn = self.connect()
            cur = conn.cursor()
            cur.execute("SELECT role FROM users WHERE username = %s", (username,))
            role = cur.fetchone()
            cur.close()
            conn.close()
            
            if role:
                return role[0]
            else:
                return None 


    # Search for all members
    def search_all_members(self):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM members;")
        members = cur.fetchall()
        cur.close()
        conn.close()
        return members


    def export_data(self, data_type, filepath):
        conn = self.connect()
        cur = conn.cursor()

        # Export member data to csv file
        if data_type == "members":
            member_path = filepath + '-members.csv'
            
            cur.execute("""SELECT member_id, first_name, last_name,
                                phone_number, email, member_start,
                                member_expire, store_credit,
                                membership_type, 
                                encode(profile_picture, 'base64') 
                           FROM members;""")
            rows = cur.fetchall()
            
            with open(member_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['member_id', 'first_name', 'last_name', 
                    'phone_number', 'email', 'member_start', 
                    'member_expire', 'store_credit', 'membership_type', 
                    'profile_picture'])
                for row in rows:
                    writer.writerow(row)

        # Export transaction data to csv file
        elif data_type == "transactions":
            trans_path = filepath + '-transactions.csv'
            
            with open(trans_path, 'w') as f:
                cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'store_credit_transactions'
                ORDER BY columns.ordinal_position
                """)
                columns = [row[0] for row in cur.fetchall()]
                f.write(','.join(columns) + '\n')
                cur.copy_to(f, 'store_credit_transactions', 
                sep=',', null='NULL')    
        cur.close()
        conn.close()


    def import_data(self, data_type, filepath):
        conn = self.connect()
        cur = conn.cursor()
        
        # Import member data from csv file
        if data_type == "members":
            csv.field_size_limit(sys.maxsize)
            with open(filepath, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    image_data = base64.b64decode(row['profile_picture']) if row['profile_picture'] else None
                    cur.execute("""
                        INSERT INTO members (member_id, first_name,
                        last_name, phone_number, email, member_start,
                        member_expire, store_credit, membership_type,
                        profile_picture)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (row['member_id'], 
                          row['first_name'], 
                          row['last_name'],
                          row['phone_number'],
                          row['email'],
                          row['member_start'],
                          row['member_expire'],
                          row['store_credit'],
                          row['membership_type'],
                          image_data))
            conn.commit()

        # Import transaction data from csv file
        elif data_type == "transactions":
            with open(filepath, 'r') as f:
                sql = f"""COPY store_credit_transactions 
                          FROM STDIN WITH CSV HEADER"""
                cur.copy_expert(sql=sql, file=f)
            conn.commit()
        cur.close()
        conn.close()


    def get_member_photo(self, member_id):
        # Find member photo in database
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("""SELECT profile_picture 
                FROM members WHERE member_id = %s""", 
                (member_id,))
            result = cursor.fetchone()
            conn.close()
            if result and result[0]:
                return result[0] 
            else:
                return None
        except Exception as e:
            print(f"Error fetching photo: {e}")
            return None


    def update_member_photo(self, member_id, photo_data):
        # Update the member's photo in the database
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("""UPDATE members 
                        SET profile_picture = %s WHERE member_id = %s""", 
                        (photo_data, member_id))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating photo: {e}")
            raise e
