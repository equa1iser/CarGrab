"use client";

import { SWRConfig } from "swr";
import { ReactNode } from "react";
import { AuthProvider } from "@/lib/auth-context";
import { AuthModal } from "@/components/auth/AuthModal";

export function Providers({ children }: { children: ReactNode }) {
  return (
    <SWRConfig
      value={{
        revalidateOnFocus: false,
        dedupingInterval: 5000,
      }}
    >
      <AuthProvider>
        {children}
        <AuthModal />
      </AuthProvider>
    </SWRConfig>
  );
}
