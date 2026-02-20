import sqlite3
import pandas as pd
import numpy as np
import re
from scipy import stats
from sklearn.metrics import cohen_kappa_score
import warnings

# 경고 무시 (데이터 수가 적을 때의 ANOVA 경고 등)
warnings.filterwarnings('ignore')

def get_kappa_interpretation(kappa):
    if kappa < 0: return "일치 불일치 (Poor)"
    if kappa < 0.2: return "아주 낮은 일치 (Slight)"
    if kappa < 0.4: return "낮은 일치 (Fair)"
    if kappa < 0.6: return "보통 일치 (Moderate)"
    if kappa < 0.8: return "높은 일치 (Substantial)"
    return "매우 높은 일치 (Almost Perfect)"

def parse_noise_level(title):
    """
    파일명_Q번호_노이즈레벨_인덱스 포맷에서 노이즈 레벨 추출
    예: 2302.03287v3.pdf_Q1_L2_0 -> 2
    예: ..._Orig_1 -> 0
    """
    if 'Orig' in title:
        return 0
    match = re.search(r'_L(\d+)_', title)
    if match:
        return int(match.group(1))
    return None

def analyze():
    # 1. DB 연결 및 데이터 로드
    db_path = 'annotation.db'
    try:
        conn = sqlite3.connect(db_path)
        query = """
        SELECT 
            a.essay_id, 
            a.user_id, 
            a.score_language, 
            a.score_organization, 
            a.score_content, 
            e.title
        FROM annotations a
        JOIN essays e ON a.essay_id = e.id
        WHERE a.is_submitted = 1
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
    except Exception as e:
        print(f"Error: DB를 읽을 수 없습니다. ({e})")
        return

    if df.empty:
        print("분석할 데이터가 없습니다. (is_submitted=1 인 데이터가 필요합니다.)")
        return

    # 2. 노이즈 레벨 파싱
    df['noise_level'] = df['title'].apply(parse_noise_level)
    
    # 노이즈 레벨이 파싱되지 않는 데이터(블라인드 처리된 경우 등) 제외
    df = df.dropna(subset=['noise_level'])
    if df.empty:
        print("노이즈 레벨을 추출할 수 있는 데이터가 없습니다. (Title 포맷 확인 필요)")
        return

    traits = {
        'language': '언어 영역 (Language)',
        'organization': '구성 영역 (Organization)',
        'content': '내용 영역 (Content)'
    }

    print("" + "="*60)
    print("🎓 합성 데이터셋 평가 결과 통계 분석 리포트")
    print("="*60)

    for trait_key, trait_name in traits.items():
        score_col = f'score_{trait_key}'
        
        print(f"[{trait_name}]")
        print("-" * 30)

        # --- (1) 평가자 간 일치도 (IRR) ---
        # 동일 essay_id에 대해 user_id별로 피벗
        try:
            pivot_df = df.pivot(index='essay_id', columns='user_id', values=score_col).dropna()
            if pivot_df.shape[1] >= 2:
                # 첫 두 명의 평가자 점수 추출
                rater1 = pivot_df.iloc[:, 0].astype(int)
                rater2 = pivot_df.iloc[:, 1].astype(int)
                
                kappa = cohen_kappa_score(rater1, rater2, weights='quadratic')
                print(f"1. 평가자 일치도 (Quadratic Kappa): {kappa:.4f}")
                print(f"   => 해석: {get_kappa_interpretation(kappa)}")
            else:
                print("1. 평가자 일치도: 데이터 부족 (교차 평가 데이터 필요)")
        except:
            print("1. 평가자 일치도: 계산 오류 (데이터 형식을 확인하세요)")

        # --- (2) 타당성 검증 (Validity) ---
        # essay_id별 평균 점수 산출
        validity_df = df.groupby('essay_id').agg({
            score_col: 'mean',
            'noise_level': 'first'
        }).reset_index()

        # Spearman 상관분석
        rho, p_val = stats.spearmanr(validity_df['noise_level'], validity_df[score_col])
        print(f"2. Spearman 상관계수 (Noise vs Score): {rho:.4f}")
        print(f"   => p-value: {p_val:.4e} ({'유의미함' if p_val < 0.05 else '유의미하지 않음'})")

        # ANOVA (그룹 간 평균 차이)
        groups = [validity_df[validity_df['noise_level'] == lvl][score_col] for lvl in sorted(validity_df['noise_level'].unique())]
        f_stat, anova_p = stats.f_oneway(*groups)
        print(f"3. ANOVA 결과 (F-statistic): {f_stat:.4f}")
        print(f"   => p-value: {anova_p:.4e} ({'그룹 간 차이 유의미' if anova_p < 0.05 else '차이 없음'})")

    print("" + "="*60)
    print("분석 완료.")
    print("="*60 + "")

if __name__ == "__main__":
    analyze()
