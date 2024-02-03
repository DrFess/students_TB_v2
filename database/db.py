import sqlite3
import os
from settings import PATH_TO_DB


def connection_to_DB(func):
    """Декоратор - подключение к базе данных"""
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect(os.path.abspath(PATH_TO_DB), detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
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
def delete_group(cursor, id: int):
    """Удаление группы"""
    cursor.execute(
        """DELETE FROM student_group WHERE id=?;""", (id,)
    )


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
def show_student_group_title(cursor, id: int):
    """Получить данные группы по id"""
    group_object = cursor.execute("""SELECT title, sub_group FROM student_group WHERE id=?;""", (id,)).fetchone()
    title = f'{group_object[0]} {group_object[1]}'
    return title


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
def show_group_students(cursor, group_id: int):
    """Возвращает список telegram_id студентов группы"""
    students = cursor.execute('SELECT telegram_id FROM student WHERE group_id=?;', (group_id,)).fetchall()
    students_list = []
    for student in students:
        students_list.append(student[0])
    return students_list


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
def show_all_teachers(cursor) -> dict:
    """Показать всех учителей"""
    teachers = cursor.execute('SELECT * FROM teacher;').fetchall()
    teachers_dict = {}
    for item in teachers:
        teachers_dict[item[0]] = f'{item[1]}, {item[2]}, {item[3]}, {item[4]}'
    return teachers_dict


@connection_to_DB
def show_teacher_id(cursor, telegram_id):
    """Получение фамилии преподавателя по telegram_id"""
    teacher = cursor.execute('SELECT id FROM teacher WHERE telegram_id=?;', (telegram_id,)).fetchone()[0]
    return teacher


@connection_to_DB
def add_theme(cursor, title: str):
    """Добавление темы"""
    cursor.execute("INSERT INTO theme (title) VALUES (?)", (title,))


@connection_to_DB
def show_all_themes(cursor):
    """Показать все темы"""
    themes_dict = {}
    themes = cursor.execute("""SELECT * FROM theme""").fetchall()
    for theme in themes:
        themes_dict[f'{theme[1]}'] = theme[0]
    return themes_dict


@connection_to_DB
def show_theme_title(cursor, id: int):
    """Показать тему по id"""
    theme = cursor.execute("""SELECT * FROM theme WHERE id=?;""", (id,)).fetchone()[0]
    return theme


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


@connection_to_DB
def add_lesson(cursor, date, theme_id, who_was, who_taught_lesson):
    data = (date, theme_id, who_was, who_taught_lesson)
    cursor.execute(
        """INSERT INTO lesson (
        date, 
        theme_id, 
        who_was, 
        who_taught_lesson
        ) VALUES (?, ?, ?, ?)""", data)

