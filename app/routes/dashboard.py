from flask import Blueprint, render_template, request
from ..models import Batch, Attendance, AttendanceRecord
from ..extensions import db, login_required, current_user

dashboard_bp = Blueprint("dashboard_bp", __name__, template_folder="../templates")


@dashboard_bp.route("/")
@login_required
def dashboard():
    batches = Batch.query.filter_by(user_email=current_user.user_email).all()
    batches_json = [b.to_json() for b in batches]

    for batch in batches_json:
        attendaces = Attendance.query.filter_by(batch_id=batch["batch_id"]).all()
        students = {r: 0 for r in range(1, batch["student_count"] + 1)}

        for a in attendaces:
            attendace_records = AttendanceRecord.query.filter_by(
                attendance_id=a.attendance_id
            ).all()
            for ar in attendace_records:
                students[ar.roll_number] += 1 if ar.status else 0

        sessions_count = len(attendaces)
        if sessions_count != 0:
            average_attendance = (
                sum(students.values()) / sessions_count / len(students)
            ) * 100
        else:
            average_attendance = 0

        batch["average_attendance"] = average_attendance
        batch["sessions_count"] = sessions_count

    return render_template("dashboard.html", batches=batches_json)


@dashboard_bp.route("/batch", methods=["GET", "POST"])
@login_required
def batch():
    batch_id = request.args.get("batch_id")
    batch = Batch.query.get(batch_id)

    if not batch:
        return {"message": "BATCH NOT FOUND"}

    if batch.user_email != current_user.user_email:
        return {"message": "USER INVALID"}, 409

    attendaces = Attendance.query.filter_by(batch_id=batch_id).all()

    students = {r: 0 for r in range(1, batch.student_count + 1)}

    for a in attendaces:
        attendace_records = AttendanceRecord.query.filter_by(
            attendance_id=a.attendance_id
        ).all()
        for ar in attendace_records:
            students[ar.roll_number] += 1 if ar.status else 0

    sessions_count = len(attendaces)
    if sessions_count != 0:
        average_attendance = (
            sum(students.values()) / sessions_count / len(students)
        ) * 100
    else:
        average_attendance = 0

    return render_template(
        "batch.html",
        batch=batch.to_json(),
        students=students,
        sessions_count=sessions_count,
        average_attendance=average_attendance,
    )


@dashboard_bp.route("/batch/new", methods=["POST"])
@login_required
def new_batch():
    batch_name = request.form.get("name")
    student_count = request.form.get("student_count")

    batch = Batch(
        batch_name=batch_name,
        student_count=student_count,
        user_email=current_user.user_email,
    )
    db.session.add(batch)
    db.session.commit()

    return {"message": "BATCH NEW SUCCESS"}, 200


@dashboard_bp.route("/batch/delete", methods=["POST"])
@login_required
def delete_batch():
    batch_id = request.args.get("batch_id")

    batch = Batch.query.get(batch_id)
    if batch.user_email == current_user.user_email:
        db.session.delete(batch)
        db.session.commit()
        return {"message": "BATCH DELETE SUCCESS"}, 200
    else:
        return {"message": "BATCH DELETE FAILED - USER INVALID"}, 409


@dashboard_bp.route("/batch/attendance", methods=["POST"])
@login_required
def mark_attendance():
    data = request.get_json()

    batch_id = data.get("batch_id")
    attendance_status = data.get("attendance_status")

    batch = Batch.query.get(batch_id)

    if batch.user_email != current_user.user_email:
        return {"message": "ATTENDANCE MARK FAILED - USER INVALID"}, 409

    attendance = Attendance(batch_id=batch_id)
    db.session.add(attendance)
    db.session.commit()

    for r, s in attendance_status.items():
        attendance_record = AttendanceRecord(
            roll_number=int(r),
            status=1 if s else 0,
            attendance_id=attendance.attendance_id,
        )
        db.session.add(attendance_record)

    db.session.commit()

    return {"message": "ATTENDANCE MARK SUCCESS"}, 200
