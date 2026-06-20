interface JobStatusCardProps {
  label: string;
  value: string | number;
  helper: string;
}

export function JobStatusCard({ label, value, helper }: JobStatusCardProps) {
  return (
    <article className="stat-card">
      <p>{label}</p>
      <strong>{value}</strong>
      <span>{helper}</span>
    </article>
  );
}
