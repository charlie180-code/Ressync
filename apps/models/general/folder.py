from datetime import datetime
from ... import db

class Folder(db.Model):
    __tablename__ = 'folders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    unique_id = db.Column(db.BigInteger, unique=True, index=True, nullable=True)
    description = db.Column(db.Text)
    type = db.Column(db.String)
    status = db.Column(db.Boolean, default=True)
    folder_number = db.Column(db.String(5), unique=True)
    client = db.Column(db.String)
    deadline = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    files = db.relationship('File', backref='folder', lazy=True)

    # Logistics-specific fields
    transport = db.Column(db.String)
    weight = db.Column(db.String)
    bills_of_ladding = db.Column(db.String)

    # Public Works and
    project_location = db.Column(db.String)
    project_manager = db.Column(db.String)
    project_phase = db.Column(db.String)  # Ex: "Design", "Construction", "Finalization"
    budget = db.Column(db.String)
    contractor = db.Column(db.String)
    materials_used = db.Column(db.Text)
    permits_approved = db.Column(db.Boolean, default=False)

    # Electricity-specific fields
    voltage = db.Column(db.String)  # Operating voltage of the project
    current = db.Column(db.String)  # Current requirements
    circuit_diagram = db.Column(db.String)  # Path to the circuit diagram file
    compliance_standards = db.Column(db.String)  # Compliance with electrical standards

    # Plumbing-specific fields
    pipe_material = db.Column(db.String)  # Material of the pipes used (e.g., PVC, copper)
    water_pressure = db.Column(db.String)  # Water pressure specifications
    plumbing_diagram = db.Column(db.String)  # Path to the plumbing system diagram

    # Electronics-specific fields
    pcb_layout = db.Column(db.String)  # Path to PCB layout file
    components_list = db.Column(db.String)  # List of electronic components used
    firmware_version = db.Column(db.String)  # Firmware version for the electronic device

    # Biology-specific fields
    species_studied = db.Column(db.String)  # Species under study or experiment
    experiment_date = db.Column(db.DateTime)  # Date of the experiment
    lab_technician = db.Column(db.String)  # Name of the lab technician responsible
    sample_storage = db.Column(db.String)  # Location or method of sample storage
    biosafety_level = db.Column(db.Integer)  # Biosafety level of the lab

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))