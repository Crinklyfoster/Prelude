import { api } from "@/lib/api";
import {
  Document,
  UploadDocumentResponse,
} from "@/types/document";

export async function getDocuments(): Promise<Document[]> {
  const response = await api.get<Document[]>("/documents");
  return response.data;
}

export async function getDocument(
  documentId: string
): Promise<Document> {
  const response = await api.get<Document>(
    `/documents/${documentId}`
  );

  return response.data;
}

export async function uploadDocument(
  file: File
): Promise<UploadDocumentResponse> {
  const formData = new FormData();

  formData.append("file", file);

  const response = await api.post<UploadDocumentResponse>(
    "/documents/upload",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
}

export async function deleteDocument(
  documentId: string
) {
  const response = await api.delete(
    `/documents/${documentId}`
  );

  return response.data;
}
