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
    const [annotation, setAnnotation] = useState<Annotation | null>(null);
    const [loading, setLoading] = useState(true);

    // Active trait for selection
    const [activeTrait, setActiveTrait] = useState<TraitType>('language');

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
            const [essayData, annotationData] = await Promise.all([
                essayApi.getEssay(parseInt(essayId)),
                annotationApi.getAnnotation(parseInt(essayId))
            ]);

            setEssay(essayData);

            if (annotationData) {
                setAnnotation(annotationData);
                setLanguage(annotationData.language);
                setOrganization(annotationData.organization);
                setContent(annotationData.content);
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

        const selected = state.selected_sentences.includes(index)
            ? state.selected_sentences.filter(i => i !== index)
            : [...state.selected_sentences, index].sort((a, b) => a - b);

        setState({ ...state, selected_sentences: selected });
    };

    const handleSave = async () => {
        if (!essay || !essayId) return;

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
            alert('저장되었습니다!');
            navigate('/dashboard');
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
        <div className="annotate-container">
            <header className="annotate-header">
                <button onClick={() => navigate('/dashboard')} className="back-btn">← 목록으로</button>
                <h1>{essay.title}</h1>
            </header>

            <div className="annotate-layout">
                {/* Left Panel: Question & Essay */}
                <div className="left-panel">
                    <section className="question-section">
                        <h3>질문 (Question)</h3>
                        <div className="question-box">{essay.question}</div>
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
                        
                        <div className="sentences-list">
                            {essay.sentences?.map((sentence, idx) => {
                                const isSelected = currentTraitState.selected_sentences.includes(idx);
                                return (
                                    <div
                                        key={idx}
                                        className={`sentence-item ${isSelected ? 'selected' : ''}`}
                                        onClick={() => toggleSentence(idx)}
                                    >
                                        <span className="sentence-num">{idx + 1}</span>
                                        <span className="sentence-text">{sentence}</span>
                                    </div>
                                );
                            })}
                        </div>
                    </section>
                </div>

                {/* Right Panel: Evaluation */}
                <div className="right-panel">
                    <h3>평가 및 채점</h3>
                    
                    <EvaluationCard
                        title="1️⃣ 언어 (Language)"
                        trait="language"
                        score={language.score}
                        onScoreChange={(s) => setLanguage({ ...language, score: s })}
                        selectedCount={language.selected_sentences.length}
                        requiredCount={calculateRequired(totalSentences, language.score)}
                        isActive={activeTrait === 'language'}
                        onActivate={() => setActiveTrait('language')}
                    />

                    <EvaluationCard
                        title="2️⃣ 구성 (Organization)"
                        trait="organization"
                        score={organization.score}
                        onScoreChange={(s) => setOrganization({ ...organization, score: s })}
                        selectedCount={organization.selected_sentences.length}
                        requiredCount={calculateRequired(totalSentences, organization.score)}
                        isActive={activeTrait === 'organization'}
                        onActivate={() => setActiveTrait('organization')}
                    />

                    <EvaluationCard
                        title="3️⃣ 내용 (Content)"
                        trait="content"
                        score={content.score}
                        onScoreChange={(s) => setContent({ ...content, score: s })}
                        selectedCount={content.selected_sentences.length}
                        requiredCount={calculateRequired(totalSentences, content.score)}
                        isActive={activeTrait === 'content'}
                        onActivate={() => setActiveTrait('content')}
                    />

                    <div className="floating-actions">
                        <button onClick={handleSave} className="save-btn">최종 평가 저장</button>
                    </div>
                </div>
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
            onClick={onActivate}
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
                            onClick={(e) => {
                                e.stopPropagation();
                                onScoreChange(s);
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
