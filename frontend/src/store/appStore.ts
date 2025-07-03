import { create } from 'zustand';
import { TabType } from '../types';

interface AppState {
  activeTab: TabType;
  copiedMessageId: string | null;
  setActiveTab: (tab: TabType) => void;
  setCopiedMessageId: (id: string | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeTab: 'chat',
  copiedMessageId: null,
  setActiveTab: (tab) => set({ activeTab: tab }),
  setCopiedMessageId: (id) => set({ copiedMessageId: id }),
}));