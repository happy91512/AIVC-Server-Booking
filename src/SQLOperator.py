import sqlite3
import json
import io
import numpy as np


class SQLOperator():
    """
    init a DB connection and R/W it.
    """
    
    DELETE: int = 0
    ADD: int = 1

    def __init__(self, db_name: str) -> None:
        self.con = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)
        self.cur = self.con.cursor()
        self.__check_and_build_table()

    def __check_and_build_table(self) -> None:
        command_dict = {
            "schedules": """
            CREATE TABLE schedules (
                schedule_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                cpus FLOAT,
                memory INTEGER,
                gpus INTEGER,
                fordward_port INTEGER,
                image_id INTEGER,
                extra_command TEXT
            );
            """,
            "using_schedule": """
            CREATE TABLE using_schedule (
                schedule_id INTEGER,
                modify_cpus FLOAT,
                modify_memory INTEGER,
                gpu_ls ARRAY,
                FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id)
            );
            """,
            "image": """
            CREATE TABLE image (
                id INTEGER PRIMARY KEY,
                title TEXT
            );
            """,
        }
        for table_name, command in command_dict.items():
            self.__exec_sql(
                command=f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
            )
            if self.cur.fetchone() is None:
                self.__exec_sql(command=command)

        self.__update_db()

    def add_delete_table(
        self, mode: int, table_name: str, data_ls: list = None, condition: str = None):
        extra_ele = None
        if mode == self.DELETE and condition != None:
            command = f"DELETE FROM {table_name} WHERE {condition}"
        elif mode == self.ADD and data_ls != None:
            if table_name == 'using_schedule':
                json_array = json.dumps(data_ls[-1])
                extra_ele = (*data_ls[:-1], json_array)
                command = f"INSERT INTO {table_name} VALUES (?, ?, ?, ?)"

            else:
                command = f"INSERT INTO {table_name} VALUES ({str(data_ls)[1:-1]})"
        else:
            print(f"Modify Error in {table_name}")    
            return
        try:
            self.__exec_sql(command, extra_ele)
            self.__update_db()
        except Exception as e: 
            print(e)

    def update_using(self):
        pass

    def get_interval_info(self):
        pass

    def move2used(self):
        pass

    def update_schedule():
        pass

    def __list2json(ls: list):
        return json.dumps(ls)

    def __exec_sql(self, command, extra_ele = None):
        if extra_ele != None: 
            self.cur.execute(command, extra_ele)
        else:
            self.cur.execute(command)
        return 

    def __update_db(self):
        self.con.commit()

    def show(self, table_name):
        command = f"SELECT * FROM {table_name}"
        self.cur.execute(command)
        rows = self.cur.fetchall()
        if rows:
            for row in rows:
                print(row)



if __name__ == "__main__":
    a = SQLOperator("test.db")

    # a.add_delete_table(SQLOperator.DELETE, 'schedules', condition='userid = \'b10930010\'')
    a.add_delete_table(SQLOperator.ADD, 'schedules', [1, 'b10930010', '0510_1429', '0511_1429', 8.0, 32, 2, 10020, 0, 'None'])
    a.add_delete_table(SQLOperator.ADD, 'schedules', [2, 'b10930010', '0512_1429', '0513_1429', 8.0, 32, 2, 10020, 0, 'None'])
    a.add_delete_table(SQLOperator.ADD, 'schedules', [3, 'b10930010', '0514_1429', '0515_1429', 8.0, 32, 2, 10020, 0, 'None'])
    # a.add_delete_table(SQLOperator.ADD, 'using_schedule', [2, 8, 16, [0, 1, 2, 3]])  
    # a.show("image")
