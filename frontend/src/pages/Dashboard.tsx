import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { essayApi, authApi } from '../api/client';
import type { Essay } from '../api/client';
import { useAuthStore } from '../store/authStore';
import './Dashboard.css';

export default function Dashboard() {
    const [essays, setEssays] = useState<Essay[]>([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const { user, setAuth, logout } = useAuthStore();

    useEffect(() => {
        const init = async () => {
            // If user info is missing but token exists, fetch user info
            if (!user) {
                try {
                    const userData = await authApi.getCurrentUser();
                    const token = localStorage.getItem('token');
                    if (token) setAuth(userData, token);
                } catch (error) {
                    console.error('Failed to fetch user:', error);
                    logout();
                    navigate('/');
                    return;
                }
            }
            loadEssays();
        };
        init();
    }, []);

    const loadEssays = async () => {
        try {
            const data = await essayApi.getEssays();
            setEssays(data);
        } catch (error) {
            console.error('Failed to load essays:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    const completedCount = essays.filter(e => e.is_annotated).length;
    const progress = essays.length > 0 ? (completedCount / essays.length) * 100 : 0;

    return (
        <div className="dashboard">
            <header className="dashboard-header">
                <div>
                    <h1>Annotation Dashboard</h1>
                    <p>Welcome, {user?.full_name}</p>
                </div>
                <button onClick={handleLogout} className="logout-btn">Logout</button>
            </header>

            <div className="progress-section">
                <h2>Progress: {completedCount} / {essays.length}</h2>
                <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${progress}%` }}></div>
                </div>
            </div>

            <div className="essay-list">
                <h2>Essays</h2>
                {loading ? (
                    <p>Loading...</p>
                ) : (
                    <div className="essay-grid">
                        {essays.map((essay) => (
                            <div
                                key={essay.id}
                                className={`essay-card ${essay.is_annotated ? 'completed' : ''}`}
                                onClick={() => navigate(`/annotate/${essay.id}`)}
                            >
                                <div className="essay-card-header">
                                    <h3>{essay.title.split('_')[0]}</h3>
                                    {essay.is_annotated && <span className="badge">✓ Completed</span>}
                                </div>
                                <p className="essay-question">{essay.question}</p>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
