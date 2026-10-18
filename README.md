# Developer Friendly: Technical Interview Suite & Assessment Hub

An interactive, production-grade technical interview suite and assessment platform tailored for evaluating Senior, Lead, and Principal Software Engineers across full-stack Java, distributed systems, cloud architecture, and modern frontend development.

---

## 🚀 Key Features

- **Dynamic Question Bank & Coverage-First Architecture**:
  - **Governing Principle**: *Coverage determines question count, not the other way around.* Domains are not restricted by arbitrary question limits. Questions expand to achieve comprehensive, systematic coverage of real-world edge cases, production bug hunts, system trade-offs, and architecture design.
  - Dynamic discovery and navigation automatically synchronizes question counts, jump chips, and progress bars directly from the DOM and metadata.
- **Machine-Readable Technology Coverage Matrix**:
  - Full structured inventory tracked in [`interview-questions/data/coverage-matrix.json`](interview-questions/data/coverage-matrix.json) and [`interview-questions/js/coverage-matrix.js`](interview-questions/js/coverage-matrix.js) across all 9 domains (concept ID, subtopics, required depth, assessment dimensions, relevant versions, coverage status).
- **Interactive Candidate Scorecard**:
  - Live rating on a 1–4 qualitative scale (*Cannot Explain*, *Partial*, *Good*, *Exceptional*).
  - Automatically calculates competency and hiring recommendations in real-time.
  - Auto-saved to browser `localStorage` (`interview_master_data_v7`) to prevent data loss during long interviews.
- **Executive HR & Management Report**:
  - One-click summary generation translating technical ratings into qualitative executive feedback (assessed competencies, candidate strengths, growth areas, and hiring recommendations) without arbitrary numeric scoring.
- **Code Inspection Modals & Quick Navigation**:
  - Integrated syntax-highlighted code viewer with valid, production-ready imports and zero solution giveaways.
  - Responsive Quick Jump Question Navigator with smooth scrolling, highlight pulse animations, and live rating indicators on every domain page.

---

## 📚 Domains Covered

| Domain | Page | Description |
| :--- | :--- | :--- |
| **Core Java & JVM** | [`java.html`](interview-questions/java.html) | Concurrency, Memory Model, Garbage Collection, CompletableFuture, Streams, Virtual Threads. |
| **Spring & Spring Boot** | [`spring-spring-boot.html`](interview-questions/spring-spring-boot.html) | Bean Lifecycle, Transaction Propagation, AOP Proxies, Security Internals, Auto-configuration. |
| **ORM, Hibernate & JPA** | [`orm-hibernate-jpa.html`](interview-questions/orm-hibernate-jpa.html) | N+1 Query Problem, First/Second Level Caching, Dirty Checking, Entity Graphs, Optimistic Locking. |
| **REST & Microservices** | [`rest-api-microservices.html`](interview-questions/rest-api-microservices.html) | Distributed Transactions (Saga), Circuit Breakers, API Gateways, Service Discovery, Idempotency. |
| **AWS Cloud (EC2 & Lambda)** | [`aws-deployment.html`](interview-questions/aws-deployment.html) | Serverless architectures, VPC CIDRs, S3 tiering, SQS/SNS decoupled messaging, Zero-downtime deployment. |
| **Modern Angular** | [`angular.html`](interview-questions/angular.html) | Signals, RxJS operators, Change Detection (OnPush), Dependency Injection, Route Resolvers. |
| **Architecture & System Design** | [`architecture-design.html`](interview-questions/architecture-design.html) | SOLID refactoring, Event-Driven Architecture, Caching topologies, High Availability, CAP theorem. |
| **Python Core & AsyncIO** | [`python-core.html`](interview-questions/python-core.html) | GIL bottlenecks, AsyncIO event loop mechanics, Memory & Cyclic GC, Descriptors, Metaclasses, Protocols. |
| **Django, FastAPI & Flask** | [`python-web-frameworks.html`](interview-questions/python-web-frameworks.html) | Django ORM N+1 & `select_for_update`, FastAPI `async def` vs `def` starvation, Pydantic v2, Flask contexts. |

---

## 💻 Getting Started

The platform runs purely on client-side web technologies (HTML5, CSS3, ES6 JavaScript) with zero external server dependencies.

### Option 1: Open Directly in Browser
Double-click or open [`interview-questions/index.html`](interview-questions/index.html) in your browser:
```bash
open interview-questions/index.html
```

### Option 2: Run with a Local Static Server
If running via Python or Node:
```bash
# Using Python 3
python3 -m http.server 8000 --directory interview-questions

# Or using npx serve
npx serve interview-questions
```
Then navigate to `http://localhost:8000` in your browser.

---

## 📁 Repository Structure

```text
developer-friendly/
├── .gitignore                      # Git ignore rules (OS, Python, IDE artifacts)
├── README.md                       # Repository overview and usage guide
├── docs/                           # Curated developer reading & references
│   └── Good-Reads.md               # Recommended deep-dive technical articles
└── interview-questions/            # Technical Interview Assessment Hub
    ├── index.html                  # Master dashboard & candidate scorecard
    ├── css/
    │   └── styles.css              # Responsive UI design system
    ├── js/
    │   └── interview-tracker.js    # Scoring engine & executive report generator
    ├── java.html                   # Domain question pages (20 scenarios each)
    ├── spring-spring-boot.html
    ├── orm-hibernate-jpa.html
    ├── rest-api-microservices.html
    ├── aws-deployment.html
    ├── angular.html
    ├── architecture-design.html
    ├── python-core.html
    └── python-web-frameworks.html
```

---

## 📖 Curated Technical References

High-impact technical deep dives and internal architecture guides are curated in [`docs/Good-Reads.md`](docs/Good-Reads.md):
- **Spring Security Internals**: Architecture and filter chain walkthrough
- **How Spring Boot Works**: Under-the-hood class loading and auto-configuration
- **Angular State Management**: Approaches and trade-offs

