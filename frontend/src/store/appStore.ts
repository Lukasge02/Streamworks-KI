import { create } from 'zustand';
import { TabType, SearchFilter } from '../types';

interface SmartSearchState {
  lastQuery: string;
  lastFilters: SearchFilter;
  searchHistory: string[];
}

interface AppState {
  activeTab: TabType;
  copiedMessageId: string | null;
  smartSearch: SmartSearchState;
  setActiveTab: (tab: TabType) => void;
  setCopiedMessageId: (id: string | null) => void;
  updateSmartSearchState: (state: Partial<SmartSearchState>) => void;
  addToSearchHistory: (query: string) => void;
  clearSearchHistory: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeTab: 'chat',
  copiedMessageId: null,
  smartSearch: {
    lastQuery: '',
    lastFilters: {},
    searchHistory: []
  },
  setActiveTab: (tab) => set({ activeTab: tab }),
  setCopiedMessageId: (id) => set({ copiedMessageId: id }),
  updateSmartSearchState: (newState) => set((state) => ({
    smartSearch: { ...state.smartSearch, ...newState }
  })),
  addToSearchHistory: (query) => set((state) => {
    const history = state.smartSearch.searchHistory;
    if (query && !history.includes(query)) {
      return {
        smartSearch: {
          ...state.smartSearch,
          searchHistory: [query, ...history.slice(0, 9)] // Keep last 10 searches
        }
      };
    }
    return state;
  }),
  clearSearchHistory: () => set((state) => ({
    smartSearch: { ...state.smartSearch, searchHistory: [] }
  }))
}));