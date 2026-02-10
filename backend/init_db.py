import json
import os
from models import Base, engine, SessionLocal, User, Essay
from auth import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

def load_essays_from_json():
    json_path = os.path.join(os.path.dirname(__file__), '..', 'paperclinic_generated_dataset_gemini_2.json')
    if not os.path.exists(json_path):
        print(f"Error: JSON file not found at {json_path}")
        return []

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_data = data.get('data', [])
    selected_essays = []
    used_filenames = set()

    # Target scores: (Content, Organization, Language)
    targets = [
        {"scores": (5.0, 5.0, 5.0), "label": "모범답안", "domain": "None", "idx": 0},
        {"scores": (5.0, 5.0, 2.0), "label": "언어2점", "domain": "Language", "idx": 1},
        {"scores": (5.0, 2.0, 5.0), "label": "구성2점", "domain": "Organization", "idx": 2},
        {"scores": (2.0, 5.0, 5.0), "label": "내용2점", "domain": "Content", "idx": 3},
    ]

    for target in targets:
        target_scores = target["scores"]
        for entry in all_data:
            out = entry.get('output', {})
            entry_scores = (out.get('내용'), out.get('구성'), out.get('언어'))
            filename = entry.get('filename', 'unknown')

            if entry_scores == target_scores and filename not in used_filenames:
                # 제목 형식: [논문제목]_[문제번호]_[노이즈영역]_[번호]
                # 예: 2012.09015v2.pdf_Q1_Language_1
                paper_title = filename
                question_num = f"Q{target['idx'] + 1}"
                noise_domain = target['domain']
                serial_num = 1
                
                formatted_title = f"{paper_title}_{question_num}_{noise_domain}_{serial_num}"
                
                selected_essays.append({
                    "title": formatted_title,
                    "question": entry.get('question'),
                    "content": entry.get('input'),
                    "evidence": json.dumps(entry.get('evidence_list', []), ensure_ascii=False)
                })
                used_filenames.add(filename)
                break
    
    return selected_essays

# Initialize database
db = SessionLocal()

# Create test users (4 annotators)
test_users = [
    {"username": "annotator1", "password": "password123", "full_name": "김철수 교수"},
    {"username": "annotator2", "password": "password123", "full_name": "이영희 교수"},
    {"username": "annotator3", "password": "password123", "full_name": "박민수 교수"},
    {"username": "annotator4", "password": "password123", "full_name": "정수진 교수"},
]

# Check if users already exist
existing_users = db.query(User).count()
if existing_users == 0:
    for user_data in test_users:
        user = User(
            username=user_data["username"],
            password_hash=get_password_hash(user_data["password"]),
            full_name=user_data["full_name"]
        )
        db.add(user)
    db.commit()
    print(f"✓ Created {len(test_users)} users")
else:
    print(f"✓ Users already exist ({existing_users} users)")

# Load essays from JSON
sample_essays = load_essays_from_json()

# Check if essays already exist
existing_essays = db.query(Essay).count()
if existing_essays == 0:
    for essay_data in sample_essays:
        essay = Essay(
            title=essay_data["title"],
            question=essay_data["question"],
            content=essay_data["content"],
            evidence=essay_data.get("evidence")
        )
        db.add(essay)
    db.commit()
    print(f"✓ Created {len(sample_essays)} essays from JSON")
else:
    print(f"✓ Essays already exist ({existing_essays} essays). Delete backend/annotation.db for a fresh start.")

db.close()
print("\n✓ Database initialized successfully!")
print("\nTest credentials:")
for user in test_users:
    print(f"  Username: {user['username']}, Password: {user['password']}")