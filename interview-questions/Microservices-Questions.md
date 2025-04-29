
### Microservices Questions 
---
#### **Talk about Monolithic Application / Architecture ?**

A **monolithic architecture** is a traditional software design pattern where an application is built as a **single, tightly coupled unit**. In a monolithic application, all components — including the user interface, business logic, and database interactions — are integrated within the same codebase and deployed together.

- **Types of Monolithic Architecture**
  - While monolithic architectures can vary in structure, they generally fall into the following categories:
    - **Single-tier Monoliths**: Entire application is deployed as one  layer.
    - **Modular Monoliths**: Logically separated into modules but still deployed as a single unit. Deployed as EAR files
    - **Layered Monoliths**: Organized by layers (e.g., presentation, business, data), but still tightly coupled.

- **When to Use Monolithic Architecture**
  - **Small Applications** MVP or low-traffic apps with simple logic.
  - **Short-Term Projects** Proof-of-concepts with no scaling needs
  - **Limited Team Size** Single-team projects with minimal coordination overhead.

- **Advantages of Monolithic Architecture**
  - **Building** the application as a single unit  
  - **Testing** components together in one environment  
  - **Deploying** with fewer moving parts  
  - **Troubleshooting** through centralized logs and business logic  
  - **Scaling vertically** by increasing resources on a single server

- **Challenges of Monolithic Architecture**
  - **Scalability Issues**
    - Vertical Scaling Only: Must scale the entire app (even if only one feature needs more resources).
    - Resource Waste: Over-provisioning for peak loads affects cost efficiency.
  - **Slower Development & Deployment**
    - Long Release Cycles: Small changes require full redeployment
    - Team Bottlenecks: Large teams working on the same codebase cause conflicts.
  - **Limited Agility & Innovation**
    - Tech Lock-in: Hard to adopt new frameworks/languages.
    - High Risk Changes: A bug in one module can crash the entire system.
  - **Poor Fault Isolation**
    - Cascading Failures: One failing component can bring down the whole app.
    - Complex Debugging: Logs and errors are centralized but harder to trace.
  - **Maintenance Complexity**
    - Spaghetti Code: Over time, dependencies grow uncontrollably
    - High Technical Debt: Legacy code becomes harder to refactor.
  - **Inefficient Resource Usage**
    - Memory/CPU Hog: Even idle features consume resources.
    - Database Bottlenecks: Single RDBMS struggles with diverse query patterns.


#### **Explain Microservices and its advantages / disadvantages ?**

Microservices is an architectural style where an application is built as a collection of small, independent services that communicate over lightweight protocols like HTTP or messaging queues. Each service focuses on a **specific business capabilit**y, ensuring **loose coupling and high cohesion**

- **Advantages**
  - **Independent developement**
    - Microservices can be assigned to specific development teams, which allows them to focus solely on one service/feature
  - **Independently deployable**
    - Microservice can be deployed independently, as needed, enabling continuous improvement and faster app updates
  - **Scalability**
    - Since all services are separate, you can more easily scale the most needed ones at the appropriate times, as opposed to the whole application. This also means scaling is faster and often more cost-efficient as well
  - **Fault Isolation**
    - If a specific microservice fails, you can isolate that failure to that single service and prevent cascading failures that would cause the app to crash. This fault isolation means that your critical application can stay up and running even when one of its modules fails
    - Microservices reduce downtime through fault isolation
  - **Mixed Technology Stack**
      - Microservices provide the flexibility to try out a new technology stack on an individual service as needed
  - **Ease to understand and maintain**
      - Smaller codebase enables teams to more easily understand the code, making it simpler to maintain

- **Disadvantages**
  - **Communication between services is complex**
      - Communication between services can be complex. An application can include dozens or even hundreds of different services, and they all need to communicate securely
  - **Debugging problems can be harder**
      - Debugging becomes more challenging with microservices. With an application consisting of multiple microservices and with each microservice having its own set of logs, tracing the source of the problem can be difficult
  - **Global testing is difficult**
      - Unit testing may be easier with microservices, integration testing is not. The components are distributed, and developers can’t test an entire system from their individual machines/workspaces
  - **Interface control is even more critical**
      - Each microservice has its own API, which apps rely on to be consistent. While you can easily make changes to a microservice without impacting the external systems interacting with it, if you change the API (the interface), any application using that microservice will be affected if the change is not backwards compatible
  - **Up-front costs may be higher with microservices**
      - Its highly likely that in the short term at least you’ll see an increase in costs from a number of factors
  - **Distributed transactions handling could be complex/difficult to handle**

#### **Explain why RESTful API is stateless services ?**

- **Statelessness of REST Api**
  - Statelessness means that every HTTP request happens in complete isolation
  - Each request must contain all of the information necessary to be understood by the server, rather than be dependent on the server remembering prior requests.
  - Storing session state on the server violates the stateless constraint of the REST architecture
  - If any such information is important then the client will send that as part of the current request

- **The stateless constraint**
  - Each request from client to server must contain all of the information necessary to understand the request, and cannot take advantage of any stored context on the server
  - Session state kept entirely on the client

- **Authentication and authorization**
  - If the client requests protected resources that require authentication, every request must contain all necessary data to be properly authenticated/authorized.
  - HTTP authentication is presumed to be stateless: all of the information necessary to authenticate a request MUST be provided in the request, rather than be dependent on the server remembering prior requests and **authentication data should belong to the standard HTTP Authorization header**

- **how authentication/authorization works**
  - For authentication, you could use the Basic HTTP Authentication scheme, which transmits credentials as username and password pairs, encoded using Base64: ***Authorization: Basic \<credentials>***
  - If you don't want to send the username and password in each request, the username and password could be exchanged for a token (such as JWT) that is sent in each request. JWT can contain the username, an expiration date and any other metadata that may be relevant for your application: ***Authorization: Bearer \<token>***


#### **How to modernize application ?**

- **Understand the Existing Monolith**
  - **Analyze the architecture:** Identify modules, business logic boundaries, and dependencies.
  - **Identify pain points:** Scalability issues, tightly coupled components, long deployment cycles.

- **Apply Domain-Driven Design (DDD) principles**
  - Split into Bounded Contexts (e.g., User, Orders, Inventory).
  - Identify aggregate roots, entities, and value objects.

- **Prioritize Services for Extraction**
  - Start with low-coupled, high-cohesion components.
  - Choose areas that change often or need independent scaling.

- **Design Microservice APIs**
  - Define clear, versioned REST APIs or gRPC endpoints.
  - Establish input/output contracts using OpenAPI/Swagger.

- **Refactor the Monolith**
  - Strangle the monolith gradually using the Strangler Fig Pattern.
  - Move features one by one, replacing internal calls with API calls.

- **Data Management**
  - Each microservice must own its database (no shared DB).
  - Use event-driven architecture to sync data if needed (CQRS/Event Sourcing).

- **Communication**
  - Synchronous: REST/gRPC between services.
  - Asynchronous: Messaging queues (Kafka, RabbitMQ) for event-based communication.

- **Centralized Configuration and Discovery**
  - Use Service Discovery (Eureka, Consul, etc.)
  - Centralized configuration (Spring Cloud Config, HashiCorp Vault, etc.)

- **Observability**
  - Logging (ELK/EFK stack)
  - Monitoring (Prometheus + Grafana)
  - Tracing (Jaeger/Zipkin + OpenTelemetry)

- **CI/CD and DevOps**
  - Independent build pipelines per service.
  - Containerization (Docker), orchestration (Kubernetes).

#### **What is DDD and how its applied with microservices ?**

Domain-driven design (DDD) is a key & necessary tool when designing microservices, be it breaking a monolith or implementing a greenfield project. Domain-driven design (DDD) requires a good understanding of the domain for which the application is written

- **Domain Analysis**:  
   Collaborate with domain experts to understand the application's functional requirements and identify core business processes.  

- **Define Bounded Contexts**:  
   Divide the domain into smaller, distinct areas, each with its own unique vocabulary and model, called **Bounded Contexts**.  

- **Context Mapping**:  
   Visualize the relationships between Bounded Contexts and how they interact.  

- **Tactical DDD**:  
   Within each Bounded Context, model entities, aggregates, and domain services, applying tactical DDD patterns.  

- **Microservice Design**:  
   Identify microservices by aligning them with Bounded Contexts, ensuring each service is self-contained and loosely coupled.  

- **Layered Architecture**:  
   Organize each microservice into layers (*presentation, application, domain, infrastructure*) to improve maintainability and testability.  

- **Iterative Refinement**:  
   Continuously refine the domain model and microservices based on feedback and evolving business needs.  

#### **How to design scalable microservices ?**

#### **What are the best practices to design microservices ?**
