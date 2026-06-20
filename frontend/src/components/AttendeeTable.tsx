import type { Attendee } from "../types/attendee";

interface AttendeeTableProps {
  attendees: Attendee[];
}

export function AttendeeTable({ attendees }: AttendeeTableProps) {
  if (attendees.length === 0) {
    return <p className="muted">Upload an attendee file to preview validated rows.</p>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Row</th>
            <th>Name</th>
            <th>Email</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {attendees.map((attendee) => (
            <tr key={attendee.id}>
              <td>{attendee.original_row_number}</td>
              <td>{attendee.full_name || "Missing"}</td>
              <td>{attendee.email || "Not provided"}</td>
              <td>
                <span className={attendee.is_valid ? "status valid" : "status invalid"}>
                  {attendee.is_valid ? "Valid" : attendee.validation_error}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
