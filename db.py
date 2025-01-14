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
        cur.execute(
            """INSERT INTO members (
            first_name, 
            last_name, 
            phone_number, 
            member_start, 
            member_expire, 
            store_credit) 
            VALUES (%s, %s, %s, %s, %s, %s);""",
            (
                first_name, 
                last_name, 
                phone_number, 
                member_start, 
                member_expire, 
                store_credit
                )
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
            member_expire, 
            store_credit):
        query = """
            UPDATE members
            SET first_name = %s,
                last_name = %s,
                phone_number = %s,
                member_start = %s,
                member_expire = %s,
                store_credit = %s
            WHERE id = %s
        """
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(query, (first_name, last_name, phone_number, member_start, member_expire, store_credit, member_id))
        conn.commit()


    def delete_member(self, member_id):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM members WHERE id = %s", (member_id,))
        conn.commit()
        conn.close()
