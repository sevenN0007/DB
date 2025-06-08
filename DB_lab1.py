import psycopg2
import threading
import time

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="user_counter", 
        user="postgres",          
        password="0007" 
    )


# Функція для обнулення каунтера
def reset_counter():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_counter SET counter = 0, version = 0 WHERE user_id = 1")
    conn.commit()
    cursor.close()
    conn.close()

# Lost-update метод
def lost_update():
    conn = get_connection()
    cursor = conn.cursor()
    for i in range(10000):
        cursor.execute("SELECT counter FROM user_counter WHERE user_id = 1")
        counter = cursor.fetchone()[0]
        counter += 1
        cursor.execute("UPDATE user_counter SET counter = %s WHERE user_id = %s", (counter, 1))
        conn.commit()
    cursor.close()
    conn.close()

# In-place update метод
def inplace_update():
    conn = get_connection()
    cursor = conn.cursor()
    for i in range(10000):
        cursor.execute("UPDATE user_counter SET counter = counter + 1 WHERE user_id = 1")
        conn.commit()
    cursor.close()
    conn.close()

# Row-level locking метод
def row_level_locking_update():
    conn = get_connection()
    cursor = conn.cursor()
    for i in range(10000):
        cursor.execute("BEGIN;")  
        cursor.execute("SELECT counter FROM user_counter WHERE user_id = 1 FOR UPDATE")
        counter = cursor.fetchone()[0]
        counter += 1
        cursor.execute("UPDATE user_counter SET counter = %s WHERE user_id = %s", (counter, 1))
        conn.commit() 
    cursor.close()
    conn.close()

# Optimistic concurrency control метод
def optimistic_concurrency_update():
    conn = get_connection()
    cursor = conn.cursor()
    for i in range(10000):
        while True:
            cursor.execute("SELECT counter, version FROM user_counter WHERE user_id = 1")
            row = cursor.fetchone()
            counter, version = row[0], row[1]
            counter += 1
            # Спробуємо оновити лише якщо версія не змінилась
            cursor.execute("""
                UPDATE user_counter 
                SET counter = %s, version = %s 
                WHERE user_id = %s AND version = %s
            """, (counter, version + 1, 1, version))
            conn.commit()
            if cursor.rowcount > 0:
                break  # успішно оновили — виходимо з циклу
    cursor.close()
    conn.close()

# Загальна функція запуску тесту
def run_test(update_function, description):
    print(f"\nЗапускаємо тест: {description}")

    # Обнуляємо каунтер перед кожним тестом
    reset_counter()

    start_time = time.time()

    threads = []
    for i in range(10):  
        t = threading.Thread(target=update_function)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    end_time = time.time()

    print("Завершено за", end_time - start_time, "секунд")

    # Перевір фінальне значення каунтера
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT counter FROM user_counter WHERE user_id = 1")
    final_counter = cursor.fetchone()[0]
    print("Фінальне значення каунтера:", final_counter)
    cursor.close()
    conn.close()


if __name__ == "__main__":
    run_test(lost_update, "Lost-update")
    run_test(inplace_update, "In-place update")
    run_test(row_level_locking_update, "Row-level locking")
    run_test(optimistic_concurrency_update, "Optimistic concurrency control")