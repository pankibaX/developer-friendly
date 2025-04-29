
### Architectural Questions

#### **Explain SOLID principle ?**
SOLID is a set of 5 design principles which encourage us to create more maintainable, understandable, and flexible object oriented software
- **S**ingle Responsibility
  - **A class should have only one reason to change,** means that each class only does one thing and every class or module only has responsibility for one part of the software’s functionality
- **O**pen for extensions, close for modifications
  - **Open for extension,** meaning that the class’s behavior can be extended and **Closed for modification,** meaning that the source code is set and cannot be changed.
- **L**iskov Substitution principle
  - Every derived class should be substitutable for its parent class
  - In a lot of ways it’s simply an extension of open-closed principle, as it’s a way of ensuring that derived classes extend the base class without changing behavior
  - Respecting this principle brings more stability over time to your complex systems with a hard focus on **retro-compatibility**
  - Objects of a superclass shall be replaceable with objects of its subclasses without breaking the application. That requires the objects of your subclasses to behave in the same way as the objects of your superclass. Its done by ***design by contract concept***
- **I**nterface Segregation
  - Clients should not be forced to depend upon interfaces that they don't use
  - Fine grained interfaces shoulde be designed that are client-specific and they should not be forced to implement interfaces they do not use.
  - Should have client specific interfaces and avoid general purpose fat interface
- **D**ependency Inversion    
  - High-level modules should not depend on low-level modules. Both should depend on abstractions. Depend on abstractions, not on concretions
  - ***High Level Classes --> Abstraction Layer --> Low Level Classes***

#### **Explain TDD approach ?**

Test driven development (TDD) is a software development approach in which a test is written before writing the code.It is a technique where test code is written before production code. It is a technique that is used for designing as well as testing software.
- **Stages**
  - Red Stage
      - Writing a test that fails because of code absence
  - Green Stage
      - Writing a code after which the test is passed 
  - Refactor Stage
      - Checking the code structure and its improvement without changing its external behavior. The expected result of refactoring is obtaining a perfectly written code   
- **Advantages**
  - Better program design and higher code quality
  - TDD keeps the code clear and simple and improves the quality of code
  - It Ensures that the written code is covered by at least one test casted
  - TDD reduces the debugging time and Eliminates duplication of code.
  - TDD helps in complete understanding of requirements and provides the ability to modify the application with the changing business requirements. Detailed project documentation
  - Code flexibility and easier maintenance
  - TDD reduces the time required for project development
- **Disadvantages**
  - DB & external files are not tested
  - Difficult to test GUI based applications
  - Need additional time to write/maintain test classes

#### **Explain Design Pattern ?**

Design patterns are reusable solutions to common problems in software design, offering proven approaches for structuring code and solving recurring issues. They are blueprints for creating flexible, maintainable, and scalable applications.

- **Creational Patterns**
  These patterns deal with object creation mechanisms, trying to create objects in a manner suitable for the situation 
  - **Factory Method**
    - Defines interface for creating objects
    - Lets subclasses decide which class to instantiate
    - Promotes loose coupling
    - Example: `Calendar.getInstance()`
    - Refer [Factory Pattern](https://github.com/pankibaX/design-patterns/tree/main/creational-patterns/src/main/java/com/pankiba/designpatterns/creational/factory)
  - **Abstract Factory**
    - Creates families of related objects
      - Higher level than Factory Method
      - Useful when system needs multiple product families
  - **Singleton**
      - Ensures only one instance of a class exists
      - Provides global access point to the instance
      - Common uses: Logger, Configuration, Database connections
      - Implementation types: Eager, Lazy, Thread-safe, Double-checked locking
      - [Refer](/creational-patterns/src/main/java/com/pankiba/designpatterns/creational/singleton)
  - **Builder**
      - Separates complex object construction from representation
      - Allows step-by-step construction
      - Example: `StringBuilder`
  - **Prototype**
      - Creates new objects by cloning prototypes
      - Avoids costly creation process
      - Requires implementing `Cloneable` interface

- **Structural Patterns**
  These patterns focus on object & class composition and provide relationships between objects to form larger structures
  - **Adapter** 
      - Bridges incompatible interfaces
      - Wraps an existing class
      - Example: `Arrays.asList()`
  - **Decorator**
      - Adds responsibilities dynamically
      - Alternative to subclassing
      - Example: `Java I/O streams`
  - **Proxy**
      - Controls access to another object
      - Types: Virtual, Remote, Protection, Smart reference
      - Example: `java.lang.reflect.Proxy`
  - **Facade**
      - Provides simplified interface to complex subsystem
      - Reduces subsystem dependencies
      - Typical in library design
- **Behavioural Patterns**
  These patterns deals with object collaboration, focusing on how objects interact and communicate with one another.
  - **Observer**
      - One-to-many dependency between objects
      - Publisher-Subscriber pattern
      - Example: Event listeners in Swing
  - **Strategy**
      - Defines family of algorithms
      - Makes them interchangeable
      - Example: `Comparator` interface
  - **Template Method**
      - Defines algorithm skeleton
      - Lets subclasses redefine certain steps
      - Example: `HttpServlet` or `JDBCTemplate` class


#### **How to design low latency and scalable applications ?**
  - Scalability is the ability of application to deal with an increasing number of users concurrently. Consequently, a scalable web application is one that performs equally well with one or a thousand users and stands ups and downs of the traffic
  - Application framework plays an important role in application performance. Components of application like front end & Back End needs to be designed corrrectly.
  - Things to consilder for low latency when you have microservices -
    - **Individual Service Design Excellence** : Each microservice should adhere to the Single Responsibility Principle, exposing a clear and concise API to minimize inter-service dependencies and reduce latency. By following Domain-Driven Design (DDD), need to aligned services with core business domains, ensuring efficient communication, streamlined data flow, and maintainable boundaries between components
    - **Efficient Communication Protocols** : Selecting the right communication protocol directly affects microservice performance. Binary protocols like gRPC or Protocol Buffers outperform text-based options by reducing payload size and serialization overhead, boosting speed and efficiency while saving bandwidth
    - **Strategic Caching & Replication** : Reduce latency by implementing layered caching and data replication. Storing frequently accessed data at multiple layers of microservices, minimizes redundant calls, improving response times and reducing backend load. Balance caching carefully to avoid stale data and excessive memory usage.
    - **Asynchronous Communication Paradigms** : Use async patterns like message queues and event-driven architectures to reduce latency. Decoupled services communicate without blocking, improving responsiveness and fault tolerance. This prevents cascading failures during peak loads or outages

  - Load Balancers for different nodes
  - Load testinig helps to locate and overcome weak areas of your application and guarantees the seamless performance
  - Infrastucture can help -
    - Vertical Scaling - more power to server
    - Horizontal Scaling - more nodes/machines for applications
  - Distribute the load horizontally
  - Design API Layer to serve client in better way
  - Use cachinig wherever possible. This will reducce DB hits and round trips
  - Monitor the performance and provide regular updates
  - Design statelesssness in application. Stateless app can scale easily
  - Database
    - Scaling
    - Replication
    - Indexes

#### **How to approach application performance optimization ?**
  - **Understand the application components and optimize them layer wise**
    - Presentation Layer optimization
      - Design Changes
        - Include only required functionality and reduce page section
        - On demand data loading & paginated results should be adopted
        - Search page should have 'paginated' view instead of 'show-all' view
      - Asset optimization
        - Minification of java script files
        - Appropriate load sequence of JS files
      - Image optimization
      - Adoption of CDN
    - Business Layer optimization
      - CRUD Operations
      - Business Logic implementation, API contract, design patterns used
      - Resource pooling
        - Database connection pooling
        - Batching operations to reduce database round trips
      - ORM framework
        - Configure the ORM framework to do lazy loading of objects and configured to use level 1 and level 2 cache. Native queries should be used for complex query operations
      - Async processing
    - DB Layer optimization
      - add/remove indexes as necessary
      - Caching Query execution plans that reduces resource usage
  - **Memory utilization review**
    - Java Virtual Machine (JVM) stores all objects and JRE classes created by the Java application in the heap
    - Take a memory snapshot, while app is running using ***jmap -dump:format=b,file=<filename.hprof> <process id>***
    - Heap Utilization review
      - Can be viewed using VisualGC plugin on VisualVM. This explains how GC effects the Eden and Survivor spaces before moving the objects to old gen. Upward & Downward graph indicates how the memory utilisation is increasing and decreasing with time.
      - Memory Leaks
        - A memory leak is a situation where unused objects occupy unnecessary space in memory.
        - VisualVM provides memory and CPU profilers and samplers.
        - Generation counts of objects in memory profilers provides data on the objects that have survived the most and can be an cause of memory leaks. More analysis required to check why the objects are surviving the garbage collection cycles, but any objects surviving for a longer duration of time which are not specifically required to survive GC’s are most likely to cause memory leaks
      - Analyze/Inspect code
        - Collections have default memory allocated and an excessive usage of collections with lesser data in the collections can lead to higher memory utilization. This can be rectified using code analysis
        - Not initializing the size of collections, can lead to higher GC’s due to failure of allocations in memory
      - Garbage Collection Logs
        - Garbage Collection logs help in identifying the JVM heap utilization, issues related to memory and can potentially indicate the memory leaks
  - **CPU Utilization review**
    - CPU resource should be optimally utilized. Applications use CPU processing for creation of resources like Threads/Executors, GC’s, Computations. Following things needs to considered while developing an application
      - Batch processing
      - Async & Parallel processing
      - Processing time analysis of each API steps
      - Caching
        - Store static data for faster retrievals
  - **Monitoring tools**
    - App Dynamics
  - **Load Testing**
    - Load/Stress testing of applications is done to analyze the performance under high stress. It helps in identifying gaps & area of improvements explained above so that app can be optimized
  - **Soak Testing**
    - Soak testing involves testing the app to detect performance-related issues such as stability and response time by requesting the designed load on a system. This is done for longer duration of time
  - **Throughput calculations**
    - Transaction per second (TPS)
    - Request per second (RPS)

#### **Explian 12 Factor App principles ?**
  The twelve-factor methodology is a set of twelve best practices to develop applications developed to run as a service.
  - **Codebase**
    - An app should be tracked in a single code repository and must not share that repository with any other apps.
  - **Dependencies**
    - Twelve-factor app should always explicitly declare all its dependencies
  - **Config**
    - A twelve-factor app should externalize all such configurations that vary between deployments.
  - **Backing Service**
    - Treat backing services as attached resources
    - In a 12-factor app, any services that don’t support the core app must be accessed as a service. These non-core essential services might include    Databases, External storage, Message queues etc.
  - **Build, release, run**
    - strictly separates the process of converting codebase into a running application
    - Build Stage
    - Release Stage
    - Run Stage
  - **Processes**
    - A twelve-factor app is expected to run in an execution environment as stateless processes.
  - **Port Binding**
    - Export services via port binding
    - 12-factor apps must always be independent from additional applications. Every function should be its own process—in full isolation
  - **Concurrency**
    - The twelve-factor methodology suggests apps to rely on processes for scaling.
    - A true 12-factor app is designed for scaling. Build your applications so that scaling in the cloud is seamless. When you develop the app to be concurrent, you can spin up new instances to the cloud effortlessly.
  - **Disposability**
    - Maximize robustness with fast startup and graceful shutdown
    - Application processes can be shut down on purpose or through an unexpected event. In either case, a twelve-factor app is supposed to handle it gracefully
  - **Dev/Prod Parity**
    - The twelve-factor methodology suggests keeping the gap between development and production environment as minimal as possible
    - Keep development, staging, and production as similar as possible
  - **Logs**
    - Treat logs as event streams
    - Logs are essential data that an application generates during its lifetime. They provide invaluable insights into the working of the application
  - **Admin processes**
    - Run admin/management tasks as one-off processes
    - Administrative tasks should be treated no differently, they should be executed within the same process formation and the code or scripts associated with them should be part of the applications repository

#### **How sessions are handled in web applications ?**
  - HTTP protocol and Web Servers are stateles
    - Session is a conversional state between client and server and it can consists of multiple request and response between client and server. Since HTTP and Web Server both are stateless, the only way to maintain a session is when some unique information about the session (session id) is passed between server and client in every request & esponse
    - several ways to handle session information
      - URL rewriting
      - Cookies
      - Hidden Form fields
      - HttpSession Api
  
#### **Design Principles for scalable applications ?**
  
#### **How to handle refrential integrity while designing microservice/s database ?**
  
#### **Explain event driven architecture ?**
  
#### **Explain the need of distributed caching ?**
  
#### **Which design patterns are getting used a lot ?**
  
#### **What's the process you follow while architecting technical solution ?**
  
#### **What are different architecting styels ?**
 
#### **What is CAP theorm ?**
