"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";

import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { toast } from "sonner";

import { useAuth } from "@/lib/auth-provider";

const registerSchema = z.object({
  name: z.string().min(2, "Name must contain at least 2 characters"),
  email: z.email("Invalid email address"),
  password: z.string().min(8, "Password must contain at least 8 characters"),
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export function RegisterForm() {
  const router = useRouter();

  const {
    register: registerUser,
    loading: authLoading,
    isAuthenticated,
  } = useAuth();

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.replace("/chat");
    }
  }, [authLoading, isAuthenticated, router]);

  const [formLoading, setFormLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
  });

  async function onSubmit(data: RegisterFormValues) {
    setFormLoading(true);

    try {
      await registerUser(data.name, data.email, data.password);

      toast.success("Account created successfully.");
      router.push("/chat");
    } catch {
      toast.error("Unable to create account.");
    } finally {
      setFormLoading(false);
    }
  }

  return (
    <div className="w-full max-w-md rounded-xl border border-border bg-card p-8 shadow-lg">
      <h1 className="mb-6 text-center text-2xl font-bold">
        Prelude
      </h1>

      <form
        onSubmit={handleSubmit(onSubmit)}
        className="space-y-5"
      >
        <div>
          <label htmlFor="name" className="mb-1 block text-sm font-medium">Name</label>
          <input
            id="name"
            {...register("name")}
            className="w-full rounded-md border border-border bg-background p-2 text-foreground outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-500">
              {errors.name.message}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="email" className="mb-1 block text-sm font-medium">Email</label>
          <input
            id="email"
            type="email"
            {...register("email")}
            className="w-full rounded-md border border-border bg-background p-2 text-foreground outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.email && (
            <p className="mt-1 text-sm text-red-500">
              {errors.email.message}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="password" className="mb-1 block text-sm font-medium">Password</label>
          <input
            id="password"
            type="password"
            {...register("password")}
            className="w-full rounded-md border border-border bg-background p-2 text-foreground outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.password && (
            <p className="mt-1 text-sm text-red-500">
              {errors.password.message}
            </p>
          )}
        </div>

        <button
          type="submit"
          disabled={formLoading}
          className="w-full rounded-md bg-blue-600 py-2 text-white transition hover:bg-blue-700 disabled:opacity-50"
        >
          {formLoading ? "Creating Account..." : "Create Account"}
        </button>
      </form>

      <p className="mt-6 text-center text-sm">
        Already have an account?{" "}
        <Link
          href="/login"
          className="font-medium text-blue-600 hover:underline"
        >
          Login
        </Link>
      </p>
    </div>
  );
}

