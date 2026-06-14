export interface Document {
  id: string;
  filename: string;
  file_path: string;
  status: string;
  uploaded_at: string;
}

export interface UploadDocumentResponse {
  document_id: string;
  filename: string;
  status: string;
}