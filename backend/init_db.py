from models import Base, engine, SessionLocal, User, Essay
from auth import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

# Mock essay data
sample_essays = [
    {
        "title": "논문 1 - Transformer 핵심 기여",
        "question": "이 논문의 핵심 기여도를 설명하세요.",
        "content": """이 논문은 자연어 처리 분야에서 획기적인 성과를 달성했다. 기존 RNN 모델들과 달리 완전히 어텐션 메커니즘만 사용한다. 실험 결과 BLEU 점수가 기존 대비 15% 향상되었다. 병렬 처리가 가능해 학습 속도도 크게 개선되었다. 하지만 계산 비용이 증가하는 단점이 있다. 향후 연구에서는 효율성 개선이 필요하다. 모델의 해석 가능성도 중요한 과제로 남아있다. 다양한 downstream task에서 우수한 성능을 보였다."""
    },
    {
        "title": "논문 2 - BERT 사전학습",
        "question": "이 논문에서 제시하는 핵심 개념을 설명하세요.",
        "content": """BERT는 양방향 인코더를 사용하는 사전학습 모델이다. Masked Language Model 기법으로 문맥을 학습한다. Next Sentence Prediction으로 문장 간 관계도 파악한다. 대규모 코퍼스로 사전학습 후 fine-tuning한다. 다양한 NLP 태스크에서 SOTA를 달성했다. 특히 질의응답과 감성분석에서 뛰어났다. 계산 자원이 많이 필요한 것이 단점이다."""
    },
    {
        "title": "논문 3 - ResNet 깊은 네트워크",
        "question": "이 논문의 방법론을 설명하세요.",
        "content": """ResNet은 잔차 연결을 도입한 딥러닝 모델이다. Skip connection으로 gradient vanishing 문제를 해결했다. 152층까지 깊은 네트워크 학습이 가능해졌다. ImageNet 대회에서 1위를 차지했다. 컴퓨터 비전 분야에 큰 영향을 미쳤다. 다른 아키텍처에도 잔차 연결이 적용되었다."""
    },
    {
        "title": "논문 4 - GAN 생성 모델",
        "question": "이 논문의 실험 결과를 분석하세요.",
        "content": """GAN은 생성자와 판별자가 경쟁하는 구조다. 생성자는 실제 같은 데이터를 만들려 한다. 판별자는 진짜와 가짜를 구별하려 한다. 두 네트워크가 동시에 학습되며 발전한다. 이미지 생성에서 놀라운 결과를 보였다. 하지만 학습이 불안정한 문제가 있다. Mode collapse 현상도 자주 발생한다."""
    },
    {
        "title": "논문 5 - GPT 언어 모델",
        "question": "이 논문의 한계점과 향후 연구 방향을 설명하세요.",
        "content": """GPT는 대규모 텍스트로 사전학습된 언어 모델이다. Transformer 디코더 구조를 사용한다. Zero-shot 학습이 가능하다는 장점이 있다. 다양한 언어 생성 태스크를 수행할 수 있다. 하지만 사실성 검증이 어렵다. 편향된 데이터로 인한 문제도 있다. 모델 크기가 계속 커지고 있어 환경 문제도 제기된다."""
    }
]

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

# Check if essays already exist
existing_essays = db.query(Essay).count()
if existing_essays == 0:
    for essay_data in sample_essays:
        essay = Essay(
            title=essay_data["title"],
            question=essay_data["question"],
            content=essay_data["content"]
        )
        db.add(essay)
    db.commit()
    print(f"✓ Created {len(sample_essays)} essays")
else:
    print(f"✓ Essays already exist ({existing_essays} essays)")

db.close()
print("\n✓ Database initialized successfully!")
print("\nTest credentials:")
for user in test_users:
    print(f"  Username: {user['username']}, Password: {user['password']}")
