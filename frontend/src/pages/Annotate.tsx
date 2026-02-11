import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { essayApi, annotationApi } from '../api/client';
import type { Essay, Annotation, TraitAnnotation } from '../api/client';
import './Annotate.css';

type TraitType = 'language' | 'organization' | 'content';

export default function Annotate() {
    const { essayId } = useParams<{ essayId: string }>();
    const navigate = useNavigate();
    const [essay, setEssay] = useState<Essay | null>(null);
    const [essays, setEssays] = useState<Essay[]>([]);
    const [annotation, setAnnotation] = useState<Annotation | null>(null);
    const [loading, setLoading] = useState(true);
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [showEvidence, setShowEvidence] = useState(false);

    // Active trait for selection
    const [activeTrait, setActiveTrait] = useState<TraitType>('language');

    const traitDescriptions: Record<TraitType, string> = {
        language: "언어 항목 평가 기준에 대한 설명입니다. 문법, 어휘, 표현의 다양성 등을 고려합니다.",
        organization: "구성 항목 평가 기준에 대한 설명입니다. 글의 흐름, 단락 구성, 논리적 연결성 등을 고려합니다.",
        content: "내용 항목 평가 기준에 대한 설명입니다. 주제의 명확성, 아이디어의 깊이, 관련성 등을 고려합니다."
    };

    // Trait states
    const [language, setLanguage] = useState<TraitAnnotation>({ score: null, selected_sentences: [] });
    const [organization, setOrganization] = useState<TraitAnnotation>({ score: null, selected_sentences: [] });
    const [content, setContent] = useState<TraitAnnotation>({ score: null, selected_sentences: [] });

    useEffect(() => {
        loadData();
    }, [essayId]);

    const loadData = async () => {
        if (!essayId) return;

        try {
            const [essayData, annotationData, allEssays] = await Promise.all([
                essayApi.getEssay(parseInt(essayId)),
                annotationApi.getAnnotation(parseInt(essayId)),
                essayApi.getEssays()
            ]);

            setEssay(essayData);
            setEssays(allEssays);

            if (annotationData) {
                setAnnotation(annotationData);
                setLanguage(annotationData.language);
                setOrganization(annotationData.organization);
                setContent(annotationData.content);
            } else {
                // Reset state for new essay
                setAnnotation(null);
                setLanguage({ score: null, selected_sentences: [] });
                setOrganization({ score: null, selected_sentences: [] });
                setContent({ score: null, selected_sentences: [] });
                setActiveTrait('language');
            }
        } catch (error) {
            console.error('Failed to load data:', error);
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
        if (!essay || !essayId || essays.length === 0) return;

        const data = {
            essay_id: parseInt(essayId),
            language,
            organization,
            content
        };

        try {
            if (annotation) {
                await annotationApi.updateAnnotation(annotation.id, data);
            } else {
                await annotationApi.createAnnotation(data);
            }

            // Find current index and check for next essay
            const currentIndex = essays.findIndex(e => e.id === essay.id);
            const nextEssay = essays[currentIndex + 1];

            if (nextEssay) {
                if (window.confirm('저장되었습니다. 다음 에세이를 바로 채점하시겠습니까?')) {
                    navigate(`/annotate/${nextEssay.id}`);
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
                    <h1>{essay.title.split('_')[0]}</h1>
                </div>
                <div className="header-right">
                    <button onClick={() => navigate('/dashboard')} className="back-btn">← 목록으로</button>
                </div>
            </header>

            <div className="annotate-layout">
                {/* Left Sidebar: Essay List */}
                <aside className={`essay-sidebar ${isSidebarOpen ? 'open' : 'closed'}`}>
                    <div className="sidebar-header">
                        <h3>에세이 목록</h3>
                        <span className="count">{essays.filter(e => e.is_annotated).length} / {essays.length}</span>
                    </div>
                    <div className="sidebar-list">
                        {essays.map((e) => (
                            <div
                                key={e.id}
                                className={`sidebar-item ${e.id === essay.id ? 'active' : ''} ${e.is_annotated ? 'completed' : ''}`}
                                onClick={() => navigate(`/annotate/${e.id}`)}
                            >
                                <span className="status-icon">{e.is_annotated ? '✓' : '•'}</span>
                                <span className="title">{e.title.split('_')[0]}</span>
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
                                    {JSON.parse(essay.evidence).map((item: any, idx: number) => (
                                        <div key={idx} className="evidence-item">
                                            <span className="evidence-section-name">[{item.section}]</span>
                                            <p className="evidence-text">{item.original_sentence}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </section>

                    <section className="essay-section">
                        <div className="section-header">
                            <h3>학생 에세이 본문</h3>
                            <span className="active-indicator">
                                현재 평가 항목: <strong>{
                                    activeTrait === 'language' ? '언어' : 
                                    activeTrait === 'organization' ? '구성' : '내용'
                                }</strong>
                            </span>
                        </div>
                        
                        <div className="essay-content-paragraph">
                            {essay.sentences?.map((sentence, idx) => {
                                const isSelected = currentTraitState.selected_sentences.includes(idx);
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
                    
                    {/* Dynamically rendered EvaluationCard based on activeTrait */}
                    {(activeTrait === 'language' && (
                        <EvaluationCard
                            title="1️⃣ 언어 (Language)"
                            trait="language"
                            score={language.score}
                            onScoreChange={(s) => setLanguage({ ...language, score: s })}
                            selectedCount={language.selected_sentences.length}
                            requiredCount={calculateRequired(totalSentences, language.score)}
                            isActive={true}
                            onActivate={() => setActiveTrait('language')}
                        />
                    )) || (activeTrait === 'organization' && (
                        <EvaluationCard
                            title="2️⃣ 구성 (Organization)"
                            trait="organization"
                            score={organization.score}
                            onScoreChange={(s) => setOrganization({ ...organization, score: s })}
                            selectedCount={organization.selected_sentences.length}
                            requiredCount={calculateRequired(totalSentences, organization.score)}
                            isActive={true}
                            onActivate={() => setActiveTrait('organization')}
                        />
                    )) || (activeTrait === 'content' && (
                        <EvaluationCard
                            title="3️⃣ 내용 (Content)"
                            trait="content"
                            score={content.score}
                            onScoreChange={(s) => setContent({ ...content, score: s })}
                            selectedCount={content.selected_sentences.length}
                            requiredCount={calculateRequired(totalSentences, content.score)}
                            isActive={true}
                            onActivate={() => setActiveTrait('content')}
                        />
                    ))}

                    <div className="trait-description-box">
                        <h4>평가 기준</h4>
                        <p>{traitDescriptions[activeTrait]}</p>
                    </div>

                    <div className="trait-navigation">
                        <button 
                            className="nav-btn"
                            disabled={activeTrait === 'language'}
                            onClick={() => {
                                if (activeTrait === 'organization') setActiveTrait('language');
                                else if (activeTrait === 'content') setActiveTrait('organization');
                            }}
                        >
                            ← 이전 항목
                        </button>
                        <button 
                            className="nav-btn"
                            disabled={activeTrait === 'content'}
                            onClick={() => {
                                if (activeTrait === 'language') setActiveTrait('organization');
                                else if (activeTrait === 'organization') setActiveTrait('content');
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
    trait: TraitType;
    score: number | null;
    onScoreChange: (score: number) => void;
    selectedCount: number;
    requiredCount: number;
    isActive: boolean;
    onActivate: () => void;
}

function EvaluationCard({
    title,
    score,
    onScoreChange,
    selectedCount,
    requiredCount,
    isActive,
    onActivate
}: EvaluationCardProps) {
    const isComplete = score !== null && selectedCount === requiredCount;

    return (
        <div 
            className={`eval-card ${isActive ? 'active' : ''} ${isComplete ? 'complete' : ''}`}
        >
            <div className="card-header">
                <h4>{title}</h4>
                {isActive && <span className="active-badge">평가 중</span>}
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

            {score !== null && (
                <div className={`selection-status ${isComplete ? 'valid' : 'invalid'}`}>
                    문장 선택: <strong>{selectedCount} / {requiredCount}</strong>
                    {isComplete && <span className="check-icon">✓</span>}
                </div>
            )}
        </div>
    );
}