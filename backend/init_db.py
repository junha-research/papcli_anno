import json
import os
import random
import uuid
from models import Base, engine, SessionLocal, User, Essay, Annotation
from auth import get_password_hash

# 테이블 생성 및 초기화
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def load_and_distribute_essays():
    json_path = os.path.join(os.path.dirname(__file__), '..', 'paperclinic_generated_dataset_gemini_1.json')
    if not os.path.exists(json_path):
        print(f"Error: JSON file not found at {json_path}")
        return [], {}

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_raw_data = data.get('data', [])
    
    # 1. 파일별 그룹화 및 65개 세트(Q1~Q5 각 13개)가 완벽한 논문 찾기
    papers = {}
    for item in all_raw_data:
        fname = item.get('filename')
        if fname not in papers: papers[fname] = []
        papers[fname].append(item)
    
    target_filename = None
    target_data = []
    
    for fname, items in papers.items():
        # 질문별 개수 확인 (Q1~Q5 각 13개씩 있는지)
        q_groups = {}
        for it in items:
            q = it.get('question')
            if q not in q_groups: q_groups[q] = []
            q_groups[q].append(it)
        
        # 5개 질문이 모두 있고, 각 질문당 최소 13개(정답1+노이즈12)가 있는 논문 선택
        if len(q_groups) == 5:
            valid_set = []
            for q_text, q_items in q_groups.items():
                orig = [it for it in q_items if it.get('is_original')]
                noise = [it for it in q_items if not it.get('is_original')]
                if orig and len(noise) >= 12:
                    valid_set.append(orig[0])
                    valid_set.extend(noise[:12])
                else:
                    break
            
            if len(valid_set) == 65:
                target_filename = fname
                target_data = valid_set
                break
    
    if not target_filename:
        print("Error: 65개 세트(Q1~Q5 각 13개)가 완벽한 논문을 찾을 수 없습니다.")
        return [], {}

    print(f"✓ Target paper identified for blind test: {target_filename} (65 items selected)")

    # 질문 ID 태깅 (Q1~Q5)
    unique_questions = list(set([item['question'] for item in target_data]))
    for item in target_data:
        item['q_id'] = f"Q{unique_questions.index(item['question']) + 1}"

    # 2. 블록(A~E) 층화 분배 (각 블록 13개)
    blocks = {'A': [], 'B': [], 'C': [], 'D': [], 'E': []}
    block_names = list(blocks.keys())
    
    # 질문별로 13개를 A~E에 고르게 분산
    for q_idx in range(5):
        q_id = f"Q{q_idx + 1}"
        q_pool = [it for it in target_data if it['q_id'] == q_id]
        orig = [it for it in q_pool if it.get('is_original')][0]
        noises = [it for it in q_pool if not it.get('is_original')]
        
        # 정답 문장은 블록 A~E 중 하나씩 배치 (Q1->A, Q2->B, Q3->C, Q4->D, Q5->E)
        blocks[block_names[q_idx]].append(orig)
        
        # 노이즈 12개를 나머지 블록에 분배
        random.shuffle(noises)
        for i, n_item in enumerate(noises):
            # 순환하며 분배
            chosen_block = block_names[(q_idx + 1 + i) % 5]
            blocks[chosen_block].append(n_item)

    return target_data, blocks

def anti_anchoring_shuffle(items):
    """앵커링 방지를 위해 동일한 Q_id가 연속 노출되지 않도록 셔플"""
    random.shuffle(items)
    for i in range(1, len(items) - 1):
        if items[i].get('q_id') == items[i-1].get('q_id'):
            for j in range(i+1, len(items)):
                if items[j].get('q_id') != items[i-1].get('q_id') and items[j].get('q_id') != items[i].get('q_id'):
                    items[i], items[j] = items[j], items[i]
                    break
    return items

db = SessionLocal()

# DB 초기화
print("! Resetting database for new blind test...")
db.query(Annotation).delete()
db.query(Essay).delete()
db.query(User).delete()
db.commit()

# 1. 평가자(User) 5명 생성
test_users = [
    {"username": "annotator1", "password": "password123", "full_name": "양윤모"},
    {"username": "annotator2", "password": "password123", "full_name": "최다온"},
    {"username": "annotator3", "password": "password123", "full_name": "홍윤이"},
    {"username": "annotator4", "password": "password123", "full_name": "염준화"},
    {"username": "annotator5", "password": "password123", "full_name": "송준하"},
]

user_map = {}
for u_data in test_users:
    user = User(username=u_data["username"], password_hash=get_password_hash(u_data["password"]), full_name=u_data["full_name"])
    db.add(user)
    db.flush()
    user_map[user.username] = user.id
db.commit()
print("✓ Created 5 evaluator accounts.")

# 2. 에세이(Essay) 생성
all_data, blocks = load_and_distribute_essays()

# 질문별 공통 참고자료(정답 문항의 evidence_list) 추출
question_evidence_map = {}
for item in all_data:
    if item.get('is_original') and item.get('evidence_list'):
        question_evidence_map[item.get('question')] = item.get('evidence_list')

# 논문 요약 데이터 로드
summary_json_path = os.path.join(os.path.dirname(__file__), '..', 'paperclinic_papers_summary_1.json')
paper_summaries = {}
if os.path.exists(summary_json_path):
    with open(summary_json_path, 'r', encoding='utf-8') as f:
        paper_summaries = json.load(f)
    print(f"✓ Loaded {len(paper_summaries)} paper summaries from JSON.")

if all_data:
    for idx, item in enumerate(all_data):
        output = item.get('output', {})
        keys = list(output.keys())
        
        scores = {
            "content": output.get(keys[0]) if len(keys) > 0 else None,
            "organization": output.get(keys[1]) if len(keys) > 1 else None,
            "language": output.get(keys[2]) if len(keys) > 2 else None,
            "consistency": output.get(keys[3]) if len(keys) > 3 else None
        }

        ai_feedback = {
            "evidence_list": item.get('evidence_list', []),
            "reasoning": item.get('reasoning', '') or item.get('organization_reasoning', ''),
            "scores": scores,
            "consistency_score": scores["consistency"],
            "feedback": item.get('feedback', '')
        }
        
        # 파일명을 숨기기 위해 순차적인 번호로 타이틀 부여
        blind_title = f"평가 문항 #{idx + 1}"
        
        # 실제 논문 요약 매칭 (filename 기반)
        orig_filename = item.get('filename')
        actual_paper_summary = paper_summaries.get(orig_filename, "요약 정보가 제공되지 않았습니다.")
        
        # 질문 기반 공통 참고자료 할당
        common_evidence = question_evidence_map.get(item.get('question'), [])
        
        essay = Essay(
            title=blind_title,
            content=item.get('input', ''),
            question=item.get('question', ''),
            evidence=json.dumps(common_evidence, ensure_ascii=False),
            summary=json.dumps(ai_feedback, ensure_ascii=False),
            paper_summary=actual_paper_summary # 새 컬럼에 저장
        )
        db.add(essay)
        db.flush()
        
        # 할당을 위해 DB ID 매핑
        item['db_id'] = essay.id
        
    db.commit()
    # 검증: Essay 개수 확인 (정확히 65개여야 함)
    essay_count = db.query(Essay).count()
    print(f"✓ Validation: {essay_count} essays created. (Expected: 65)")

# 3. 빈 어노테이션(Annotation) 레코드로 할당 (130개)
if all_data and blocks:
    evaluator_mapping = {
        "annotator1": blocks['A'] + blocks['B'],
        "annotator2": blocks['B'] + blocks['C'],
        "annotator3": blocks['C'] + blocks['D'],
        "annotator4": blocks['D'] + blocks['E'],
        "annotator5": blocks['E'] + blocks['A']
    }
    
    assign_count = 0
    for username, assigned_items in evaluator_mapping.items():
        user_id = user_map.get(username)
        if not user_id: continue
        
        # 유저별 26개 문항 앵커링 방지 셔플
        shuffled_items = anti_anchoring_shuffle(assigned_items.copy())
        
        for order_idx, item in enumerate(shuffled_items):
            annotation = Annotation(
                user_id=user_id,
                essay_id=item['db_id'],
                blind_id=f"{uuid.uuid4().hex[:8].upper()}", 
                display_order=order_idx + 1,
                is_submitted=False
            )
            db.add(annotation)
            assign_count += 1
            
    db.commit()
    # 검증: Annotation 할당 개수 확인 (정확히 130개여야 함)
    total_annotations = db.query(Annotation).count()
    print(f"✓ Validation: {total_annotations} annotations assigned. (Expected: 130)")

db.close()
print("\n✓ Database for Blind Test initialized successfully!")
