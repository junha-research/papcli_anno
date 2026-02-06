import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export interface User {
    id: number;
    username: string;
    full_name: string;
}

export interface TraitAnnotation {
    score: number | null;
    selected_sentences: number[];
}

export interface Annotation {
    id: number;
    essay_id: number;
    language: TraitAnnotation;
    organization: TraitAnnotation;
    content: TraitAnnotation;
    is_submitted: boolean;
}

export interface Essay {
    id: number;
    title: string;
    content: string;
    question: string;
    is_annotated?: boolean;
    sentences?: string[];
}

export const authApi = {
    login: async (username: string, password: string) => {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        const response = await api.post('/auth/login', formData);
        return response.data;
    },

    getCurrentUser: async () => {
        const response = await api.get<User>('/users/me');
        return response.data;
    },
};

export const essayApi = {
    getEssays: async () => {
        const response = await api.get<Essay[]>('/essays');
        return response.data;
    },

    getEssay: async (id: number) => {
        const response = await api.get<Essay>(`/essays/${id}`);
        return response.data;
    },
};

export const annotationApi = {
    getAnnotation: async (essayId: number) => {
        const response = await api.get<Annotation | null>(`/annotations/${essayId}`);
        return response.data;
    },

    createAnnotation: async (data: Omit<Annotation, 'id' | 'is_submitted'>) => {
        const response = await api.post<Annotation>('/annotations', data);
        return response.data;
    },

    updateAnnotation: async (id: number, data: Partial<Annotation>) => {
        const response = await api.patch<Annotation>(`/annotations/${id}`, data);
        return response.data;
    },

    submitAll: async () => {
        const response = await api.post('/annotations/submit-all');
        return response.data;
    },
};

export default api;
