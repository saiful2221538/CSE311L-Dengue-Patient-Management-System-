# CSE311L(Dengue Patient Management System)

An enterprise-grade, data-driven web application designed to track, monitor, and manage dengue outbreaks and patient care effectively. Built as part of the **CSE311L (Database Management Systems Laboratory)** curriculum, this system provides healthcare professionals and administrators with real-time analytics, automated clinical severity scaling, patient tracking, contact tracing, and daily vital monitoring.

---

## 🚀 Key Features

* **Comprehensive Patient Registration & Profiling:** Captures complete patient demographics, national IDs, custom automated age calculations, and localized primary/secondary addresses.
* **Dynamic Epidemiological Statistics:** Track live metrics including total active cases, critical/severe incidents, and recovery statuses. Includes a fallback demo mechanism to ensure high availability.
* **Clinical Lab & Progress Tracking:** Record diagnostic metrics such as NS1 Antigen, IgM/IgG antibodies, and continuous platelet tracking.
* **Automated Severity Scaling:** The backend dynamically updates patient clinical severity flags (`Mild`, `Moderate`, `Severe`, `Critical`) in real-time based on fluctuating laboratory platelet values:
* **Critical:** $< 20,000 / \mu L$
* **Severe:** $< 50,000 / \mu L$
* **Moderate:** $< 100,000 / \mu L$
* **Mild:** $\ge 100,000 / \mu L$


* **Contact Tracing Network:** Built-in vector exposure monitoring to isolate geographical cluster outbreaks and manage high-risk relations (Family, Colleagues, Neighbors).
* **Daily Ward Monitoring:** Captures point-in-time nursing logs including multi-point diagnostics (spO2, Blood Pressure, Hematocrit levels, Temperature, and Pain Scale metrics).

---

## 🛠️ System Architecture & Tech Stack

The application is structured around a decoupled relational database schema interacting seamlessly with a micro-backend service pipeline:

### Tech Stack

* **Backend Framework:** Python Flask
* **Database ORM Engine:** Flask-SQLAlchemy (SQLAlchemy 2.x compatible)
* **Database Driver:** PyMySQL
* **Relational Database:** MySQL (Optimized for XAMPP / Local standalone environments)
* **Security:** Werkzeug (Cryptographic SHA256 Password Hashing)
* **Frontend Routing:** Flask Static Server Engine (serves decoupled client architectures)

### Database Schema Layout

The relational schema leverages strongly-typed definitions, clustered/non-clustered indexing for lightning-fast queries, and atomic constraints across 9 primary entities:

1. **Patients:** Core identity master data.
2. **Addresses:** Polymorphic tracking (Current, Permanent, Work) with spatial coordinates support.
3. **DengueDetails:** Clinical classifications (`Classic`, `Hemorrhagic`, `Shock Syndrome`) and dynamic tracking states.
4. **Hospitals:** Inventory master tracking total beds, specialized ICU capacity, and operational contacts.
5. **Treatments:** Financial ledger and inpatient/outpatient admission tracking.
6. **LabTests:** Standardized laboratory test results metadata.
7. **ContactTracing:** Direct mapping layer tracking vector cluster circles.
8. **DailyMonitoring:** Periodic structured vital data collection.
9. **Users:** Multi-tier role authorization structure (`Admin`, `Doctor`, `Nurse`, `Field Worker`, `Data Entry`).

---

## 📁 Repository Structure

```text
├── app.py               # Flask application server, ORM models, and API endpoints
├── database.sql         # Raw DDL database schema definitions, Views, and Seed data
├── static/              # Web application frontend assets 
│   ├── index.html       # Single Page Application core structure
│   └── [CSS/JS assets]  # Dashboard layouts and forms
└── README.md            # Repository documentation

```

---

## ⚙️ Quick Start Installation

### Prerequisites

* Python 3.8 or higher installed on your host system.
* XAMPP Server (with MySQL/MariaDB module enabled) or a standalone MySQL instance running locally.

### Step 1: Database Initialization

1. Open your XAMPP Control Panel and start the **Apache** and **MySQL** actions.
2. Head over to your browser and access **phpMyAdmin** (`http://localhost/phpmyadmin`).
3. Create a new database named `denguetrackingsystem`.
4. Import the provided `database.sql` script into your newly created database. This step sets up the core tables, analytical views (`DenguePatientSummary`, `DengueDistrictStats`), and populates the database with default healthcare infrastructure metadata.

### Step 2: Backend Dependencies Setup

Clone this repository to your local directory, navigate into it, and set up a clean Python virtual environment:

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/CSE311L-Dengue-Patient-Management-System-.git
cd CSE311L-Dengue-Patient-Management-System-

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install required system packages
pip install flask flask_sqlalchemy flask_cors pymysql cryptography

```

### Step 3: Run the Application

Kick off the core Flask service layer:

```bash
python app.py

```

The terminal will log database synchronization operations and initiate a live local runtime instance:

* **Local Web Server URL:** `http://localhost:5000`
* **Root Default Admin User ID:** `admin`
* **Root Default Admin Password:** `admin123`

---

## 🔌 API Documentation (Core REST Endpoints)

| Method | Endpoint | Description |
| --- | --- | --- |
| **POST** | `/api/login` | Validates session security tokens for application entry points. |
| **GET** | `/api/dashboard/stats` | Aggregates system metrics (Total Cases, Critical Alerts). |
| **POST** | `/api/patients` | Registers a patient profile, maps spatial addresses, and maps an initial clinical instance. |
| **GET** | `/api/patients` | Paginated index with integrated search filters (`search`, `severity`, `district`). |
| **GET** | `/api/patients/<id>` | Deep fetch detailing core demographic metadata, addresses, and clinical diagnosis context. |
| **GET** | `/api/dengue/district-stats` | Complex sub-query grouping regional outbreak analysis vectors across geographical districts. |
| **POST** | `/api/patients/<id>/lab-tests` | Injects a new laboratory test. Triggers automated clinical severity cascades if mapping platelet metrics. |
| **POST** | `/api/patients/<id>/daily-monitoring` | Registers regular daily vitals, updating critical telemetry trends seamlessly. |

---

## 📊 Database Reporting Layer

The system uses pre-compiled database views within `database.sql` to offload analytical aggregation from the application layer to the MySQL engine:

* **`DenguePatientSummary`**: Joins `Patients`, `DengueDetails`, `Addresses`, and active `Treatments` to create a live snapshot of hospitalized cases.
* **`DengueDistrictStats`**: Uses aggregate calculations (`COUNT`, `SUM`, `MIN`, `MAX`) grouped by geographical district to help health officials locate emerging hot zones.
