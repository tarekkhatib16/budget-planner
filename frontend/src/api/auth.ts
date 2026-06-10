import { api } from './client';
import type { User } from './types';

export interface AuthResponse {
  token: string;
  user: User;
}

export function register(email: string, password: string): Promise<AuthResponse> {
  return api.post<AuthResponse>('/auth/register', { email, password });
}

export function login(email: string, password: string): Promise<AuthResponse> {
  return api.post<AuthResponse>('/auth/login', { email, password });
}

export function me(): Promise<User> {
  return api.get<User>('/auth/me');
}
