-- Database: DengueTrackingSystem
CREATE DATABASE IF NOT EXISTS DengueTrackingSystem;
USE DengueTrackingSystem;

-- 1. PATIENTS TABLE
CREATE TABLE Patients (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    national_id VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    age INT,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    blood_type ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'),
    phone_number VARCHAR(15) NOT NULL,
    email VARCHAR(100),
    emergency_contact VARCHAR(15),
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_name (first_name, last_name),
    INDEX idx_phone (phone_number),
    INDEX idx_national_id (national_id)
);

-- 2. ADDRESSES TABLE
CREATE TABLE Addresses (
    address_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    address_type ENUM('Permanent', 'Current', 'Work') DEFAULT 'Current',
    street_address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    division VARCHAR(100),
    postal_code VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    is_primary BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE,
    INDEX idx_location (district, city),
    INDEX idx_patient (patient_id)
);

-- 3. DENGUE DETAILS TABLE
CREATE TABLE DengueDetails (
    dengue_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT UNIQUE NOT NULL,
    diagnosis_date DATE NOT NULL,
    dengue_type ENUM('Classic', 'Hemorrhagic', 'Shock Syndrome') NOT NULL,
    severity_level ENUM('Mild', 'Moderate', 'Severe', 'Critical') NOT NULL,
    infection_source ENUM('Local', 'Travel', 'Unknown'),
    travel_history TEXT,
    hospitalization_required BOOLEAN DEFAULT FALSE,
    icu_admission BOOLEAN DEFAULT FALSE,
    platelet_count INT,
    hematocrit_level DECIMAL(4,2),
    warning_signs TEXT,
    outcome ENUM('Recovered', 'Under Treatment', 'Referred', 'Death') DEFAULT 'Under Treatment',
    follow_up_date DATE,
    notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE,
    INDEX idx_severity (severity_level),
    INDEX idx_diagnosis_date (diagnosis_date),
    INDEX idx_outcome (outcome)
);

-- 4. HOSPITALS TABLE
CREATE TABLE Hospitals (
    hospital_id INT PRIMARY KEY AUTO_INCREMENT,
    hospital_name VARCHAR(200) NOT NULL,
    hospital_type ENUM('Government', 'Private', 'Clinic', 'Specialized') NOT NULL,
    address TEXT,
    city VARCHAR(100),
    district VARCHAR(100),
    contact_number VARCHAR(20),
    total_beds INT,
    icu_beds INT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    INDEX idx_hospital_district (district),
    INDEX idx_hospital_type (hospital_type)
);

-- 5. TREATMENTS TABLE
CREATE TABLE Treatments (
    treatment_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    hospital_id INT,
    admission_date DATE NOT NULL,
    discharge_date DATE,
    treatment_type ENUM('Outpatient', 'Inpatient', 'ICU') NOT NULL,
    doctor_name VARCHAR(100),
    initial_diagnosis TEXT,
    prescribed_medications TEXT,
    iv_fluid_required BOOLEAN DEFAULT FALSE,
    blood_transfusion BOOLEAN DEFAULT FALSE,
    platelet_transfusion BOOLEAN DEFAULT FALSE,
    treatment_cost DECIMAL(10,2),
    treatment_notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (hospital_id) REFERENCES Hospitals(hospital_id),
    INDEX idx_treatment_dates (admission_date, discharge_date),
    INDEX idx_patient_treatment (patient_id)
);

-- 6. LAB TESTS TABLE
CREATE TABLE LabTests (
    test_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    test_date DATE NOT NULL,
    test_type ENUM('NS1 Antigen', 'IgM Antibody', 'IgG Antibody', 'PCR', 'Complete Blood Count', 'Platelet Count') NOT NULL,
    test_result ENUM('Positive', 'Negative', 'Inconclusive') NOT NULL,
    result_value VARCHAR(50),
    normal_range VARCHAR(50),
    lab_name VARCHAR(200),
    technician_name VARCHAR(100),
    notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE,
    INDEX idx_test_type (test_type),
    INDEX idx_test_date (test_date),
    INDEX idx_patient_test (patient_id)
);

-- 7. CONTACT TRACING TABLE
CREATE TABLE ContactTracing (
    trace_id INT PRIMARY KEY AUTO_INCREMENT,
    infected_patient_id INT NOT NULL,
    contact_patient_id INT,
    contact_name VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(15),
    contact_relation ENUM('Family', 'Colleague', 'Neighbor', 'Friend', 'Other'),
    exposure_date DATE,
    exposure_location VARCHAR(255),
    exposure_duration_hours INT,
    contact_status ENUM('Monitored', 'Tested', 'Positive', 'Negative', 'Quarantined'),
    FOREIGN KEY (infected_patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (contact_patient_id) REFERENCES Patients(patient_id) ON DELETE SET NULL,
    INDEX idx_contact_tracing (infected_patient_id, contact_status)
);

-- 8. DAILY MONITORING TABLE
CREATE TABLE DailyMonitoring (
    monitor_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    monitor_date DATE NOT NULL,
    temperature DECIMAL(4,2),
    blood_pressure VARCHAR(20),
    platelet_count INT,
    hematocrit DECIMAL(4,2),
    urine_output VARCHAR(50),
    respiratory_rate INT,
    oxygen_saturation DECIMAL(4,2),
    pain_level INT CHECK (pain_level BETWEEN 0 AND 10),
    symptoms_status TEXT,
    nurse_notes TEXT,
    doctor_notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE,
    UNIQUE KEY unique_daily_monitor (patient_id, monitor_date),
    INDEX idx_monitor_date (monitor_date),
    INDEX idx_patient_monitoring (patient_id)
);

-- 9. USERS TABLE
CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('Admin', 'Doctor', 'Nurse', 'Field Worker', 'Data Entry') NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(15),
    hospital_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES Hospitals(hospital_id),
    INDEX idx_user_role (role)
);

-- Insert Sample Data
INSERT INTO Hospitals (hospital_name, hospital_type, city, district, contact_number, total_beds, icu_beds) VALUES
('Dhaka Medical College Hospital', 'Government', 'Dhaka', 'Dhaka', '02-9660015', 2000, 50),
('Bangabandhu Sheikh Mujib Medical University', 'Government', 'Dhaka', 'Dhaka', '02-8616644', 1000, 30),
('Square Hospitals Ltd', 'Private', 'Dhaka', 'Dhaka', '02-8144400', 500, 20),
('Chittagong Medical College Hospital', 'Government', 'Chittagong', 'Chittagong', '031-619344', 1200, 25),
('Rajshahi Medical College Hospital', 'Government', 'Rajshahi', 'Rajshahi', '0721-761001', 1000, 15);

-- Insert Admin User (password: admin123)
INSERT INTO Users (username, password_hash, full_name, role, email) VALUES
('admin', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'System Administrator', 'Admin', 'admin@dengue.gov');

-- Create Views for Reporting
CREATE VIEW DenguePatientSummary AS
SELECT
    p.patient_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    p.age,
    p.gender,
    p.blood_type,
    p.phone_number,
    a.district,
    a.city,
    d.diagnosis_date,
    d.dengue_type,
    d.severity_level,
    d.outcome,
    t.admission_date,
    t.treatment_type,
    h.hospital_name
FROM Patients p
LEFT JOIN DengueDetails d ON p.patient_id = d.patient_id
LEFT JOIN Addresses a ON p.patient_id = a.patient_id AND a.is_primary = TRUE
LEFT JOIN Treatments t ON p.patient_id = t.patient_id AND t.discharge_date IS NULL
LEFT JOIN Hospitals h ON t.hospital_id = h.hospital_id
WHERE d.patient_id IS NOT NULL;

CREATE VIEW DengueDistrictStats AS
SELECT
    a.district,
    COUNT(DISTINCT p.patient_id) AS total_cases,
    SUM(CASE WHEN d.severity_level = 'Critical' THEN 1 ELSE 0 END) AS critical_cases,
    SUM(CASE WHEN d.severity_level = 'Severe' THEN 1 ELSE 0 END) AS severe_cases,
    SUM(CASE WHEN d.outcome = 'Death' THEN 1 ELSE 0 END) AS deaths,
    MIN(d.diagnosis_date) AS first_case_date,
    MAX(d.diagnosis_date) AS latest_case_date
FROM Patients p
JOIN DengueDetails d ON p.patient_id = d.patient_id
JOIN Addresses a ON p.patient_id = a.patient_id AND a.is_primary = TRUE
GROUP BY a.district
ORDER BY total_cases DESC;