import { Document } from "@/types/document";
import DocumentCard from "./DocumentCard";

interface DocumentListProps {
  documents: Document[];
}

export default function DocumentList({
  documents,
}: Readonly<DocumentListProps>) {
  if (documents.length === 0) {
    return (
      <div className="py-12 text-center">
        <h2 className="text-2xl font-semibold">
          No documents uploaded
        </h2>

        <p className="mt-2 text-muted-foreground">
          Upload your first document to start using Enterprise RAG.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {documents.map((document) => (
        <DocumentCard
          key={document.id}
          document={document}
        />
      ))}
    </div>
  );
}
