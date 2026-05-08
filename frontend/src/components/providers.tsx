"use client";

import { SWRConfig } from "swr";
import { ReactNode } from "react";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { AuthProvider } from "@/lib/auth-context";
import { AuthModal } from "@/components/auth/AuthModal";

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID ?? "";

export function Providers({ children }: { children: ReactNode }) {
  return (
    <SWRConfig value={{ revalidateOnFocus: false, dedupingInterval: 5000 }}>
      <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
        <AuthProvider>
          {children}
          <AuthModal />
        </AuthProvider>
      </GoogleOAuthProvider>
    </SWRConfig>
  );
}
