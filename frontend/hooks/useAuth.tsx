"use client";

import { createContext, useContext, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";
import {
  useAuthStore,
  selectIsAdmin,
  selectIsOwner,
  selectIsInternal,
  selectIsCustomer,
  selectCanCreateProject,
  selectCanDeleteProject,
  selectCanUpload
} from "../lib/stores/auth-store";
import { apiFetch } from "../lib/api/config";

export type UserRole = "owner" | "admin" | "internal" | "customer";

export interface User {
  id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  role: UserRole;
  organization_id?: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: () => void;
  logout: () => void;
  isAdmin: boolean;
  isOwner: boolean;
  isInternal: boolean;
  isCustomer: boolean;
  canCreateProject: boolean;
  canDeleteProject: boolean;
  canUpload: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: () => { },
  logout: () => { },
  isAdmin: false,
  isOwner: false,
  isInternal: false,
  isCustomer: false,
  canCreateProject: false,
  canDeleteProject: false,
  canUpload: false,
});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const router = useRouter();

  // Use Zustand store with selectors
  const user = useAuthStore((state) => state.user);
  const isLoading = useAuthStore((state) => state.loading);
  const setUser = useAuthStore((state) => state.setUser);
  const setLoading = useAuthStore((state) => state.setLoading);
  const clearUser = useAuthStore((state) => state.logout);

  // Use derived selectors from store
  const isAdmin = useAuthStore(selectIsAdmin) ?? false;
  const isOwner = useAuthStore(selectIsOwner) ?? false;
  const isInternal = useAuthStore(selectIsInternal) ?? false;
  const isCustomer = useAuthStore(selectIsCustomer) ?? false;
  const canCreateProject = useAuthStore(selectCanCreateProject);
  const canDeleteProject = useAuthStore(selectCanDeleteProject);
  const canUpload = useAuthStore(selectCanUpload);

  useEffect(() => {
    checkUser();
  }, []);

  const checkUser = async () => {
    try {
      setLoading(true);
      const userData = await apiFetch<User>("/api/auth/me");
      setUser(userData);
    } catch (error) {
      console.error("Auth check failed:", error);
      clearUser();
    }
  };

  const login = () => {
    router.push("/login");
  };

  const logout = async () => {
    clearUser();
    router.push("/login");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading: isLoading,
        login,
        logout,
        isAdmin,
        isOwner,
        isInternal,
        isCustomer,
        canCreateProject,
        canDeleteProject,
        canUpload,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
