from .extensions import db, bcrypt, UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    __tablename__ = "users"

    user_email = db.Column(db.String(120), primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # Relationships
    batches = db.relationship("Batch", backref="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def get_id(self):
        return self.user_email


class Batch(db.Model):
    __tablename__ = "batches"

    batch_id = db.Column(db.Integer, primary_key=True)
    batch_name = db.Column(db.String(100), nullable=False)
    student_count = db.Column(db.Integer, nullable=False)

    user_email = db.Column(
        db.String(120), db.ForeignKey("users.user_email"), nullable=False
    )

    # Relationships
    attendances = db.relationship(
        "Attendance", backref="batch", cascade="all, delete-orphan"
    )

    def to_json(self):
        return {
            "batch_id": self.batch_id,
            "batch_name": self.batch_name,
            "student_count": self.student_count,
        }


class Attendance(db.Model):
    __tablename__ = "attendances"

    attendance_id = db.Column(db.Integer, primary_key=True)
    attendance_date = db.Column(db.Date, default=datetime.now().date, nullable=False)

    batch_id = db.Column(db.Integer, db.ForeignKey("batches.batch_id"), nullable=False)

    # Relationships
    records = db.relationship(
        "AttendanceRecord", backref="attendance", cascade="all, delete-orphan"
    )


class AttendanceRecord(db.Model):
    __tablename__ = "attendance_records"

    record_id = db.Column(db.Integer, primary_key=True)
    roll_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)

    attendance_id = db.Column(
        db.Integer, db.ForeignKey("attendances.attendance_id"), nullable=False
    )
