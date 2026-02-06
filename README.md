# CogniMentor - V2 Professional Platform

CogniMentor V2 is a production-grade educational platform featuring advanced OTP verification, structured "w3schools-style" curriculum, and adaptive AI learning paths.

## 🚀 Key V2 Features

### 1. Robust Security Architecture
- **OTP Verification**: Email-based OTP is enforced during signup and strictly validated before account activation.
- **Session Security**: Secure session management with `Flask-Login` and `Flask-WTF` CSRF protection.
- **Role-Based Access**: Strict route protection via `@login_required` decorators.

### 2. Professional Content Structure
- **Doc-Style Learning**: Topics are rendered with clear learning objectives, structured theory sections, and code blocks with syntax highlighting.
- **Linear Progression**: Topics follow a strict `order_index` sequence (Intro -> Variables -> Logic).
- **Rich Metadata**: Content is stored as structured JSON payloads (`content_payload`) in the database, allowing granular rendering control.

### 3. Expanded Curriculum (Seed Data)
- **GATE CSE & IT**: Comprehensive syllabus including Theory of Computation, OS, and Networks.
- **Government Exams**: General Knowledge, History, and Economy modules.
- **Aptitude**: Quantitative and Logical Reasoning.

### 4. Premium UI/UX & AI
- **Google Material Design**: Glassmorphism, 8px grid system, and responsive animations.
- **CongiMentor AI Bot**: A persistent floating mentor that offers teaching, guidance, and motivation.
- **Adaptive Recommendations**: Smart remediation logic detecting weak areas (<70%).

## 🛠️ Setup & Installation

1.  **Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2. **Initialize V2 Database with Content**:
    ```bash
    python seed_v2.py
    ```
    *Note: This creates a super-admin and populates the structured curriculum.*

3. **Run Application**:
    ```bash
    python app.py
    ```
    Access at `http://127.0.0.1:5000`

## 🏗️ System Architecture

### Authentication Flow
1. User Sign Up -> Created in DB (`is_verified=False`) -> Generate 6-digit OTP.
2. OTP stored in DB with 5-minute expiry.
3. User redirected to `/verify`.
4. Valid OTP -> `is_verified=True` -> Session Active.

### Data Flow
- **Frontend**: Jinja2 Templates (Google Material CSS) -> Request.
- **Backend**: Flask Blueprints (`main`, `auth`) -> Controller Logic.
- **Content**: `Topic` Model (JSON Payload) OR `AI Engine` (Fallback Generation) -> View.

---
