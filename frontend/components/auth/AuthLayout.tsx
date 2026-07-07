export function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-background text-foreground px-4">
      {children}
    </main>
  );
}
