import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
  timeout: 600_000, // reasoning 모델 분석은 응답 시간 변동이 커서 안전망을 10분으로 둔다
});
