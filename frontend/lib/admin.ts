import { api } from "@/lib/api";

// ── Types ──────────────────────────────────────────────────────────────────────

export interface DashboardStats {
  users: number;
  documents: number;
  sessions: number;
  messages: number;
  database: string;
  ollama: string;
  status: string;
}

export interface AdminUser {
  id: string;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

// ── Dashboard ──────────────────────────────────────────────────────────────────

export async function getDashboard(): Promise<DashboardStats> {
  const res = await api.get<DashboardStats>("/admin/dashboard");
  return res.data;
}

// ── User Management ────────────────────────────────────────────────────────────

export async function getUsers(): Promise<AdminUser[]> {
  const res = await api.get<AdminUser[]>("/admin/users");
  return res.data;
}

export async function promoteUser(id: string): Promise<AdminUser> {
  const res = await api.put<AdminUser>(`/admin/users/${id}/promote`);
  return res.data;
}

export async function demoteUser(id: string): Promise<AdminUser> {
  const res = await api.put<AdminUser>(`/admin/users/${id}/demote`);
  return res.data;
}

export async function deleteUser(id: string): Promise<void> {
  await api.delete(`/admin/users/${id}`);
}

// ── Document Management ────────────────────────────────────────────────────────

export interface AdminDocument {
  id: string;
  filename: string;
  status: string;
  uploaded_at: string;
  file_path: string;
  user: {
    email: string;
    name: string;
  };
}

export async function getDocuments(): Promise<AdminDocument[]> {
  const res = await api.get<AdminDocument[]>("/admin/documents");
  return res.data;
}

export async function deleteDocument(id: string): Promise<void> {
  await api.delete(`/admin/documents/${id}`);
}

export async function reindexDocument(id: string): Promise<void> {
  await api.post(`/admin/documents/${id}/reindex`);
}

// ── Session Management ─────────────────────────────────────────────────────────

export interface AdminSession {
  id: string;
  title: string;
  owner: string;
  created_at: string;
  message_count: number;
}

export interface AdminMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export async function getSessions(): Promise<AdminSession[]> {
  const res = await api.get<AdminSession[]>("/admin/sessions");
  return res.data;
}

export async function getSession(id: string): Promise<AdminMessage[]> {
  const res = await api.get<AdminMessage[]>(`/admin/sessions/${id}`);
  return res.data;
}

export async function deleteSession(id: string): Promise<void> {
  await api.delete(`/admin/sessions/${id}`);
}
