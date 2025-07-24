import { create } from 'zustand';

interface UserState {
  // Placeholder for user state
  isAuthenticated: boolean;
  user: null | { id: string; name: string; email: string };
}

export const useUserStore = create<UserState>(() => ({
  isAuthenticated: false,
  user: null,
}));