
import sqlite3
import json

def dump_recent_job():
    conn = sqlite3.connect('web/prisma/dev.db')
    cursor = conn.cursor()
    
    # Get latest job
    cursor.execute("SELECT id, status, logs, contentItemId FROM AgentJob ORDER BY createdAt DESC LIMIT 1")
    job = cursor.fetchone()
    
    if job:
        print(f"Job ID: {job[0]}")
        print(f"Status: {job[1]}")
        print(f"Content ID: {job[3]}")
        print("-" * 20)
        # Content item info
        cursor.execute("SELECT title, topic FROM ContentItem WHERE id = ?", (job[3],))
        item = cursor.fetchone()
        if item:
            print(f"Item Title: {item[0]}")
            print(f"Item Topic: {item[1]}")
        
        print("-" * 20)
        print("LOGS:")
        print(job[2][-10000:] if job[2] and len(job[2]) > 10000 else job[2])
    else:
        print("No jobs found.")
    
    conn.close()

if __name__ == "__main__":
    dump_recent_job()
