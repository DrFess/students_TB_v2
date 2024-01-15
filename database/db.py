import sqlite3


def connection_to_DB(func):
    """Декоратор - подключение к базе данных"""
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('database/studentsDB.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        result = func(cursor, *args, **kwargs)

        conn.commit()
        cursor.close()
        conn.close()

        return result
    return wrapper


@connection_to_DB
def create_tables(cursor):
    """Создание таблиц базы данных"""
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS student(
                                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                            telegram_id INTEGER,
                                            surname TEXT,
                                            name TEXT,
                                            patronymic TEXT,
                                            group_id INTEGER,
                                            FOREIGN KEY (group_id) REFERENCES student_group(id) ON DELETE CASCADE
        )""",
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS student_group(
                                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                            title TEXT,
                                            sub_group TEXT
        )""",
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS question(
                                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                            content TEXT,
                                            first_answer TEXT,
                                            second_answer TEXT,
                                            third_answer TEXT,
                                            fourth_answer TEXT,
                                            right_answer TEXT,
                                            theme_id INTEGER,
                                            FOREIGN KEY (theme_id) REFERENCES theme(id) ON DELETE CASCADE
        )""",
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS theme(
                                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                            title TEXT
        )""",
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS student_answers(
                                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                            student_id INTEGER,
                                            lesson_id INTEGER,
                                            answers TEXT,
                                            FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE
        )""",
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS teacher(
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            telegram_id INTEGER,
                                            surname TEXT,
                                            name TEXT,
                                            patronymic TEXT
        )""",
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS lesson(
                                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                            date timestamp,
                                            theme_id INTEGER,
                                            who_was TEXT,
                                            who_taught_lesson INTEGER,
                                            FOREIGN KEY (theme_id) REFERENCES theme(id) ON DELETE CASCADE,
                                            FOREIGN KEY (who_taught_lesson) REFERENCES teacher(id) ON DELETE CASCADE
        )""",
    )


@connection_to_DB
def add_student_group(cursor, title: str, sub_group: str):
    """Добавление группы с подгруппой"""
    data = (title, sub_group)
    cursor.execute("""INSERT INTO student_group(title, sub_group) VALUES (?, ?)""", data)


@connection_to_DB
def show_all_student_group(cursor):
    """Получить данные всех групп"""
    groups_dict = {}
    groups = cursor.execute("""SELECT * FROM student_group""").fetchall()
    for item in groups:
        groups_dict[f'{item[1]} {item[2]}'] = item[0]
    return groups_dict


@connection_to_DB
def show_student_group(cursor, group_title: str, sub_group: str):
    """Получить данные группы по title"""
    group_id = cursor.execute("""SELECT id FROM student_group WHERE title=? AND sub_group=?;""", (group_title, sub_group)).fetchone()[0]
    return group_id


@connection_to_DB
def add_student(cursor, telegram_id: int, surname: str, name: str, patronymic: str, group_id: str):
    """Добавление студента"""
    data = (telegram_id, surname, name, patronymic, group_id)
    cursor.execute(
        """INSERT INTO student(
        telegram_id,
        surname,
        name,
        patronymic,
        group_id
        ) VALUES (?, ?, ?, ?, ?)""", data)


@connection_to_DB
def check_student(cursor, telegram_id: int):
    """Проверка наличия студента в базе данных"""
    if cursor.execute('SELECT * FROM student WHERE telegram_id=?;', (telegram_id,)).fetchone():
        return True
    return False


@connection_to_DB
def add_teacher(cursor, telegram_id: int, surname: str, name: str, patronymic: str):
    """Добавление преподавателя"""
    data = (telegram_id, surname, name, patronymic)
    cursor.execute(
        """INSERT INTO teacher (
        telegram_id,
        surname,
        name,
        patronymic
        ) VALUES (?, ?, ?, ?)""", data)


@connection_to_DB
def check_teacher(cursor, telegram_id: int):
    """Проверка наличия преподавателя в базе данных"""
    if cursor.execute('SELECT * FROM teacher WHERE telegram_id=?;', (telegram_id,)).fetchone():
        return True
    return False


@connection_to_DB
def add_theme(cursor, title: str):
    """Добавление темы"""
    cursor.execute("INSERT INTO theme (title) VALUES (?)", (title,))


@connection_to_DB
def add_question(cursor, content: str, first_answer: str, second_answer: str,
                 third_answer: str, fourth_answer: str, right_answer: str, theme_id: int):
    """Добавление вопроса"""
    data = (content, first_answer, second_answer, third_answer, fourth_answer, right_answer, theme_id)
    cursor.execute(
        """INSERT INTO question (
        content,
        first_answer,
        second_answer,
        third_answer,
        fourth_answer,
        right_answer,
        theme_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?)""", data)


# create_tables()
# add_student_group('22-1', 'A')
# add_student_group('22-1', 'Б')
# add_student_group('22-2', 'A')
# add_student_group('22-2', 'Б')
# add_student_group('22-3', 'A')
# add_student_group('22-3', 'Б')
# add_student_group('21-5', 'A')
# add_student_group('21-5', 'Б')
# add_student_group('21-7', 'A')
# add_student_group('21-7', 'Б')
# add_student_group('22-7', 'A')
# add_student_group('22-7', 'Б')
