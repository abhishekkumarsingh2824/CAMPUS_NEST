# CampusNest — Room Finder for Students 🏠🎓

**CampusNest** is a full-stack web application designed to help college students easily discover, filter, and secure affordable rooms, PGs, hostels, and shared flats near their universities across India.

Built with **Django** and **PyMongo** interfacing natively with **MongoDB**, this project serves as a comprehensive **Final-Year College Project / Capstone** adhering to real-world software engineering practices, responsive UI/UX standards, and secure session-based authentication.

---

## 🌟 Key Features

### 🎓 1. For Students
- **Smart Room Search & Multi-Criteria Filtering**: Filter by City, Room Type (Single Room, Shared Room, PG, Hostel, Studio, 1BHK, 2BHK), Rent Range, and Specific Amenities (WiFi, AC, Food/Mess, CCTV, Security, Power Backup, Gym, etc.).
- **Property Details & Media Gallery**: Rich visual property pages displaying room images, rent, deposit, locality, distance to nearest college, owner details, and list of amenities.
- **Favorites & Bookmarks**: Save properties to wishlist with one click for easy side-by-side comparison.
- **Direct Owner Inquiries**: Send messages directly to property owners specifying college, semester, and move-in requirements.
- **Ratings & Reviews**: Read verified feedback from other students and submit star ratings and detailed reviews.
- **Student Dashboard**: Track active inquiries, review inquiry statuses (Pending / Responded / Closed), and manage saved properties.

### 🏢 2. For Property Owners
- **Easy Listing Management**: Add properties with title, description, rent, deposit, occupancy rules, city, locality, nearby college, address, and upload property photos.
- **Availability Toggle**: Switch listings between *Available* and *Occupied* with one click without having to delete properties.
- **Inquiry Management Hub**: View inquiries sent by students for listed rooms and update status (`Pending`, `Responded`, `Closed`).
- **Owner Dashboard**: Real-time stats showing total active listings, inquiries received, and property health.

### 🛡️ 3. For Platform Administrators
- **Admin Panel**: Moderation dashboard for reviewing property submissions (`Pending`, `Approved`, `Rejected`).
- **User Management**: Monitor registered student and owner accounts with administrative privileges to maintain platform safety.
- **System Statistics**: Real-time analytics on approved properties, active users, cities covered, and total inquiries.

---

## 🛠️ Technology Stack

| Layer | Technology | Details |
|---|---|---|
| **Backend** | Python 3.14+, Django 6.1 | MVC/MVT architecture, Custom middleware, Form processing, Session management |
| **Database** | MongoDB | Document-oriented NoSQL database |
| **Database Driver** | PyMongo 4.19 | Mandatory native Python driver for MongoDB (No djongo or ORM abstraction) |
| **Frontend** | HTML5, CSS3, JavaScript | Modern semantic markup, CSS variables, glassmorphic styling |
| **UI Framework** | Bootstrap 5.3 + Bootstrap Icons | Responsive grid system, modals, badges, cards, navigation |
| **Auth** | Django Session & Password Hashers | Secure PBKDF2/SHA256 password hashing via `make_password` & `check_password` |
| **Image Uploads** | Pillow & Django Media Root | File extension validation, secure UUID naming, dynamic image rendering |

---

## 🗄️ Database Architecture (MongoDB + PyMongo)

All application data is maintained inside MongoDB (Database name: `campusnest`) using 5 primary collections:

### 1. `users` Collection
```json
{
  "_id": ObjectId("..."),
  "full_name": "Aarav Sharma",
  "email": "student@demo.com",
  "phone": "9876543210",
  "password_hash": "pbkdf2_sha256$...",
  "role": "student", // "student" | "owner" | "admin"
  "college": "Delhi University (North Campus)",
  "city": "New Delhi",
  "profile_pic": null,
  "created_at": ISODate("...")
}
```

### 2. `properties` Collection
```json
{
  "_id": ObjectId("..."),
  "title": "Cozy Single Room near North Campus",
  "description": "Fully furnished room with dedicated study table, high-speed WiFi...",
  "property_type": "Room",
  "room_type": "Single Room",
  "monthly_rent": 8500,
  "security_deposit": 8500,
  "city": "New Delhi",
  "locality": "Kamla Nagar",
  "nearby_college": "Delhi University (North Campus)",
  "address": "B-42, Near Hansraj College, Kamla Nagar",
  "amenities": ["WiFi", "AC", "Attached Bathroom", "Power Backup", "Study Room"],
  "occupancy": "1 Person",
  "gender_preference": "Any",
  "owner_id": "...",
  "images": ["properties/sample.jpg"],
  "approval_status": "approved", // "pending" | "approved" | "rejected"
  "availability_status": true,
  "created_at": ISODate("..."),
  "updated_at": ISODate("...")
}
```

### 3. `inquiries` Collection
```json
{
  "_id": ObjectId("..."),
  "student_id": "...",
  "owner_id": "...",
  "property_id": "...",
  "message": "Hello, I am interested in this room for the academic year...",
  "status": "pending", // "pending" | "responded" | "closed"
  "created_at": ISODate("...")
}
```

### 4. `favorites` Collection
```json
{
  "_id": ObjectId("..."),
  "student_id": "...",
  "property_id": "...",
  "created_at": ISODate("...")
}
```

### 5. `reviews` Collection
```json
{
  "_id": ObjectId("..."),
  "student_id": "...",
  "property_id": "...",
  "rating": 5,
  "comment": "Safe environment, reliable power backup, very close to campus.",
  "created_at": ISODate("...")
}
```

---

## ⚡ Quick Start & Setup Guide

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- MongoDB Server running locally on `localhost:27017` (or a MongoDB Atlas connection URI)

### 2. Clone / Open Directory
```bash
cd e:/Django_Project
```

### 3. Install Required Packages
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Verify or adjust your `.env` file (copied from `.env.example`):
```ini
DJANGO_SECRET_KEY=django-insecure-campusnest-student-room-finder-project-key-2025
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=campusnest
```

### 5. Run Migrations & System Checks
Django auth and session frameworks require the base schema:
```bash
python manage.py check
python manage.py migrate
```

### 6. Populate Sample Indian Data
Seed the MongoDB database with realistic demo properties, owners, students, and an admin:
```bash
python manage.py seed_data --clear
```

### 7. Run Test Suite
Run the automated unit and integration tests:
```bash
python manage.py test
```
All 21 test cases should pass with `OK`.

### 8. Start the Development Server
```bash
python manage.py runserver
```
Visit the platform at: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔑 Demo Login Credentials

For demonstration and viva evaluation, the following pre-configured accounts are ready to use:

| Role | Email | Password | Access / Purpose |
|---|---|---|---|
| **Student** | `student@demo.com` | `demo1234` | Search rooms, favorite listings, submit inquiries & reviews |
| **Student 2** | `student2@demo.com` | `demo1234` | Secondary student account for multi-user testing |
| **Owner** | `owner@demo.com` | `demo1234` | Add rooms, edit properties, toggle availability, respond to inquiries |
| **Owner 2** | `owner2@demo.com` | `demo1234` | Additional owner account with listings |
| **Administrator** | `admin@demo.com` | `demo1234` | Access `/admin-panel/` to approve/reject rooms and manage users |

---

## 📁 Project Structure

```
Django_Project/
│
├── accounts/               # Custom user auth, dashboards, profile management
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── properties/             # Room listings, filtering, search, add/edit CRUD
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── inquiries/              # Student-to-owner messaging & inquiry lifecycle
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── favorites/              # Student bookmarking & wishlist
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── reviews/                # Ratings & student feedback
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── core/                   # Landing page, about, contact, admin panel & moderation
│   ├── context_processors.py
│   ├── decorators.py       # Custom @student_required, @owner_required, @admin_required
│   ├── templatetags/       # Custom template filters (split, get_item)
│   ├── management/commands/seed_data.py # Realistic data seeding script
│   └── views.py
│
├── config/                 # Project configuration (settings, root urls, wsgi)
├── templates/              # Bootstrap 5 Jinja/Django templates with responsive design
├── static/                 # Custom CSS and client JavaScript
├── db_utils.py             # Reusable PyMongo connection, index setup, document wrapper
├── requirements.txt        # Pinned dependencies
├── manage.py               # Django CLI utility
└── README.md               # Project documentation
```

---

## 🔒 Security Best Practices Implemented

1. **Password Hashing**: Uses Django's cryptographically secure PBKDF2 with SHA-256 implementation (`make_password`, `check_password`). Plaintext passwords are never stored.
2. **Access Control**: Role-based access decorators (`@login_required_custom`, `@student_required`, `@owner_required`, `@admin_required`) prevent privilege escalation.
3. **Template Injection & Safe ID Resolution**: Custom wrapper guarantees proper sanitization and string ID exposure to prevent unauthorized internal attribute exposure.
4. **CSRF Protection**: All POST forms include `{% csrf_token %}` tokens.
5. **Safe File Handling**: Uploaded images are restricted to `.jpg`, `.jpeg`, `.png`, and `.webp` with cryptographically random UUID filenames preventing path traversal.

---

## 🎓 Academic Presentation Tips

- **Why PyMongo instead of Djongo/Django ORM?**
  *Djongo translates SQL to MongoDB queries via complex translation layers that often break with modern Django versions. Using PyMongo directly gives 100% native control over MongoDB document structures, indexing, and high-performance querying without ORM overhead.*
- **How is session security handled?**
  *The user's session stores a unique session key in Django's session store, which references the MongoDB user ID. Every view validates the session role before granting access.*

---

## 📊 Presentation Deck Content (10-Slide PPT Guide)

Use the structured slide content below to prepare a professional 9 to 10-slide PowerPoint deck for your project viva, seminar, or capstone evaluation:

```markdown
================================================================================
SLIDE 1: Title & Introduction
================================================================================
Title: CampusNest — Smart Room & PG Finder for College Students
Subtitle: A Full-Stack Web Application Powered by Django & Native MongoDB (PyMongo)
Presented By: [Your Name / Team Members]
Branch & Year: Computer Science & Engineering / Final Year
Guided By: [Guide / Professor Name]
College/University: [Your University Name]

Visual/Layout Suggestions:
- Clean minimalist hero layout with CampusNest logo / badge.
- Tags: #Django #MongoDB #PyMongo #WebDevelopment #StudentHousing

--------------------------------------------------------------------------------
SLIDE 2: Problem Statement & Motivation
================================================================================
Header: The Challenge in Student Accommodation
Key Bullet Points:
• Heavy Brokerage & Hidden Charges: Traditional real estate brokers charge hefty fees from students with tight budgets.
• Unverified Listings & Safety Concerns: Lack of dedicated verification leads to misleading photos, fake listings, and safety risks.
• Missing Student-Centric Filters: Existing general portals lack filters for college proximity, gender preferences, study environments, and mess/food options.
• Fragmented Communication: Disorganized inquiry management makes communication between students and room owners slow and chaotic.

Takeaway:
Students need a secure, zero-brokerage, college-focused housing discovery platform.

--------------------------------------------------------------------------------
SLIDE 3: Proposed Solution — CampusNest
================================================================================
Header: Centralized, Transparent & Role-Driven Ecosystem
Key Bullet Points:
• Direct Student-to-Owner Connection: Complete elimination of middleman brokers; direct inquiry dispatch.
• Proximity-Based Discovery: Filter listings based on nearby universities, city, rent range, and amenities.
• Role-Based Access Control (RBAC): Dedicated workflows and intuitive dashboards for Students, Property Owners, and Admins.
• Moderation & Quality Assurance: Admin verification pipeline ensures only verified properties go live on the platform.

--------------------------------------------------------------------------------
SLIDE 4: Core Features & User Modules
================================================================================
Header: System Modules & Functional Highlights
Three-Column Layout:
1. Student Module:
   - Multi-criteria search (Rent, Room Type, Amenities, Nearby College)
   - One-click Favorites / Wishlist
   - Direct Inquiry submission with move-in dates & college info
   - Verified Ratings & Reviews
2. Owner Module:
   - Comprehensive property listing with multi-image upload
   - Instant Availability Toggle (Available ⇄ Occupied)
   - Inquiry tracking & status management (Pending / Responded / Closed)
   - Owner analytics dashboard
3. Admin Module:
   - Listing verification workflow (Pending ➔ Approved / Rejected)
   - Platform analytics (Active rooms, users, cities, inquiries)
   - Account governance and safety moderation

--------------------------------------------------------------------------------
SLIDE 5: System Architecture & Data Flow
================================================================================
Header: Technical Architecture (MVT + Native NoSQL)
Architecture Flowchart Overview:
[Client Browser] 
       │ (HTTP / Bootstrap 5 UI / Jinja2 Templates)
       ▼
[Django 6.1 Web Layer] (Views, Custom Decorators & Session Auth)
       │
[Native PyMongo Driver Layer] (Direct Querying, Indexing, Connection Pooling)
       ▼
[MongoDB NoSQL Database] (Collections: users, properties, inquiries, favorites, reviews)

Key Highlights:
• Decoupled MVT (Model-View-Template) pattern.
• Native PyMongo layer bypasses ORM overhead and provides 100% native MongoDB flexibility.
• Django session management integrates smoothly with custom role-based authentication.

--------------------------------------------------------------------------------
SLIDE 6: Technology Stack & Implementation Tools
================================================================================
Header: Technology Stack
Table Layout:
• Backend Framework: Python 3.14+, Django 6.1
• Database Engine: MongoDB (Document-Oriented NoSQL)
• Driver / Interface: PyMongo 4.19 (Native high-performance driver)
• Frontend / UI: HTML5, CSS3, JavaScript, Bootstrap 5.3, Bootstrap Icons
• Security & Auth: Django PBKDF2 with SHA-256 password hashing, CSRF tokens
• Media Handling: Pillow & Django Media Root with UUID-based safe naming
• Dev & Testing: Pytest / Django TestCase, Mongo CLI, Git / GitHub

--------------------------------------------------------------------------------
SLIDE 7: Database Design (MongoDB Schema)
================================================================================
Header: Schema Design & Collection Architecture
Core Collections:
1. `users`: Stores credentials, role (`student`, `owner`, `admin`), college, and contact info.
2. `properties`: Listing details, pricing, locality, amenities array, status (`approval_status`, `availability_status`), and image references.
3. `inquiries`: Relational mappings between student_id, owner_id, property_id, inquiries messages, and status lifecycle.
4. `favorites`: Dynamic bookmarks linking student IDs with property listings.
5. `reviews`: User ratings (1-5 stars), review comments, and timestamps.

Design Advantage:
NoSQL document model provides dynamic flexibility for varied amenities and schema evolution.

--------------------------------------------------------------------------------
SLIDE 8: Security & Engineering Best Practices
================================================================================
Header: Security Architecture & Reliability
Key Points:
• Cryptographic Password Hashing: PBKDF2 with SHA-256 — plaintext passwords are never stored.
• Custom RBAC Decorators: `@student_required`, `@owner_required`, and `@admin_required` enforce strict endpoint security.
• Secure Media Storage: File extension whitelist (.jpg, .jpeg, .png, .webp) and cryptographic UUID renaming to block file execution & path traversal.
• CSRF & Sanitization: Django CSRF token enforcement on all mutation requests and safe template output sanitization.

--------------------------------------------------------------------------------
SLIDE 9: Project Demonstration & Results
================================================================================
Header: Results & Working Demonstration
Visual Elements:
- Screenshot 1: Responsive Homepage & Multi-Filter Search Bar
- Screenshot 2: Property Details View with Image Gallery & Amenities Badges
- Screenshot 3: Student / Owner Dashboard with Inquiry Management
- Screenshot 4: Admin Moderation Panel (Approve / Reject Workflow)

Key Outcomes Achieved:
• Fast sub-second search and filtering query response times.
• Zero-brokerage direct communication established between students and owners.
• 100% responsive user experience across mobile, tablet, and desktop viewports.

--------------------------------------------------------------------------------
SLIDE 10: Conclusion & Future Scope
================================================================================
Header: Conclusion & Roadmap Ahead
Conclusion:
• Successfully engineered a robust, secure, full-stack housing portal tailored specifically for university students.
• Demonstrated practical application of native PyMongo integration with Django.

Future Enhancements:
• Integrated In-App Real-Time Chat (WebSockets via Django Channels).
• Integrated Online Payment Gateway for advance token/deposit transactions.
• AI-Powered Roommate Matching based on habits, college course, and budget.
• Interactive Map Integration (Google Maps / OpenStreetMap API) with radius search.

Closing:
• Q&A session with evaluators: "Thank You!"
================================================================================
```

