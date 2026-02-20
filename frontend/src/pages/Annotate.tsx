import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { essayApi, annotationApi } from '../api/client';
import type { Essay, Annotation, TraitAnnotation, BlindAnnotationInfo } from '../api/client';
import './Annotate.css';

type TraitType = 'content' | 'organization' | 'language' | 'ai_feedback';

const traitDescriptions: Record<TraitType, string> = {
    content: '주제에 대한 이해도, 주장의 타당성, 충분한 근거 제시 및 내용의 풍부함을 평가합니다.',
    organization: '글의 서론-본론-결론 구조, 문단 간의 논리적 연결성 및 응집성을 평가합니다.',
    language: '어휘 사용의 적절성, 문법적 정확성, 문장 구조의 다양성 및 유창성을 평가합니다.',
    ai_feedback: 'AI 피드백의 정확성, 유용성, 구체성 및 전반적인 품질을 평가합니다.'
};

const scoreLevelDescriptions: Record<TraitType, Record<number, string>> = {
    content: {
        5: "논문의 핵심 요소(연구 목적·개념·방법·결과·의미)를 정확히 식별하고, 중요 정보를 선별하며, 불필요한 내용을 배제하고, 원문 의미를 왜곡 없이 재구성하여 완성도 높은 요약을 제시한다.",
        4: "주요 내용을 대체로 정확하게 이해하고 핵심 정보를 적절히 선택해 요약한다. 일부 세부 정보는 단순화될 수 있으나 전체 요지 전달에는 문제가 없다.",
        3: "핵심 내용을 부분적으로만 파악하고, 일부 중요한 요소를 누락하거나 모호하게 표현한다. 요약이 가능하지만 불완전하거나 균형이 부족하다.",
        2: "논문의 주요 개념·결과를 충분히 식별하지 못하고, 요약 과정에서 핵심 정보를 누락·오해하여 원문과 불일치하는 내용이 다수 발생한다.",
        1: "논문의 핵심 내용을 파악하지 못하고, 요약이 왜곡되거나 무관한 내용 중심으로 이루어져 과제 목적을 전혀 충족하지 못한다."
    },
    organization: {
        5: "도입–전개–결론 구조를 명확히 구성하고, 정보를 논문 흐름에 따라 논리적으로 배열하며, 단락 간 관계를 부드럽게 연결한다. 전환 표현을 적절히 사용해 글 전체가 매우 일관적이다.",
        4: "구조를 안정적으로 유지하고 단락을 대체로 논리적 순서로 배열한다. 일부 연결이 약간 어색할 수 있으나 전체 흐름은 자연스럽다.",
        3: "기본 구조는 있으나 정보 배열이 불균형하거나 일부 전개가 단절적이다. 흐름은 이해 가능하나 완성도가 낮다.",
        2: "구조 요소가 형식적으로만 존재하며 정보가 부적절한 순서로 제시된다. 단락 간 연결이 부족해 글의 흐름을 따라가기 어렵다.",
        1: "구조가 거의 없거나 완전히 무너져 있으며, 내용이 무작위로 배열된다. 조직화된 글로 보기 어렵다."
    },
    language: { // User referred to '형식' for language/format
        5: "맞춤법·띄어쓰기·문장부호를 정확히 적용하고 오류가 거의 없다. 인용·참고문헌을 요구 형식에 맞춰 작성하며, 분량 및 형식 요건을 모두 충족한다.",
        4: "대부분 정확히 사용하며 소수의 경미한 오류만 보인다. 인용·참고문헌 형식도 대체로 정확하다. 분량·형식 요건을 대체로 준수한다.",
        3: "규범 오류가 다수 보이나 의미 전달에는 큰 지장을 주지 않는다. 인용·참고문헌에 불일치나 누락이 있다. 분량·형식 요건을 부분적으로 준수한다.",
        2: "규범 오류가 빈번하며 인용·참고문헌이 불완전·누락 상태다. 분량·형식 요건을 충족하지 못한다.",
        1: "규범 오류가 매우 많아 글의 이해가 어렵고, 인용·참고문헌이 없거나 전혀 형식 미준수 상태이다. 과제 수행 형식을 거의 따르지 않는다."
    },
    ai_feedback: { // Generic descriptions for AI feedback
        5: "AI 피드백이 매우 정확하고 유용하며 구체적인 개선 방향을 제시하여 평가에 큰 도움이 됩니다.",
        4: "AI 피드백이 정확하고 유용하지만, 약간의 모호함이나 일반적인 내용이 포함되어 있습니다.",
        3: "AI 피드백이 대체로 정확하나, 유용성이 낮거나 구체적인 개선점을 찾기 어렵습니다.",
        2: "AI 피드백에 일부 오류가 있거나, 평가에 거의 도움이 되지 않는 일반적인 내용입니다.",
        1: "AI 피드백이 부정확하거나, 오히려 평가에 혼란을 야기하여 신뢰하기 어렵습니다."
    }
};

export default function Annotate() {
    const { blindId } = useParams<{ blindId: string }>();
    const navigate = useNavigate();
    const [essay, setEssay] = useState<Essay | null>(null);
    const [blindAnnotations, setBlindAnnotations] = useState<BlindAnnotationInfo[]>([]); // New state
    const [essayIdMap, setEssayIdMap] = useState<Map<string, number>>(new Map()); // New state for mapping blind_id to essay_id
    const [currentEssayId, setCurrentEssayId] = useState<number | null>(null); // New state to hold the actual essayId
    const [annotation, setAnnotation] = useState<Annotation | null>(null);
    const [loading, setLoading] = useState(true);
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [showEvidence, setShowEvidence] = useState(false);

    // Active trait for selection
    const [activeTrait, setActiveTrait] = useState<TraitType>('content');

    // Trait states
    const [language, setLanguage] = useState<TraitAnnotation>({ score: null, selected_sentences: [] });
    const [organization, setOrganization] = useState<TraitAnnotation>({ score: null, selected_sentences: [] });
    const [content, setContent] = useState<TraitAnnotation>({ score: null, selected_sentences: [] });
    const [aiFeedbackScore, setAiFeedbackScore] = useState<number | null>(null);

    useEffect(() => {
        loadData();
    }, [blindId]); // Changed dependency from essayId to blindId

    const loadData = async () => {
        if (!blindId) return;

        setLoading(true);

        try {
            // 1. Fetch all blind annotations for navigation and mapping
            const allBlindAnnotations = await annotationApi.getBlindAnnotationIds();
            setBlindAnnotations(allBlindAnnotations);

            // 2. Find the current blind annotation info based on the URL blindId
            const currentBlindInfo = allBlindAnnotations.find(ba => ba.blind_id === blindId);
            if (!currentBlindInfo) {
                console.error(`Blind ID ${blindId} not found.`);
                navigate('/dashboard'); // Redirect if blindId is invalid
                return;
            }

            const essayId = currentBlindInfo.essay_id;
            setCurrentEssayId(essayId); // Store the actual essayId

            // 3. Fetch essay and annotation data using the actual essayId
            const [essayData, annotationData] = await Promise.all([
                essayApi.getEssay(essayId),
                annotationApi.getAnnotation(essayId)
            ]);

            setEssay(essayData);

            if (annotationData) {
                setAnnotation(annotationData);
                setLanguage(annotationData.language);
                setOrganization(annotationData.organization);
                setContent(annotationData.content);
                setAiFeedbackScore(annotationData.ai_feedback_score || null);
            } else {
                // Reset state for new annotation
                setAnnotation(null);
                setLanguage({ score: null, selected_sentences: [] });
                setOrganization({ score: null, selected_sentences: [] });
                setContent({ score: null, selected_sentences: [] });
                setAiFeedbackScore(null);
            }

            // Always reset to the first trait (Content) when a new essay is loaded
            setActiveTrait('content');

            // Build essayIdMap for sidebar and handleSave
            const newEssayIdMap = new Map<string, number>();
            allBlindAnnotations.forEach(ba => {
                newEssayIdMap.set(ba.blind_id, ba.essay_id);
            });
            setEssayIdMap(newEssayIdMap);


        } catch (error) {
            console.error('Failed to load data:', error);
            navigate('/dashboard'); // Redirect on error
        } finally {
            setLoading(false);
        }
    };

    const calculateRequired = (totalSentences: number, score: number | null) => {
        if (score === null) return 0;
        return Math.round(totalSentences * (5 - score) / 5);
    };

    const toggleSentence = (index: number) => {
        const trait = activeTrait;

        // AI feedback does not involve sentence selection
        if (trait === 'ai_feedback') return;

        const setState = trait === 'language' ? setLanguage : trait === 'organization' ? setOrganization : setContent;
        const state = trait === 'language' ? language : trait === 'organization' ? organization : content;

        if (state.score === null) {
            alert('이 항목에 대한 점수를 먼저 선택해 주세요.');
            return;
        }

        const selected = state.selected_sentences.includes(index)
            ? state.selected_sentences.filter(i => i !== index)
            : [...state.selected_sentences, index].sort((a, b) => a - b);

        setState({ ...state, selected_sentences: selected });
    };

    const handleSave = async () => {
        if (!essay || !currentEssayId) return; // Use currentEssayId

        const data = {
            essay_id: currentEssayId, // Use currentEssayId
            language,
            organization,
            content,
            ai_feedback_score: aiFeedbackScore
        };

        try {
            if (annotation) {
                await annotationApi.updateAnnotation(annotation.id, data);
            } else {
                await annotationApi.createAnnotation(data);
            }

            // Find current blind annotation index
            const currentIndex = blindAnnotations.findIndex(ba => ba.blind_id === blindId);
            const nextBlindAnnotation = blindAnnotations[currentIndex + 1];

            if (nextBlindAnnotation) {
                if (window.confirm('저장되었습니다. 다음 에세이를 바로 채점하시겠습니까?')) {
                    navigate(`/annotate/${nextBlindAnnotation.blind_id}`); // Navigate by blind_id
                } else {
                    navigate('/dashboard');
                }
            } else {
                alert('마지막 에세이입니다. 저장 후 목록으로 이동합니다.');
                navigate('/dashboard');
            }
        } catch (error: any) {
            alert('저장 실패: ' + (error.response?.data?.detail || error.message));
        }
    };

    if (loading) return <div className="loading">Loading...</div>;
    if (!essay) return <div className="error">Essay not found</div>;

    const totalSentences = essay.sentences?.length || 0;
    const currentTraitState = activeTrait === 'language' ? language : activeTrait === 'organization' ? organization : content;
    const requiredCount = calculateRequired(totalSentences, currentTraitState.score);

    return (
        <div className={`annotate-container ${!isSidebarOpen ? 'sidebar-collapsed' : ''}`}>
            <header className="annotate-header">
                <div className="header-left">
                    <h1>{blindId}</h1> {/* Display blindId */}
                </div>
                <div className="header-right">
                    <button onClick={() => navigate('/dashboard')} className="back-btn">← 목록으로</button>
                </div>
            </header>

            <div className="annotate-layout">
                {/* Left Sidebar: Blind Annotation List */}
                <aside className={`essay-sidebar ${isSidebarOpen ? 'open' : 'closed'}`}>
                    <div className="sidebar-header">
                        <h3>평가 항목 (Blind ID)</h3>
                        {/* No longer displaying overall counts here, as 'essays' state is removed. */}
                    </div>
                    <div className="sidebar-list">
                        {blindAnnotations.map((ba) => (
                            <div
                                key={ba.blind_id}
                                className={`sidebar-item ${ba.blind_id === blindId ? 'active' : ''}`}
                                onClick={() => navigate(`/annotate/${ba.blind_id}`)}
                            >
                                {/* is_annotated status check removed for simplicity */}
                                <span className="title">{ba.blind_id} (순서: {ba.display_order})</span>
                            </div>
                        ))}
                    </div>
                </aside>

                {/* Center Panel: Question & Essay */}
                <div className="left-panel">
                    <section className="question-section">
                        <div className="section-header">
                            <h3>질문 (Question)</h3>
                            <button 
                                className={`evidence-toggle-btn ${showEvidence ? 'active' : ''}`}
                                onClick={() => setShowEvidence(!showEvidence)}
                            >
                                {showEvidence ? '💡 질문만 보기' : '💡 참고자료 보기'}
                            </button>
                        </div>
                        <div className="question-box">{essay.question}</div>
                        
                        {showEvidence && essay.evidence && (
                            <div className="evidence-section">
                                <h4>📚 채점 참고 근거 (Evidence List)</h4>
                                <div className="evidence-list">
                                    {(() => {
                                        try {
                                            const evidenceList = JSON.parse(essay.evidence);
                                            return Array.isArray(evidenceList) ? evidenceList.map((item: any, idx: number) => (
                                                <div key={idx} className="evidence-item">
                                                    <span className="evidence-section-name">[{item.section}]</span>
                                                    <p className="evidence-text">{item.original_sentence}</p>
                                                </div>
                                            )) : <p>데이터 형식이 올바르지 않습니다.</p>;
                                        } catch (e) {
                                            console.error("Failed to parse evidence:", e);
                                            return <p>근거 데이터를 파싱할 수 없습니다.</p>;
                                        }
                                    })()}
                                </div>
                            </div>
                        )}
                    </section>

                    <section className="essay-section">
                        <div className="section-header">
                            <h3>학생 에세이 본문</h3>
                            <span className="active-indicator">
                                현재 평가 항목: <strong>{
                                    activeTrait === 'content' ? '내용' : 
                                    activeTrait === 'organization' ? '구성' : 
                                    activeTrait === 'language' ? '언어' : 
                                    'AI 피드백'
                                }</strong>
                            </span>
                        </div>
                        
                        <div className="essay-content-paragraph">
                            {essay.sentences?.map((sentence, idx) => {
                                const isSelected = (activeTrait === 'language' && language.selected_sentences.includes(idx)) ||
                                                   (activeTrait === 'organization' && organization.selected_sentences.includes(idx)) ||
                                                   (activeTrait === 'content' && content.selected_sentences.includes(idx));
                                return (
                                    <span
                                        key={idx}
                                        className={`sentence-span ${isSelected ? 'selected' : ''}`}
                                        onClick={() => toggleSentence(idx)}
                                        title={`문장 ${idx + 1}`}
                                    >
                                        {sentence}{' '}
                                    </span>
                                );
                            })}
                        </div>
                    </section>
                </div>

                {/* Right Panel: Evaluation */}
                <div className="right-panel">
                    <h3>평가 및 채점</h3>
                    
                    {activeTrait === 'content' && (
                        <EvaluationCard
                            title="1️⃣ 내용 (Content)"
                            description={traitDescriptions.content}
                            score={content.score}
                            onScoreChange={(s) => setContent({ ...content, score: s })}
                            selectedCount={content.selected_sentences.length}
                            requiredCount={calculateRequired(totalSentences, content.score)}
                            isActive={true}
                            onActivate={() => setActiveTrait('content')}
                            scoringGuide={scoreLevelDescriptions.content}
                        />
                    )}

                    {activeTrait === 'organization' && (
                        <EvaluationCard
                            title="2️⃣ 구성 (Organization)"
                            description={traitDescriptions.organization}
                            score={organization.score}
                            onScoreChange={(s) => setOrganization({ ...organization, score: s })}
                            selectedCount={organization.selected_sentences.length}
                            requiredCount={calculateRequired(totalSentences, organization.score)}
                            isActive={true}
                            onActivate={() => setActiveTrait('organization')}
                            scoringGuide={scoreLevelDescriptions.organization}
                        />
                    )}

                    {activeTrait === 'language' && (
                        <EvaluationCard
                            title="3️⃣ 언어 (Language)"
                            description={traitDescriptions.language}
                            score={language.score}
                            onScoreChange={(s) => setLanguage({ ...language, score: s })}
                            selectedCount={language.selected_sentences.length}
                            requiredCount={calculateRequired(totalSentences, language.score)}
                            isActive={true}
                            onActivate={() => setActiveTrait('language')}
                            scoringGuide={scoreLevelDescriptions.language}
                        />
                    )}

                    {activeTrait === 'ai_feedback' && (
                        <EvaluationCard
                            title="4️⃣ AI 피드백 (AI Feedback)"
                            description={traitDescriptions.ai_feedback}
                            score={aiFeedbackScore}
                            onScoreChange={(s) => setAiFeedbackScore(s)}
                            isAIFeedback={true}
                            isActive={true}
                            onActivate={() => setActiveTrait('ai_feedback')}
                            aiFeedbackContent={(() => {
                                try {
                                    if (essay.summary) {
                                        console.log("Raw essay.summary:", essay.summary); // Debugging line
                                        const summaryJson = JSON.parse(essay.summary);
                                        console.log("Parsed summaryJson:", summaryJson); // Debugging line
                                        console.log("summaryJson.feedback:", summaryJson.feedback); // Debugging line
                                        return summaryJson.feedback || "AI 피드백 내용을 찾을 수 없습니다.";
                                    }
                                } catch (e) {
                                    console.error("Failed to parse essay.summary as JSON:", e);
                                }
                                return "AI 피드백 내용 없음.";
                            })()}
                            scoringGuide={scoreLevelDescriptions.ai_feedback}
                        />
                    )}

                    <div className="trait-navigation">
                        <button 
                            className="nav-btn"
                            disabled={activeTrait === 'content'}
                            onClick={() => {
                                const traits: TraitType[] = ['content', 'organization', 'language', 'ai_feedback'];
                                const currentIndex = traits.indexOf(activeTrait);
                                if (currentIndex > 0) {
                                    setActiveTrait(traits[currentIndex - 1]);
                                }
                            }}
                        >
                            ← 이전 항목
                        </button>
                        <button 
                            className="nav-btn"
                            disabled={activeTrait === 'ai_feedback'}
                            onClick={() => {
                                const traits: TraitType[] = ['content', 'organization', 'language', 'ai_feedback'];
                                const currentIndex = traits.indexOf(activeTrait);
                                if (currentIndex < traits.length - 1) {
                                    setActiveTrait(traits[currentIndex + 1]);
                                }
                            }}
                        >
                            다음 항목 →
                        </button>
                    </div>

                    <div className="floating-actions">
                        <button onClick={handleSave} className="save-btn">최종 평가 저장</button>
                    </div>
                </div>

                <button 
                    className="sidebar-handle-btn" 
                    onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                >
                    {isSidebarOpen ? '사이드바 닫기' : '사이드바 열기'}
                </button>
            </div>
        </div>
    );
}

interface EvaluationCardProps {
    title: string;
    description: string;
    score: number | null;
    onScoreChange: (score: number) => void;
    // For regular traits, sentence selection is required
    selectedCount?: number;
    requiredCount?: number;
    // For AI feedback, no sentence selection
    isAIFeedback?: boolean; 
    isActive: boolean;
    onActivate: () => void;
    aiFeedbackContent?: string;
    scoringGuide?: Record<number, string>;
}

function EvaluationCard({
    title,
    description,
    score,
    onScoreChange,
    selectedCount,
    requiredCount,
    isAIFeedback = false,
    isActive,
    onActivate,
    aiFeedbackContent,
    scoringGuide
}: EvaluationCardProps) {
    const isComplete = isAIFeedback ? (score !== null) : (score !== null && selectedCount === requiredCount);

    return (
        <div 
            className={`eval-card ${isActive ? 'active' : ''} ${isComplete ? 'complete' : ''}`}
        >
            <div className="card-header">
                <h4>{title}</h4>
                {isActive && <span className="active-badge">평가 중</span>}
            </div>

            <p className="trait-description">{description}</p>
            
            {isAIFeedback && aiFeedbackContent && (
                <div className="ai-feedback-display">
                    <h5>AI 피드백 내용:</h5>
                    <div className="feedback-content-box">
                        {aiFeedbackContent.split('\n').map((line, idx) => (
                            <p key={idx}>{line}</p>
                        ))}
                    </div>
                </div>
            )}

            <div className="scoring-guide">
                <h5>점수 기준:</h5>
                <ul>
                    {scoringGuide ? (
                        Object.entries(scoringGuide).sort(([a], [b]) => parseInt(b) - parseInt(a)).map(([s, desc]) => (
                            <li key={s}><strong>{s}점:</strong> {desc}</li>
                        ))
                    ) : (
                        <>
                            <li><strong>5점:</strong> 매우 우수하며 결점이 거의 없음</li>
                            <li><strong>4점:</strong> 우수하며 미세한 결점만 있음</li>
                            <li><strong>3점:</strong> 보통이며 개선의 여지가 있음</li>
                            <li><strong>2점:</strong> 미흡하며 상당한 수정이 필요함</li>
                            <li><strong>1점:</strong> 매우 미흡하며 전반적인 수정이 필요함</li>
                        </>
                    )}
                </ul>
            </div>

            <div className="score-group">
                <label>점수 선택:</label>
                <div className="score-buttons">
                    {[1, 2, 3, 4, 5].map((s) => (
                        <button
                            key={s}
                            className={`score-btn ${score === s ? 'selected' : ''}`}
                            disabled={!isActive}
                            onClick={(e) => {
                                e.stopPropagation();
                                onScoreChange(s);
                                onActivate();
                            }}
                        >
                            {s}
                        </button>
                    ))}
                </div>
            </div>

            {score !== null && !isAIFeedback && (
                <div className={`selection-status ${isComplete ? 'valid' : 'invalid'}`}>
                    문장 선택: <strong>{selectedCount} / {requiredCount}</strong>
                    {isComplete && <span className="check-icon">✓</span>}
                </div>
            )}
            {score !== null && isAIFeedback && (
                <div className={`selection-status ${isComplete ? 'valid' : 'invalid'}`}>
                    AI 피드백 평가 완료: <strong>{score}점</strong>
                    {isComplete && <span className="check-icon">✓</span>}
                </div>
            )}
        </div>
    );
}