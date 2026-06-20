import { useId, useState } from "react";

interface UploadBoxProps {
  title: string;
  description: string;
  accept: string;
  buttonLabel: string;
  isUploading: boolean;
  onUpload: (file: File) => Promise<void>;
}

export function UploadBox({ title, description, accept, buttonLabel, isUploading, onUpload }: UploadBoxProps) {
  const inputId = useId();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (selectedFile) {
      await onUpload(selectedFile);
      setSelectedFile(null);
      event.currentTarget.reset();
    }
  }

  return (
    <section className="upload-card">
      <div>
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
      <form onSubmit={handleSubmit}>
        <label className="file-drop" htmlFor={inputId}>
          <span>{selectedFile ? selectedFile.name : "Choose a file"}</span>
          <input
            id={inputId}
            type="file"
            accept={accept}
            disabled={isUploading}
            onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
          />
        </label>
        <button type="submit" disabled={!selectedFile || isUploading}>
          {isUploading ? "Uploading..." : buttonLabel}
        </button>
      </form>
    </section>
  );
}
