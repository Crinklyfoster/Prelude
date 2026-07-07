import { api } from "@/lib/api";
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
} from "@/types/auth";

export async function login(
  data: LoginRequest,
): Promise<TokenResponse> {
  const response = await api.post<TokenResponse>("/auth/login", data);
  return response.data;
}

export async function register(
  data: RegisterRequest,
): Promise<User> {
  const response = await api.post<User>("/auth/register", data);
  return response.data;
}

export async function getCurrentUser(): Promise<User> {
  const response = await api.get<User>("/auth/me");
  return response.data;
}





