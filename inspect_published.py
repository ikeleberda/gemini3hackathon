def list_all_content():
    conn = sqlite3.connect('web/dev.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, title, topic, status FROM ContentItem ORDER BY createdAt DESC")
    items = cursor.fetchall()
    
    print("Items in DB:")
    for item in items:
        print(f"ID: {item[0]}, Title: {item[1]}, Topic: {item[2]}, Status: {item[3]}")
    
    conn.close()

if __name__ == "__main__":
    list_all_content()
