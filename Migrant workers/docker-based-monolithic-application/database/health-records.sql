-- Digital Health Records Database Schema
-- Created for Migrant Workers Health Management System

-- Create database
CREATE DATABASE IF NOT EXISTS health_records;
USE health_records;

-- Workers table - stores basic worker information
CREATE TABLE Workers (
    worker_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    occupation VARCHAR(255) NOT NULL,
    contact VARCHAR(20) NOT NULL,
    relation_name VARCHAR(255) NOT NULL,
    relation_phone VARCHAR(20) NOT NULL,
    relation_type ENUM('Parent', 'Spouse', 'Sibling', 'Child', 'Friend', 'Other') NOT NULL,
    height DECIMAL(5,2) NOT NULL,
    weight DECIMAL(5,2) NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Doctors table - stores doctor information
CREATE TABLE Doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    license_number VARCHAR(50) UNIQUE NOT NULL,
    specialization VARCHAR(255) NOT NULL,
    contact VARCHAR(20) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Admins table - stores admin information
CREATE TABLE Admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- WorkerRecords table - stores medical records for workers
CREATE TABLE WorkerRecords (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    worker_id VARCHAR(10) NOT NULL,
    doctor_id INT,
    record_type VARCHAR(100) DEFAULT 'General Checkup',
    diagnosis TEXT,
    treatment TEXT,
    medications TEXT,
    notes TEXT,
    blood_pressure VARCHAR(20),
    heart_rate INT,
    temperature DECIMAL(4,2),
    weight DECIMAL(5,2),
    height DECIMAL(5,2),
    bmi DECIMAL(4,2) AS (weight / ((height/100) * (height/100))) STORED,
    risk_level ENUM('Low', 'Medium', 'High') DEFAULT 'Low',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (worker_id) REFERENCES Workers(worker_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id) ON DELETE SET NULL
);

-- AccessLogs table - logs all access to worker records
CREATE TABLE AccessLogs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id INT NOT NULL,
    worker_id VARCHAR(10) NOT NULL,
    access_type ENUM('OTP_VERIFIED', 'BREAK_GLASS') NOT NULL,
    reason TEXT,
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    session_duration INT, -- in minutes
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id) ON DELETE CASCADE,
    FOREIGN KEY (worker_id) REFERENCES Workers(worker_id) ON DELETE CASCADE
);

-- OTPVerifications table - manages OTP verification for record access
CREATE TABLE OTPVerifications (
    otp_id INT AUTO_INCREMENT PRIMARY KEY,
    worker_id VARCHAR(10) NOT NULL,
    doctor_id INT NOT NULL,
    otp VARCHAR(6) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP NULL,
    FOREIGN KEY (worker_id) REFERENCES Workers(worker_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id) ON DELETE CASCADE
);

-- Indexes for better performance
CREATE INDEX idx_workers_name ON Workers(name);
CREATE INDEX idx_workers_contact ON Workers(contact);
CREATE INDEX idx_workers_created_at ON Workers(created_at);

CREATE INDEX idx_doctors_email ON Doctors(email);
CREATE INDEX idx_doctors_license ON Doctors(license_number);
CREATE INDEX idx_doctors_specialization ON Doctors(specialization);

CREATE INDEX idx_worker_records_worker_id ON WorkerRecords(worker_id);
CREATE INDEX idx_worker_records_doctor_id ON WorkerRecords(doctor_id);
CREATE INDEX idx_worker_records_created_at ON WorkerRecords(created_at);
CREATE INDEX idx_worker_records_risk_level ON WorkerRecords(risk_level);

CREATE INDEX idx_access_logs_doctor_id ON AccessLogs(doctor_id);
CREATE INDEX idx_access_logs_worker_id ON AccessLogs(worker_id);
CREATE INDEX idx_access_logs_access_time ON AccessLogs(access_time);
CREATE INDEX idx_access_logs_access_type ON AccessLogs(access_type);

CREATE INDEX idx_otp_worker_doctor ON OTPVerifications(worker_id, doctor_id);
CREATE INDEX idx_otp_expires ON OTPVerifications(expires_at);
CREATE INDEX idx_otp_used ON OTPVerifications(used);

-- Sample data insertion
-- Insert sample workers
INSERT INTO Workers (worker_id, name, age, gender, occupation, contact, relation_name, relation_phone, relation_type, height, weight, blood_group, password_hash) VALUES
('MW123456', 'John Smith', 32, 'Male', 'Construction Worker', '+1-555-0101', 'Mary Smith', '+1-555-0102', 'Spouse', 175.50, 78.20, 'O+', '$2b$12$example_hash_1'),
('MW234567', 'Maria Garcia', 28, 'Female', 'Domestic Helper', '+1-555-0201', 'Carlos Garcia', '+1-555-0202', 'Spouse', 162.00, 58.50, 'A+', '$2b$12$example_hash_2'),
('MW345678', 'Ahmad Hassan', 45, 'Male', 'Farm Worker', '+1-555-0301', 'Fatima Hassan', '+1-555-0302', 'Spouse', 168.75, 72.30, 'B+', '$2b$12$example_hash_3'),
('MW456789', 'Li Wei', 38, 'Male', 'Factory Worker', '+1-555-0401', 'Chen Li', '+1-555-0402', 'Parent', 170.25, 65.80, 'AB+', '$2b$12$example_hash_4'),
('MW567890', 'Priya Sharma', 25, 'Female', 'Caregiver', '+1-555-0501', 'Raj Sharma', '+1-555-0502', 'Parent', 158.50, 52.70, 'A-', '$2b$12$example_hash_5');

-- Insert sample doctors
INSERT INTO Doctors (name, email, license_number, specialization, contact, password_hash) VALUES
('Dr. Sarah Johnson', 'sarah.johnson@hospital.com', 'MD123456', 'General Medicine', '+1-555-1001', '$2b$12$doctor_hash_1'),
('Dr. Michael Brown', 'michael.brown@clinic.com', 'MD234567', 'Cardiology', '+1-555-1002', '$2b$12$doctor_hash_2'),
('Dr. Emily Davis', 'emily.davis@healthcare.com', 'MD345678', 'Occupational Medicine', '+1-555-1003', '$2b$12$doctor_hash_3'),
('Dr. James Wilson', 'james.wilson@medical.com', 'MD456789', 'Emergency Medicine', '+1-555-1004', '$2b$12$doctor_hash_4');

-- Insert sample admins
INSERT INTO Admins (name, email, role, department, password_hash) VALUES
('Admin User', 'admin@healthrecords.com', 'System Administrator', 'IT Department', '$2b$12$admin_hash_1'),
('Healthcare Supervisor', 'supervisor@healthrecords.com', 'Healthcare Supervisor', 'Medical Department', '$2b$12$admin_hash_2');

-- Insert sample medical records
INSERT INTO WorkerRecords (worker_id, doctor_id, record_type, diagnosis, treatment, medications, notes, blood_pressure, heart_rate, temperature, weight, height, risk_level) VALUES
('MW123456', 1, 'General Checkup', 'Hypertension', 'Lifestyle modification', 'Lisinopril 10mg', 'Patient advised to reduce salt intake and exercise regularly', '140/90', 78, 98.6, 78.20, 175.50, 'Medium'),
('MW234567', 2, 'Cardiac Consultation', 'Heart Murmur', 'Monitoring', 'None', 'Functional heart murmur, no treatment required', '120/80', 72, 98.4, 58.50, 162.00, 'Low'),
('MW345678', 3, 'Occupational Health', 'Back Strain', 'Physical Therapy', 'Ibuprofen 400mg', 'Work-related back injury, recommended ergonomic adjustments', '130/85', 80, 98.7, 72.30, 168.75, 'Medium'),
('MW456789', 1, 'Respiratory Check', 'Chronic Cough', 'Investigation', 'Cough suppressant', 'Chronic cough investigation ongoing, chest X-ray ordered', '125/82', 75, 98.5, 65.80, 170.25, 'Medium'),
('MW567890', 4, 'Emergency Visit', 'Minor Cut', 'Wound Care', 'Antibiotic ointment', 'Minor laceration treated and dressed', '115/75', 68, 98.3, 52.70, 158.50, 'Low');

-- Insert sample access logs
INSERT INTO AccessLogs (doctor_id, worker_id, access_type, reason, access_time) VALUES
(1, 'MW123456', 'OTP_VERIFIED', 'Routine follow-up consultation', '2024-01-15 10:30:00'),
(2, 'MW234567', 'OTP_VERIFIED', 'Cardiac consultation', '2024-01-16 14:15:00'),
(3, 'MW345678', 'BREAK_GLASS', 'Emergency workplace injury', '2024-01-17 09:45:00'),
(4, 'MW567890', 'BREAK_GLASS', 'Emergency room treatment', '2024-01-18 16:20:00'),
(1, 'MW456789', 'OTP_VERIFIED', 'Respiratory examination', '2024-01-19 11:00:00');

-- Insert sample OTP verifications (some used, some expired)
INSERT INTO OTPVerifications (worker_id, doctor_id, otp, expires_at, used, used_at) VALUES
('MW123456', 1, '123456', '2024-01-15 10:40:00', TRUE, '2024-01-15 10:35:00'),
('MW234567', 2, '234567', '2024-01-16 14:25:00', TRUE, '2024-01-16 14:18:00'),
('MW456789', 1, '345678', '2024-01-19 11:10:00', TRUE, '2024-01-19 11:02:00');

-- Views for common queries
-- View for worker summary
CREATE VIEW WorkerSummary AS
SELECT 
    w.worker_id,
    w.name,
    w.age,
    w.gender,
    w.occupation,
    w.blood_group,
    w.created_at as registration_date,
    COUNT(wr.record_id) as total_records,
    MAX(wr.created_at) as last_visit,
    wr.risk_level as current_risk_level
FROM Workers w
LEFT JOIN WorkerRecords wr ON w.worker_id = wr.worker_id
GROUP BY w.worker_id, wr.risk_level;

-- View for doctor activity
CREATE VIEW DoctorActivity AS
SELECT 
    d.doctor_id,
    d.name as doctor_name,
    d.specialization,
    COUNT(DISTINCT al.worker_id) as patients_treated,
    COUNT(al.log_id) as total_access,
    SUM(CASE WHEN al.access_type = 'BREAK_GLASS' THEN 1 ELSE 0 END) as emergency_access,
    MAX(al.access_time) as last_activity
FROM Doctors d
LEFT JOIN AccessLogs al ON d.doctor_id = al.doctor_id
GROUP BY d.doctor_id;

-- View for emergency access monitoring
CREATE VIEW EmergencyAccessMonitor AS
SELECT 
    al.log_id,
    al.access_time,
    d.name as doctor_name,
    d.specialization,
    w.name as worker_name,
    w.worker_id,
    al.reason,
    al.ip_address
FROM AccessLogs al
JOIN Doctors d ON al.doctor_id = d.doctor_id
JOIN Workers w ON al.worker_id = w.worker_id
WHERE al.access_type = 'BREAK_GLASS'
ORDER BY al.access_time DESC;

-- Triggers for audit and security
DELIMITER $$

-- Trigger to log worker record changes
CREATE TRIGGER audit_worker_records 
AFTER INSERT ON WorkerRecords
FOR EACH ROW
BEGIN
    INSERT INTO AccessLogs (doctor_id, worker_id, access_type, reason, access_time)
    VALUES (NEW.doctor_id, NEW.worker_id, 'OTP_VERIFIED', 'Medical record created', NOW());
END$$

-- Trigger to automatically expire old OTPs
CREATE TRIGGER cleanup_expired_otps
AFTER INSERT ON OTPVerifications
FOR EACH ROW
BEGIN
    DELETE FROM OTPVerifications 
    WHERE expires_at < NOW() 
    AND used = FALSE;
END$$

DELIMITER ;

-- Stored procedures for common operations
DELIMITER $$

-- Procedure to get worker health summary
CREATE PROCEDURE GetWorkerHealthSummary(IN p_worker_id VARCHAR(10))
BEGIN
    SELECT 
        w.*,
        wr.record_type,
        wr.diagnosis,
        wr.risk_level,
        wr.created_at as last_checkup,
        COUNT(al.log_id) as total_access
    FROM Workers w
    LEFT JOIN WorkerRecords wr ON w.worker_id = wr.worker_id
    LEFT JOIN AccessLogs al ON w.worker_id = al.worker_id
    WHERE w.worker_id = p_worker_id
    GROUP BY w.worker_id, wr.record_id
    ORDER BY wr.created_at DESC;
END$$

-- Procedure to validate OTP
CREATE PROCEDURE ValidateOTP(
    IN p_worker_id VARCHAR(10),
    IN p_doctor_id INT,
    IN p_otp VARCHAR(6),
    OUT p_valid BOOLEAN
)
BEGIN
    DECLARE otp_count INT DEFAULT 0;
    
    SELECT COUNT(*) INTO otp_count
    FROM OTPVerifications
    WHERE worker_id = p_worker_id
    AND doctor_id = p_doctor_id
    AND otp = p_otp
    AND expires_at > NOW()
    AND used = FALSE;
    
    IF otp_count > 0 THEN
        UPDATE OTPVerifications
        SET used = TRUE, used_at = NOW()
        WHERE worker_id = p_worker_id
        AND doctor_id = p_doctor_id
        AND otp = p_otp;
        
        SET p_valid = TRUE;
    ELSE
        SET p_valid = FALSE;
    END IF;
END$$

-- Procedure to get system statistics
CREATE PROCEDURE GetSystemStats()
BEGIN
    SELECT 
        (SELECT COUNT(*) FROM Workers WHERE is_active = TRUE) as total_workers,
        (SELECT COUNT(*) FROM Doctors WHERE is_active = TRUE) as total_doctors,
        (SELECT COUNT(*) FROM Admins WHERE is_active = TRUE) as total_admins,
        (SELECT COUNT(DISTINCT worker_id) FROM WorkerRecords) as workers_with_records,
        (SELECT COUNT(*) FROM AccessLogs WHERE access_type = 'BREAK_GLASS' AND DATE(access_time) = CURDATE()) as today_emergency_access,
        (SELECT COUNT(*) FROM AccessLogs WHERE DATE(access_time) = CURDATE()) as today_total_access;
END$$

DELIMITER ;

-- Grant permissions (adjust as needed for your environment)
-- CREATE USER 'health_app'@'localhost' IDENTIFIED BY 'secure_password';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON health_records.* TO 'health_app'@'localhost';
-- FLUSH PRIVILEGES;

-- Final verification queries
SELECT 'Database setup completed successfully!' as Status;
SELECT COUNT(*) as Total_Workers FROM Workers;
SELECT COUNT(*) as Total_Doctors FROM Doctors;
SELECT COUNT(*) as Total_Records FROM WorkerRecords;
SELECT COUNT(*) as Total_Access_Logs FROM AccessLogs;