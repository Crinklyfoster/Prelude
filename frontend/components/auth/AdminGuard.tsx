"use client";

import { ReactNode, useEffect } from "react";
import { useRouter } from "next/navigation";

import { Loading } from "@/components/ui/loading";
import { useAuth } from "@/lib/auth-provider";

export default function AdminGuard({
  children,
}: {
  children: ReactNode;
}) {
  const router = useRouter();

  const {
    loading,
    isAuthenticated,
    user,
  } = useAuth();

  useEffect(() => {
    if (loading) return;

    if (!isAuthenticated) {
      router.replace("/login");
      return;
    }

    if (user?.role !== "admin") {
      router.replace("/");
    }
  }, [loading, isAuthenticated, user, router]);

  if (loading) {
    return <Loading />;
  }

  if (!isAuthenticated) {
    return null;
  }

  if (user?.role !== "admin") {
    return null;
  }

  return <>{children}</>;
}
