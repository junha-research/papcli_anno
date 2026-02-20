import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { essayApi } from '../api/client';
import type { Essay } from '../api/client';
import './SummaryDetail.css';

export default function SummaryDetail() {
    const { essayId } = useParams<{ essayId: string }>();
    const [essay, setEssay] = useState<Essay | null>(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const loadEssay = async () => {
            if (!essayId) return;
            try {
                const data = await essayApi.getEssay(parseInt(essayId));
                setEssay(data);
            } catch (error) {
                console.error('Failed to load essay summary:', error);
            } finally {
                setLoading(false);
            }
        };
        loadEssay();
    }, [essayId]);

    if (loading) return <div className="loading">Loading summary...</div>;
    if (!essay) return <div className="error">Summary not found.</div>;

    return (
        <div className="summary-detail-page">
            <header className="summary-detail-header">
                <button onClick={() => navigate('/dashboard')} className="back-btn">← Back to Dashboard</button>
                <h1>논문 요약</h1>
            </header>

            <div className="summary-detail-card">
                <div className="summary-info">
                    <h2>{essay.title}</h2>
                    <div className="summary-text">
                        {essay.paper_summary || '요약 정보가 없습니다.'}
                    </div>
                </div>
            </div>
        </div>
    );
}
