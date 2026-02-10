import sqlite3
import json

def check_db():
    conn = sqlite3.connect('backend/annotation.db')
    cursor = conn.cursor()

    try:
        # 저장된 평가 데이터 조회
        cursor.execute("""
            SELECT 
                u.username, 
                e.title, 
                a.score_language, 
                a.score_organization, 
                a.score_content, 
                a.is_submitted
            FROM annotations a
            JOIN users u ON a.user_id = u.id
            JOIN essays e ON a.essay_id = e.id
        """)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("데이터베이스에 아직 저장된 평가 결과가 없습니다.")
            return

        print(f"{'사용자':<10} | {'에세이 제목':<40} | {'언어':<2} | {'구성':<2} | {'내용':<2} | {'제출됨'}")
        print("-" * 100)
        
        for row in rows:
            username, title, lang, org, cont, submitted = row
            # 제목이 너무 길면 잘라서 표시
            display_title = (title[:37] + '..') if len(title) > 40 else title
            print(f"{username:<10} | {display_title:<40} | {lang:<4} | {org:<4} | {cont:<4} | {submitted}")
            
    except sqlite3.Error as e:
        print(f"오류 발생: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_db()
