# 🎫 SupportDesk — Lakebase-Powered Support Ticket Management

A transactional support ticket management application built using **Databricks Apps, Streamlit, and Lakebase PostgreSQL**.

The application allows internal teams to create support tickets, view existing tickets, read ticket conversations, add messages, and update ticket status.

---

## 📌 Business Problem

Internal support teams need a simple system to manage employee support requests.

Without a centralized support system, requests can become difficult to track:

- What issues are currently open?
- Which employee created the request?
- What conversations have happened?
- What is the current status of each ticket?
- Can support teams update and track tickets in one place?

This project solves the problem by providing a lightweight transactional support ticket application backed by **Databricks Lakebase PostgreSQL**.

---

## 🎯 Project Objectives

The application provides the following capabilities:

1. View all support tickets
2. Select a ticket and view its messages
3. Create a new support ticket
4. Add messages to an existing ticket
5. Update ticket status
6. Persist all changes in Lakebase
7. Deploy the application using Databricks Apps

---

# 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │        User         │
                    │     Web Browser     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Databricks Apps   │
                    │      Streamlit      │
                    └──────────┬──────────┘
                               │
                               │ psycopg
                               ▼
                    ┌─────────────────────┐
                    │      Lakebase       │
                    │  PostgreSQL Database│
                    └──────────┬──────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
                  ▼                         ▼
           ┌──────────────┐       ┌──────────────────┐
           │    tickets   │       │ ticket_messages  │
           └──────────────┘       └──────────────────┘
```

---

# 🗄️ Data Model

SupportDesk uses a simple relational data model consisting of two related tables.

```text
┌─────────────────────────────────────┐
│              tickets                │
├─────────────────────────────────────┤
│ PK  ticket_id      SERIAL           │
│     title          VARCHAR(200)     │
│     status         VARCHAR(50)      │
│     created_by     VARCHAR(100)     │
│     created_at     TIMESTAMP        │
└──────────────────┬──────────────────┘
                   │
                   │ 1
                   │
                   │
                   │ Many
┌──────────────────▼──────────────────┐
│          ticket_messages            │
├─────────────────────────────────────┤
│ PK  message_id     SERIAL           │
│ FK  ticket_id      INTEGER          │
│     message_text   TEXT             │
│     author         VARCHAR(100)     │
│     created_at     TIMESTAMP        │
└─────────────────────────────────────┘
```

### Relationship

```text
tickets.ticket_id
        │
        │ 1 : Many
        ▼
ticket_messages.ticket_id
```

A single support ticket can contain multiple messages.

Example:

```text
Ticket #1
    │
    ├── Message #1
    └── Message #2

Ticket #2
    │
    ├── Message #3
    └── Message #4

Ticket #3
    │
    ├── Message #5
    └── Message #6

Ticket #4
    │
    └── Message #7
```

The `ticket_id` foreign key ensures that every message belongs to an existing support ticket.

### Table Responsibilities

| Table | Responsibility |
|---|---|
| `tickets` | Stores support ticket information and current status |
| `ticket_messages` | Stores conversations associated with each ticket |

---

# ⚙️ Application Features

## 1. View Support Tickets

Users can view available support tickets along with:

- Ticket ID
- Title
- Status
- Creator
- Creation timestamp

---

## 2. Select a Ticket and View Messages

Users can select a ticket from the dropdown.

The application retrieves the messages associated with the selected ticket from Lakebase using the `ticket_id`.

---

## 3. Create a Ticket

Users can create a new ticket by providing:

- Ticket title
- Created by

The ticket is inserted into the `tickets` table.

New tickets start with the status:

```text
open
```

The `created_at` timestamp is generated automatically by the database.

---

## 4. Add a Message

Users can add a message to the selected ticket.

The message is inserted into the `ticket_messages` table.

The message is associated with the selected ticket using `ticket_id`.

---

## 5. Update Ticket Status

Users can update the status of a ticket.

Supported statuses are:

```text
open
in_progress
resolved
```

The updated status is persisted in Lakebase.

---

# 🔄 Application Flow

```text
                    SupportDesk
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
    Create Ticket   View Tickets   Select Ticket
          │                           │
          ▼                           ▼
    INSERT ticket              View Messages
          │                           │
          ▼                           ▼
       Lakebase                 Add Message
                                    │
                                    ▼
                              INSERT message
                                    │
                                    ▼
                                 Lakebase

                         Update Status
                               │
                               ▼
                         UPDATE ticket
                               │
                               ▼
                            Lakebase
```

---

# 🔐 Database Connectivity

The application uses:

- Python
- `databricks-sdk`
- `psycopg`
- `psycopg-pool`
- OAuth-based database credentials
- Databricks App resource authorization

The application dynamically generates database credentials using the Databricks SDK.

Database passwords are not hard-coded into the application.

The connection flow is:

```text
Databricks App
      │
      ▼
Databricks SDK
      │
      ▼
Generate database credential
      │
      ▼
psycopg / ConnectionPool
      │
      ▼
Lakebase PostgreSQL
```

---

# 🔑 Database Permissions

The Databricks App connects to Lakebase using its service principal.

The application was granted the required PostgreSQL permissions on:

```text
public schema
       │
       ├── tickets
       │
       └── ticket_messages
```

Required operations include:

- SELECT
- INSERT
- UPDATE
- DELETE

Sequence permissions were also granted to support automatically generated IDs.

This demonstrates an important database security concept:

> Database-level connectivity does not automatically provide table-level access.

Table permissions must be explicitly granted to the application's PostgreSQL role.

---

# 📁 Project Structure

```text
supportdesk-lakebase/
│
├── business/
│
├── sql/
│
├── app/
│   ├── app.py
│   ├── app.yaml
│   ├── manifest.yaml
│   └── requirements.txt
│
└── README.md
```

### `business/`

Contains the business problem and project requirements documentation.

### `sql/`

Contains the database schema and sample data scripts.

### `app/`

Contains the Streamlit application and Databricks Apps configuration.

---

# 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | Web application UI |
| Databricks Apps | Application deployment |
| Lakebase | Transactional PostgreSQL database |
| PostgreSQL | Relational data storage |
| psycopg | PostgreSQL connectivity |
| psycopg-pool | Database connection pooling |
| Databricks SDK | Databricks integration and database credentials |
| SQL | Data modeling and database operations |
| Databricks CLI | Source synchronization and deployment |

---

# 🚀 Deployment

The application is deployed using **Databricks Apps**.

The application source contains:

```text
app.py
app.yaml
manifest.yaml
requirements.txt
```

## Authenticate with Databricks CLI

```bash
databricks auth login
```

## Synchronize application source

From the project root:

```bash
databricks sync ./app "<WORKSPACE_SOURCE_PATH>"
```

## Deploy the application

```bash
databricks apps deploy supportdesk-app --source-code-path "<WORKSPACE_SOURCE_PATH>"
```

After deployment, the application runs as a Databricks App and connects to Lakebase through the configured PostgreSQL resource.

---

# 🧪 Testing

The application was tested for the following operations.

### Ticket Retrieval

Existing tickets can be retrieved from Lakebase and displayed in the application.

### Ticket Creation

A new ticket can be created through the Streamlit interface.

The new record remains available after refreshing the application.

### Ticket Selection

Users can select an existing ticket and view its associated messages.

### Message Retrieval

Messages are retrieved from the `ticket_messages` table based on `ticket_id`.

### Message Creation

A new message can be added to an existing ticket.

The message remains available after refreshing the application.

### Status Update

Ticket status can be changed between:

```text
open
in_progress
resolved
```

The updated status remains persisted after refreshing the application.

---

# 📊 Current Database State

The final test database contains:

```text
tickets          → 4 records
ticket_messages  → 7 records
```

The database contains both:

- Original sample records
- Records created or modified through the deployed application

This demonstrates that the application is performing real database operations rather than displaying hard-coded application data.

---

# 🔄 CRUD Operations

The application performs transactional database operations across the two related tables.

## Create

Create a new ticket:

```sql
INSERT INTO public.tickets
    (title, status, created_by)
VALUES
    (%s, %s, %s);
```

Create a new message:

```sql
INSERT INTO public.ticket_messages
    (ticket_id, message_text, author)
VALUES
    (%s, %s, %s);
```

## Read

Retrieve tickets:

```sql
SELECT
    ticket_id,
    title,
    status,
    created_by,
    created_at
FROM public.tickets
ORDER BY created_at DESC;
```

Retrieve messages for a ticket:

```sql
SELECT
    message_id,
    message_text,
    author,
    created_at
FROM public.ticket_messages
WHERE ticket_id = %s
ORDER BY created_at ASC;
```

## Update

Update ticket status:

```sql
UPDATE public.tickets
SET status = %s
WHERE ticket_id = %s;
```

## Delete

The current MVP does not expose ticket deletion through the UI.

Delete functionality can be added as a future enhancement with a confirmation step.

---

# 🧠 Why Lakebase?

The support application requires **transactional operational data**.

Users are continuously performing operations such as:

```text
Create Ticket
Add Message
Update Status
Read Ticket
Read Conversation
```

These operations require:

- Fast reads and writes
- Row-level updates
- Relational integrity
- Primary keys
- Foreign keys
- Transaction support
- Persistent operational state

Lakebase provides a PostgreSQL-compatible operational database suited for this type of application workload.

This is different from using a traditional analytical table primarily designed for reporting and large-scale analytical queries.

---

# 📈 Potential Analytics Layer

Although this project focuses on the transactional application, the data can later become the source for an analytical layer.

Potential KPIs include:

- Total support tickets
- Open tickets
- In-progress tickets
- Resolved tickets
- Tickets by status
- Tickets by creator
- Average resolution time
- Messages per ticket
- Tickets created per day
- Unresolved ticket backlog

A future architecture could look like:

```text
                 Lakebase
                    │
                    ▼
             Data Engineering
                    │
             ┌──────┴──────┐
             │             │
             ▼             ▼
           Spark        SQL / ETL
             │             │
             └──────┬──────┘
                    │
                    ▼
             Analytical Layer
                    │
                    ▼
               BI Dashboard
```

This would extend the project from a transactional application into a complete Data Engineering pipeline.

---

# 🔮 Future Improvements

Possible future enhancements include:

- Ticket priority
- Ticket categories
- Ticket assignment
- Search and filtering
- Pagination
- SLA tracking
- User authentication
- Role-based access
- Audit logging
- Email notifications
- Automated escalation
- Support KPI dashboard
- Historical ticket analytics
- Spark-based data pipeline
- Databricks SQL dashboard
- Power BI integration

---

# 🎓 Key Learnings

The most important learning from this project was understanding how a transactional application can be built around a PostgreSQL-compatible database within the Databricks ecosystem.

The application separates the presentation, application, and data layers:

```text
┌────────────────────┐
│    Streamlit UI    │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Application Logic  │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ psycopg / Pool     │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Lakebase PostgreSQL│
└────────────────────┘
```

The project also provided hands-on experience with:

- Databricks Apps
- Lakebase
- PostgreSQL
- Databricks CLI
- SQL
- Relational data modeling
- Primary keys
- Foreign keys
- Database permissions
- Service principals
- OAuth authentication
- Connection pooling
- Cloud deployment
- Persistent transactional data

---

# 🏆 Project Outcome

The final application provides a working internal support ticket management system.

Users can:

```text
Create Ticket
      ↓
View Ticket
      ↓
View Messages
      ↓
Add Message
      ↓
Update Status
      ↓
Persist Changes
```

All transactional changes are stored in **Databricks Lakebase PostgreSQL**.

The application is deployed using **Databricks Apps**.

---

# 📸 Project Evidence

The project submission includes evidence of:

### Deployed Application

The SupportDesk application running successfully through Databricks Apps.

### Lakebase Tickets Table

The `tickets` table containing persisted support ticket records.

### Lakebase Ticket Messages Table

The `ticket_messages` table containing persisted ticket conversation records.

The screenshots demonstrate that the application's data is stored in Lakebase rather than being hard-coded in the application.

---

# 📋 Project Requirements Checklist

| Requirement | Status |
|---|---|
| Lakebase schema created | ✅ |
| `tickets` table created | ✅ |
| `ticket_messages` table created | ✅ |
| Foreign-key relationship | ✅ |
| At least 3 sample tickets | ✅ |
| At least 2 messages per ticket initially | ✅ |
| Multiple ticket statuses | ✅ |
| View all tickets | ✅ |
| Select ticket and view messages | ✅ |
| Create new ticket | ✅ |
| Add message | ✅ |
| Update ticket status | ✅ |
| Databricks App deployed | ✅ |
| Lakebase persistence verified | ✅ |
| Refresh persistence tested | ✅ |

---

# 💡 Business Value

The application provides a centralized operational workflow for internal support teams.

Instead of tracking support requests through scattered communication channels, employees can:

1. Create a support request.
2. Track its status.
3. View the conversation history.
4. Add additional information.
5. Resolve the ticket.

This creates a structured operational data foundation that can later support reporting, analytics, automation, and AI-powered support workflows.

---

# 👨‍💻 Author

**Shailesh**

Data Engineering Portfolio Project

Built with:

**Databricks Apps + Lakebase + PostgreSQL + Streamlit + Python**