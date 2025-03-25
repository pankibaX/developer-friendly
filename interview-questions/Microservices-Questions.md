
### Microservices

#### **What are the advantages of Microservices Architecture ?**
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

#### **What are the disadvantages/challenges of Microservices Architecture ?**
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

#### **How to design scalable microservices ?**

#### **What are the best practices to design microservices ?**
