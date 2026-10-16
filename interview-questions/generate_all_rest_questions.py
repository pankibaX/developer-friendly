import os
import html

def get_rest_questions():
    questions = []

    # Q1: Idempotency Keys
    questions.append({
        "id": 1,
        "badge": "API Reliability & Payment Integrity",
        "keywords": "idempotency key distributed lock redis setnx race condition payment double charge",
        "concept": "Distributed Idempotency Keys (<code>Idempotency-Key</code> HTTP header), safe network retry handling, Redis atomic locking (<code>SETNX</code>), request payload hashing, and atomic response caching.",
        "question": """A payment microservice exposes <code>POST /api/v1/payments/charge</code>. Look at the code snippet.
<br><br>
<strong>Part A:</strong> Under peak load, a mobile client encounters a network socket timeout after 3 seconds, retries immediately with the same <code>Idempotency-Key</code>, while the first request is still executing inside the payment gateway. What happens in this implementation, and why does it fail to prevent a double charge?
<br>
<strong>Part B:</strong> How should an architect design an end-to-end distributed idempotency filter using Redis or database constraints to guarantee zero double charges across clustered instances?
<br>
<strong>Part C:</strong> What should the service return if a client sends the exact same <code>Idempotency-Key</code> but alters the request body payload (e.g., changes amount from $50 to $500)?""",
        "snippet_title": "PaymentChargeController.java",
        "snippet_code": """@RestController
@RequestMapping("/api/v1/payments")
public class PaymentChargeController {

    @Autowired
    private PaymentRepository paymentRepository;

    @Autowired
    private ExternalPaymentGateway gateway;

    @PostMapping("/charge")
    public ResponseEntity<PaymentResponse> charge(
            @RequestHeader("Idempotency-Key") String idempotencyKey,
            @RequestBody ChargeRequest request) {

        Optional<PaymentRecord> existing = paymentRepository.findByIdempotencyKey(idempotencyKey);
        if (existing.isPresent()) {
            return ResponseEntity.ok(new PaymentResponse(existing.get()));
        }

        TransactionResult result = gateway.executeCharge(request.getAmount(), request.getCardToken());

        PaymentRecord record = new PaymentRecord();
        record.setIdempotencyKey(idempotencyKey);
        record.setTransactionId(result.getTransactionId());
        record.setAmount(request.getAmount());
        record.setStatus("SUCCESS");
        paymentRepository.save(record);

        return ResponseEntity.ok(new PaymentResponse(record));
    }
}""",
        "rating_concept": "Distributed Idempotency Keys, concurrent in-flight retries, and atomic Redis locking",
        "solution": """<strong>Part A (The Concurrent In-Flight Check-Then-Act Race):</strong>
<br>The implementation suffers from a classic <strong>Time-Of-Check to Time-Of-Use (TOCTOU)</strong> race condition:
<br>1. Request 1 arrives; <code>findByIdempotencyKey</code> returns empty because nothing is saved yet. It invokes the external gateway.
<br>2. Client socket times out and immediately fires Request 2 with the same key.
<br>3. Request 2 arrives at another pod; Request 1 is still blocked waiting on the gateway, so <code>findByIdempotencyKey</code> ALSO returns empty.
<br>4. Both threads call <code>gateway.executeCharge()</code> concurrently &mdash; customer is <strong>double-charged</strong>! Furthermore, the second database save will either throw a unique constraint violation after charging or overwrite the first transaction.
<br><br>
<strong>Part B (Architectural In-Flight State Locking):</strong>
<br>• Acquire an atomic distributed lock via Redis <code>SET idempotency:{key} PROCESSING NX EX 120</code> before processing.
<br>• If key already exists in <code>PROCESSING</code> state: return <strong>HTTP 409 Conflict</strong> or <strong>HTTP 425 Too Early</strong> with <code>Retry-After</code> header, informing client request is actively processing.
<br>• Once the transaction completes, update Redis key to <code>COMPLETED</code> storing the serialized response payload with TTL (e.g. 24 hours).
<br>• Subsequent calls return the cached response payload immediately without calling the gateway.
<br><br>
<strong>Part C (Payload Tampering & Hash Mismatch):</strong>
<br>The idempotency record must store a cryptographic hash (SHA-256) of the original request body alongside the key. If an incoming request matches the key but has a different payload hash, the server must reject it with <strong>HTTP 422 Unprocessable Entity</strong> or <strong>HTTP 400 Bad Request</strong> with error <code>IDEMPOTENCY_PAYLOAD_MISMATCH</code> to prevent replay tampering.""",
        "optimized_code": """@Component
public class DistributedIdempotencyManager {

    @Autowired
    private StringRedisTemplate redisTemplate;

    public IdempotencyLock acquireLock(String key, String requestBody) {
        String payloadHash = DigestUtils.sha256Hex(requestBody);
        String lockKey = "idemp:" + key;
        
        Boolean acquired = redisTemplate.opsForValue()
            .setIfAbsent(lockKey, "PROCESSING:" + payloadHash, Duration.ofMinutes(2));

        if (Boolean.TRUE.equals(acquired)) {
            return new IdempotencyLock(Status.ACQUIRED, null);
        }

        String existingVal = redisTemplate.opsForValue().get(lockKey);
        if (existingVal != null && !existingVal.contains(payloadHash)) {
            throw new IdempotencyMismatchException("Payload altered for idempotency key: " + key);
        }
        if (existingVal != null && existingVal.startsWith("PROCESSING:")) {
            throw new ConcurrentRequestException("Request currently processing. Retry shortly.");
        }
        return new IdempotencyLock(Status.CACHED, existingVal);
    }
}""",
        "junior_eval": "Suggests putting @Transactional around the controller method or checks the database table synchronously without locking, oblivious to in-flight concurrent gateway calls.",
        "expert_eval": "Identifies the TOCTOU race condition, implements atomic Redis SETNX locking with TTL, handles in-flight 409/425 status responses, verifies SHA-256 payload tampering, and caches the final HTTP response."
    })

    # Q2: Saga Pattern
    questions.append({
        "id": 2,
        "badge": "Distributed Transactions & Consistency",
        "keywords": "saga pattern orchestration choreography compensating transactions dual write eventual consistency",
        "concept": "Distributed transactions across microservices, Saga Pattern (Orchestration vs Choreography), semantic compensation, pivot transactions, and idempotent rollback handlers.",
        "question": """A microservice architecture processes customer checkout across Order Service, Inventory Service, Payment Service, and Shipping Service. Look at the code snippet.
<br><br>
<strong>Part A:</strong> Why is Two-Phase Commit (2PC / XA transactions) considered an anti-pattern in high-throughput cloud microservices?
<br>
<strong>Part B:</strong> Compare Choreography-based Saga (Kafka event choreography) versus Orchestration-based Saga (Camunda / Temporal / Spring State Machine). What are the trade-offs regarding cyclic dependencies, observability, and coupling?
<br>
<strong>Part C:</strong> If Payment Service succeeds but Shipping Service fails permanently, how does the Saga execute a rollback? What happens if a compensating transaction fails midway?""",
        "snippet_title": "OrderCheckoutService.java",
        "snippet_code": """@Service
public class OrderCheckoutService {

    @Autowired
    private OrderRepository orderRepo;
    @Autowired
    private InventoryClient inventoryClient;
    @Autowired
    private PaymentClient paymentClient;
    @Autowired
    private ShippingClient shippingClient;

    @Transactional
    public CheckoutResult processCheckout(CheckoutCommand cmd) {
        Order order = orderRepo.save(new Order(cmd));
        
        inventoryClient.reserveStock(order.getId(), cmd.getItems());
        PaymentReceipt receipt = paymentClient.debitAccount(order.getId(), cmd.getTotalAmount());
        ShippingLabel label = shippingClient.createConsignment(order.getId(), cmd.getAddress());

        order.markConfirmed(receipt.getId(), label.getTrackingId());
        return new CheckoutResult(order.getId(), "CONFIRMED");
    }
}""",
        "rating_concept": "Saga Pattern, semantic compensation, Orchestration vs Choreography, and pivot transactions",
        "solution": """<strong>Part A (Why 2PC Fails in Microservices):</strong>
<br>• <strong>Blocking Coordinator:</strong> 2PC holds database row locks across remote network calls across multiple microservices throughout the prepare/commit phase.
<br>• <strong>Latency & Availability Collapse:</strong> If one participant or network partition delays response, all databases hold locks, starving connection pools (CAP theorem: sacrificing availability for consistency).
<br>• <strong>Heterogeneous Polyglot Backends:</strong> Message brokers (Kafka), NoSQL (Mongo, DynamoDB), and third-party SaaS APIs (Stripe) do not support XA/2PC protocols.
<br><br>
<strong>Part B (Choreography vs Orchestration):</strong>
<br>• <strong>Choreography (Event-Driven):</strong> Services react to domain events published to Kafka.
<br><em>Pros:</em> Loose coupling, high throughput, no central bottleneck.
<br><em>Cons:</em> High cognitive load, difficult end-to-end observability, risk of cyclic event storms, hard to track distributed transaction state.
<br>• <strong>Orchestration (Central Coordinator):</strong> A dedicated workflow engine explicitly commands participants (<code>reserveStock</code>, <code>chargeCard</code>, <code>compensateInventory</code>).
<br><em>Pros:</em> Clear state machine visibility, easy timeout handling, no cyclic dependencies.
<br><em>Cons:</em> Orchestrator can become a single point of failure and bottleneck if overloaded.
<br><br>
<strong>Part C (Compensating Transactions & Forward Recovery):</strong>
<br>• The Saga executes <strong>Compensating Actions</strong> in reverse order: <code>refundPayment()</code>, then <code>releaseStockReservation()</code>, and transitions Order to <code>CANCELLED</code>.
<br>• <strong>Pivot Transaction:</strong> The point of no return. Once Payment succeeds, subsequent steps must either succeed or be retried indefinitely (forward recovery).
<br>• If a compensating step fails (e.g., Payment refund returns 500), it cannot be rolled back via DB ACID. The Saga engine must retry with exponential backoff and publish to a Human-in-the-Loop dead-letter queue.""",
        "optimized_code": """@Component
public class OrderSagaOrchestrator {

    @Autowired
    private KafkaTemplate<String, Object> kafka;

    public void handleStepFailure(OrderSagaContext ctx, Step failedStep) {
        switch (failedStep) {
            case SHIPPING:
                kafka.send("payment-compensation-topic", new RefundPaymentCommand(ctx.getPaymentId()));
            case PAYMENT:
                kafka.send("inventory-compensation-topic", new ReleaseInventoryCommand(ctx.getReservationId()));
            case INVENTORY:
                kafka.send("order-cancellation-topic", new CancelOrderCommand(ctx.getOrderId()));
                break;
        }
    }
}""",
        "junior_eval": "Believes traditional @Transactional can coordinate multiple remote microservices or thinks 2PC is standard for cloud-native applications.",
        "expert_eval": "Explains why 2PC blocks distributed locks, contrasts Choreography vs Orchestration trade-offs, articulates the concept of pivot transactions, and guarantees idempotent compensating workflows."
    })

    # Q3: Distributed Tracing & W3C Trace Context
    questions.append({
        "id": 3,
        "badge": "Observability & Context Propagation",
        "keywords": "distributed tracing opentelemetry w3c traceparent span baggage mdc threadlocal async",
        "concept": "Distributed Tracing via OpenTelemetry and W3C Trace Context (<code>traceparent</code>), trace/span ID propagation across asynchronous boundaries (<code>CompletableFuture</code>, Kafka headers), and MDC loss prevention.",
        "question": """In a distributed banking architecture, Service A calls Service B over HTTP, which then offloads verification to an asynchronous thread pool and emits an event to Kafka. Look at the code snippet.
<br><br>
<strong>Part A:</strong> In production logs, developers notice that log statements inside <code>CompletableFuture.supplyAsync()</code> have empty or corrupted <code>traceId</code> and <code>spanId</code> values. Why does this happen?
<br>
<strong>Part B:</strong> What is the structure of the standard W3C <code>traceparent</code> HTTP header? How does it ensure uniform distributed tracing across multi-language microservices?
<br>
<strong>Part C:</strong> How do you bridge W3C Trace Context across an Apache Kafka message producer and consumer so that the entire downstream flow shares the exact same Trace ID?""",
        "snippet_title": "TransferAuditService.java",
        "snippet_code": """@Service
public class TransferAuditService {

    private static final Logger log = LoggerFactory.getLogger(TransferAuditService.class);

    @Autowired
    private KafkaTemplate<String, AuditEvent> kafkaTemplate;

    public void auditTransfer(TransferRequest request) {
        log.info("Processing audit for transfer: {}", request.getTransferId());

        CompletableFuture.supplyAsync(() -> {
            log.info("Executing async fraud score check");
            return calculateFraudScore(request);
        }).thenAccept(score -> {
            log.info("Fraud score computed: {}", score);
            kafkaTemplate.send("audit-events", new AuditEvent(request, score));
        });
    }

    private int calculateFraudScore(TransferRequest req) {
        return 95;
    }
}""",
        "rating_concept": "OpenTelemetry W3C trace context, async thread boundary context propagation, and Kafka header propagation",
        "solution": """<strong>Part A (ThreadLocal Loss Across Thread Pool Boundaries):</strong>
<br>Distributed tracing frameworks (Micrometer Tracing, OpenTelemetry, Logback MDC) store <code>traceId</code> and <code>spanId</code> in Java <strong>ThreadLocal</strong> variables tied to the incoming HTTP request thread.
<br>When <code>CompletableFuture.supplyAsync()</code> runs without an explicit <code>ContextExecutorService</code> or <code>TaskDecorator</code>, the work executes on a worker thread from <code>ForkJoinPool.commonPool()</code>.
<br>ThreadLocal storage is <strong>not automatically copied</strong> to the worker thread. As a result, MDC entries are null or contain stale data from previous pooled tasks.
<br><br>
<strong>Part B (W3C Trace Context Header Specification):</strong>
<br>Format: <code>traceparent: {version}-{trace_id}-{parent_id/span_id}-{trace_flags}</code>
<br>Example: <code>00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01</code>
<br>• <code>00</code>: Version 1.
<br>• <code>4bf92f3577b34da6...</code>: 16-byte global Trace ID (constant across entire request call graph).
<br>• <code>00f067aa0ba902b7</code>: 8-byte Parent Span ID for the current hop.
<br>• <code>01</code>: Bitmask flags (e.g. <code>01</code> = sampled / recorded).
<br>Standardization ensures Java, Go, Node.js, and Python services seamlessly connect telemetry graphs.
<br><br>
<strong>Part C (Kafka Header Context Injection & Extraction):</strong>
<br>The producer must use an OpenTelemetry <code>TextMapPropagator</code> to inject the active trace context into Kafka message <code>RecordHeaders</code> (e.g. key: <code>traceparent</code>).
<br>The Kafka consumer extracts the headers upon receipt, recreates the OpenTelemetry SpanContext, and scopes the consumer thread MDC before dispatching to the listener method.""",
        "optimized_code": """@Configuration
public class AsyncTracingConfig {

    @Bean
    public ThreadPoolTaskExecutor taskExecutor(ObservationRegistry registry) {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(50);
        executor.setTaskDecorator(runnable -> {
            Context context = Context.current();
            return () -> {
                try (Scope scope = context.makeCurrent()) {
                    runnable.run();
                }
            };
        });
        executor.initialize();
        return executor;
    }
}""",
        "junior_eval": "Logs a random UUID manually in every method or suggests passing String traceId as a method parameter through every business function.",
        "expert_eval": "Diagnoses ThreadLocal isolation in ForkJoinPool, articulates W3C traceparent 4-part structure, implements TaskDecorator for thread pool context handover, and injects context into Kafka record headers."
    })

    # Q4: Circuit Breaker & Resilience4j
    questions.append({
        "id": 4,
        "badge": "Resilience & Fault Tolerance",
        "keywords": "circuit breaker resilience4j sliding window open half open closed fallback thread starvation",
        "concept": "Circuit Breaker pattern, Resilience4j state transitions (<code>CLOSED</code> &rarr; <code>OPEN</code> &rarr; <code>HALF_OPEN</code>), count-based vs time-based sliding windows, slow call thresholds, and thread pool exhaustion.",
        "question": """An e-commerce order service calls an external legacy credit verification service. Look at the code snippet.
<br><br>
<strong>Part A:</strong> During peak sales, the external credit service latency spikes from 150ms to 25 seconds before timing out. Even though timeouts are configured at 5 seconds, the Order Service crashes with <code>Tomcat thread pool exhausted</code>. Explain the cascading failure mechanics.
<br>
<strong>Part B:</strong> Describe the exact mathematical and state transition mechanics of Resilience4j from <code>CLOSED</code> to <code>OPEN</code>, and from <code>OPEN</code> to <code>HALF_OPEN</code> to <code>CLOSED</code>.
<br>
<strong>Part C:</strong> What is the difference between a Failure Rate Threshold and a Slow Call Rate Threshold? When should you trigger a circuit trip on slow calls even if HTTP 200 is returned?""",
        "snippet_title": "CreditCheckClient.java",
        "snippet_code": """@Service
public class CreditCheckClient {

    @Autowired
    private RestTemplate restTemplate;

    public CreditReport verifyCredit(String customerId) {
        String url = "https://legacy-credit.internal/api/verify/" + customerId;
        return restTemplate.getForObject(url, CreditReport.class);
    }
}""",
        "rating_concept": "Resilience4j Circuit Breaker states, sliding window algorithms, and cascading failure prevention",
        "solution": """<strong>Part A (Cascading Failure & Thread Pool Starvation):</strong>
<br>• Tomcat has a finite incoming request thread pool (default 200 threads).
<br>• When the remote service slows down to 5 seconds per call, 40 incoming requests per second will saturate all 200 worker threads in just 5 seconds (Little's Law: $L = \\lambda \\times W$).
<br>• Subsequent requests for fast, unrelated endpoints (like <code>/health</code>, <code>/orders/status</code>, <code>/products</code>) are queued or rejected with HTTP 503. The caller service completely collapses.
<br><br>
<strong>Part B (Resilience4j State Machine & Sliding Window):</strong>
<br>1. <strong>CLOSED:</strong> All calls pass to the remote service. Calls are recorded in a sliding window (e.g. last 100 calls or last 60 seconds). If failure rate exceeds <code>failureRateThreshold</code> (e.g., 50%) after minimum calls (<code>minimumNumberOfCalls = 20</code>), the circuit transitions to <strong>OPEN</strong>.
<br>2. <strong>OPEN:</strong> All incoming calls are short-circuited immediately with <code>CallNotPermittedException</code> without hitting the network, executing fallback logic in microseconds.
<br>3. <strong>HALF_OPEN:</strong> After <code>waitDurationInOpenState</code> (e.g., 30s), circuit transitions to HALF_OPEN, permitting a limited trial probe of calls (<code>permittedNumberOfCallsInHalfOpenState = 10</code>).
<br>4. If trial failure rate is below threshold, it returns to <strong>CLOSED</strong>; if failures persist, it transitions back to <strong>OPEN</strong>.
<br><br>
<strong>Part C (Slow Call Rate vs Failure Rate):</strong>
<br>A call returning HTTP 200 after 8 seconds is functionally worse than an immediate HTTP 500 error because it ties up threads, DB connections, and sockets.
<br>Resilience4j tracks <code>slowCallDurationThreshold</code> (e.g., 2s). If 50% of calls take longer than 2 seconds, the circuit opens, protecting server threads before total collapse.""",
        "optimized_code": """@Service
public class ResilientCreditService {

    @Autowired
    private RestClient restClient;

    @CircuitBreaker(name = "creditService", fallbackMethod = "creditFallback")
    @TimeLimiter(name = "creditService")
    public CompletableFuture<CreditReport> verifyCredit(String customerId) {
        return CompletableFuture.supplyAsync(() -> 
            restClient.get()
                .uri("/api/verify/{id}", customerId)
                .retrieve()
                .body(CreditReport.class)
        );
    }

    public CompletableFuture<CreditReport> creditFallback(String customerId, Throwable ex) {
        return CompletableFuture.completedFuture(CreditReport.provisionalPass(customerId));
    }
}""",
        "junior_eval": "Wraps the RestTemplate call in a naive try-catch and returns null or increases the timeout from 5s to 30s, deepening the thread starvation.",
        "expert_eval": "Explains Little's Law and thread pool starvation, diagrams the 3-state transition model with sliding windows, tunes slow-call thresholds, and pairs CircuitBreaker with Bulkhead isolation."
    })

    # Q5: Transactional Outbox Pattern
    questions.append({
        "id": 5,
        "badge": "Event-Driven & Dual-Write Mitigation",
        "keywords": "transactional outbox pattern dual write kafka debezium cdc event published polling publisher",
        "concept": "The Dual-Write Problem in Microservices, Transactional Outbox Pattern, Change Data Capture (CDC via Debezium), and at-least-once event delivery guarantees.",
        "question": """An order placement endpoint needs to persist an Order to PostgreSQL and publish an <code>OrderCreatedEvent</code> to Apache Kafka. Look at the code snippet.
<br><br>
<strong>Part A:</strong> Identify the critical Dual-Write flaw in this implementation. Under what network or database failure scenarios does the system either lose the event or produce ghost events?
<br>
<strong>Part B:</strong> Why can't we solve this simply by placing <code>kafkaTemplate.send()</code> inside a Spring <code>@Transactional</code> method?
<br>
<strong>Part C:</strong> Detail the architecture of the <strong>Transactional Outbox Pattern</strong>. Compare an asynchronous Polling Publisher approach against a Log-Based Change Data Capture (CDC) approach using Debezium.""",
        "snippet_title": "OrderPlacementService.java",
        "snippet_code": """@Service
public class OrderPlacementService {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private KafkaTemplate<String, OrderCreatedEvent> kafkaTemplate;

    @Transactional
    public Order placeOrder(OrderRequest request) {
        Order order = new Order(request);
        orderRepository.save(order);

        OrderCreatedEvent event = new OrderCreatedEvent(order.getId(), order.getTotal());
        kafkaTemplate.send("order-created-topic", event);

        return order;
    }
}""",
        "rating_concept": "Transactional Outbox Pattern, Dual-Write problem, and Debezium Change Data Capture (CDC)",
        "solution": """<strong>Part A (The Dual-Write Failure Scenarios):</strong>
<br>1. <strong>Ghost Event:</strong> <code>kafkaTemplate.send()</code> succeeds and emits the message to Kafka. However, right after, PostgreSQL fails to commit (e.g. database constraint violation, connection timeout, disk full). Result: Downstream inventory services deduct stock for an order that <strong>does not exist</strong> in the database!
<br>2. <strong>Lost Event:</strong> Database commits, but Kafka broker is unreachable or network times out. Result: Order exists in DB, but downstream payment and fulfillment services never hear about it.
<br><br>
<strong>Part B (Why @Transactional Cannot Wrap Kafka):</strong>
<br>Kafka is not an XA-compliant resource that participates in local database ACID transactions.
<br>Even with Spring Kafka transactions, coordinated commit across heterogeneous engines requires 2PC, which Kafka does not support with standard RDBMS transactions. One of the two systems will always commit before the other.
<br><br>
<strong>Part C (Transactional Outbox Architecture):</strong>
<br>• Write the business record (<code>orders</code>) and an event record (<code>outbox_events</code>) within the <strong>same atomic local database transaction</strong>.
<br>• <strong>Approach 1 (Polling Publisher):</strong> A background scheduled worker polls <code>SELECT * FROM outbox_events WHERE status = 'PENDING'</code> and sends to Kafka, then marks sent. (Drawback: polling latency, DB CPU load, table lock contention).
<br>• <strong>Approach 2 (Log-based CDC with Debezium):</strong> Debezium tails PostgreSQL Write-Ahead Log (WAL) directly. Zero application polling overhead, sub-millisecond event streaming to Kafka, guarantees at-least-once delivery.""",
        "optimized_code": """@Entity
@Table(name = "outbox_events")
public class OutboxEvent {
    @Id
    private UUID id = UUID.randomUUID();
    private String aggregateType;
    private String aggregateId;
    private String eventType;
    @Column(columnDefinition = "jsonb")
    private String payload;
    private Instant createdAt = Instant.now();
}

@Service
public class OrderService {
    @Transactional
    public Order createOrder(OrderRequest req) {
        Order order = orderRepo.save(new Order(req));
        OutboxEvent event = new OutboxEvent("ORDER", order.getId().toString(), 
            "OrderCreated", objectMapper.writeValueAsString(order));
        outboxRepo.save(event);
        return order;
    }
}""",
        "junior_eval": "Puts kafkaTemplate.send() inside @Transactional or inside a try-catch block, falsely assuming Spring will rollback Kafka messages on DB exception.",
        "expert_eval": "Identifies the Dual-Write impossibility, designs the Outbox table within the ACID transaction boundary, and contrasts Polling Publisher vs WAL-based Debezium CDC."
    })

    # Q6: API Versioning & Zero-Downtime Evolution
    questions.append({
        "id": 6,
        "badge": "API Lifecycle & Contract Evolution",
        "keywords": "api versioning uri path header content negotiation breaking changes sunset expand contract",
        "concept": "API Versioning strategies (URI path, Header, Media Type negotiation), Expand-and-Contract schema evolution, Tolerant Reader pattern, and deprecation lifecycle headers (<code>Sunset</code>).",
        "question": """A user profile API needs to split the single field <code>fullName</code> into two distinct fields: <code>firstName</code> and <code>lastName</code>. Look at the code snippet.
<br><br>
<strong>Part A:</strong> What are the architectural trade-offs between URI path versioning (<code>/v1/users</code> vs <code>/v2/users</code>) versus Media Type Content Negotiation (<code>Accept: application/vnd.company.v2+json</code>)?
<br>
<strong>Part B:</strong> Mobile app clients cannot be forced to update immediately, and older versions will continue calling the API for up to 18 months. How do you design an <strong>Expand and Contract</strong> pattern to evolve the API with zero downtime?
<br>
<strong>Part C:</strong> What standard HTTP headers should be returned to programmatically inform API consumers that an endpoint or field is deprecated and will be decommissioned?""",
        "snippet_title": "UserProfileResponse.java",
        "snippet_code": """public class UserProfileResponse {
    private Long id;
    private String fullName;
    private String email;

    public UserProfileResponse(Long id, String fullName, String email) {
        this.id = id;
        this.fullName = fullName;
        this.email = email;
    }

    public Long getId() { return id; }
    public String getFullName() { return fullName; }
    public String getEmail() { return email; }
}""",
        "rating_concept": "API Versioning, Expand-and-Contract schema migration, and HTTP Sunset deprecation headers",
        "solution": """<strong>Part A (URI Path vs Media Type Versioning):</strong>
<br>• <strong>URI Path (<code>/api/v1/users</code>):</strong>
<br><em>Pros:</em> Explicit, easily cached by CDNs and reverse proxies, visible in browser URL and API documentation.
<br><em>Cons:</em> Violates strict REST purism (a resource should have a single canonical URI; format/version is a representation).
<br>• <strong>Media Type / Header (<code>Accept: application/vnd.mycorp.user.v2+json</code>):</strong>
<br><em>Pros:</em> RESTful, keeps URI space clean, enables fine-grained content negotiation.
<br><em>Cons:</em> Difficult to test in browser, breaks naive proxy caching (requires <code>Vary: Accept</code>), harder for mobile client teams to configure.
<br><br>
<strong>Part B (Expand and Contract Pattern):</strong>
<br>1. <strong>Phase 1 (Expand):</strong> Add new fields <code>firstName</code> and <code>lastName</code> to the DTO without removing <code>fullName</code>. Populate both in the backend. Old clients continue reading <code>fullName</code>; new clients read the split fields.
<br>2. <strong>Phase 2 (Migrate):</strong> Transition consumers to the new fields over the grace period. Ensure consumers use <strong>Tolerant Reader</strong> (ignoring unknown JSON fields).
<br>3. <strong>Phase 3 (Contract):</strong> After deprecation notice, remove <code>fullName</code>.
<br><br>
<strong>Part C (RFC 8594 Sunset & Deprecation Headers):</strong>
<br>• <code>Deprecation: @1735689600</code> (indicates when the API was deprecated).
<br>• <code>Sunset: Tue, 01 Dec 2026 00:00:00 GMT</code> (formal RFC 8594 header specifying the exact date the endpoint will be permanently terminated).
<br>• <code>Link: &lt;https://api.mycorp.com/docs/v2-migration&gt;; rel="deprecation"</code>.""",
        "optimized_code": """@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonIgnoreProperties(ignoreUnknown = true)
public class EvolvingUserResponse {
    private Long id;
    private String firstName;
    private String lastName;
    private String fullName;

    public EvolvingUserResponse(Long id, String first, String last) {
        this.id = id;
        this.firstName = first;
        this.lastName = last;
        this.fullName = first + " " + last;
    }
}""",
        "junior_eval": "Changes the fields immediately or creates a completely separate parallel microservice clone just to rename a JSON property.",
        "expert_eval": "Contrasts URI vs Content-Negotiation caching impacts, designs a 3-stage Expand-and-Contract lifecycle with Tolerant Readers, and integrates RFC 8594 Sunset headers."
    })

    # Q7: Distributed Rate Limiting & Redis Lua
    questions.append({
        "id": 7,
        "badge": "API Gateway & Traffic Control",
        "keywords": "rate limiting token bucket leaky bucket sliding window redis lua script race condition 429",
        "concept": "Distributed Rate Limiting algorithms (Token Bucket, Leaky Bucket, Sliding Window Log), atomic Redis Lua scripting, handling microsecond race conditions, and HTTP 429 <code>Retry-After</code> headers.",
        "question": """A public API gateway protects microservices from DDoS and quota abuse by enforcing 100 requests per minute per API key. Look at the code snippet.
<br><br>
<strong>Part A:</strong> Explain why the two-step Redis operations in the code snippet fail under concurrent traffic and allow malicious clients to exceed the quota.
<br>
<strong>Part B:</strong> Compare the <strong>Token Bucket</strong> algorithm against the <strong>Fixed Window Counter</strong> algorithm. What is the boundary burst problem in Fixed Window?
<br>
<strong>Part C:</strong> How do you write an atomic Redis Lua script to implement a sliding window rate limiter, and what standard HTTP headers must accompany an HTTP 429 response?""",
        "snippet_title": "NaiveRateLimitFilter.java",
        "snippet_code": """@Component
public class NaiveRateLimitFilter implements Filter {

    @Autowired
    private StringRedisTemplate redisTemplate;

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) 
            throws IOException, ServletException {
        
        HttpServletRequest req = (HttpServletRequest) request;
        HttpServletResponse res = (HttpServletResponse) response;
        String apiKey = req.getHeader("X-API-KEY");

        String currentCount = redisTemplate.opsForValue().get("ratelimit:" + apiKey);

        if (currentCount != null && Integer.parseInt(currentCount) >= 100) {
            res.setStatus(429);
            res.getWriter().write("Too Many Requests");
            return;
        }

        redisTemplate.opsForValue().increment("ratelimit:" + apiKey);
        redisTemplate.expire("ratelimit:" + apiKey, Duration.ofMinutes(1));

        chain.doFilter(request, response);
    }
}""",
        "rating_concept": "Distributed Rate Limiting, atomic Redis Lua script execution, and Token Bucket algorithm",
        "solution": """<strong>Part A (The Race Conditions in Naive Rate Limiting):</strong>
<br>1. <strong>TOCTOU Race:</strong> If 50 concurrent requests arrive simultaneously, all 50 call <code>get()</code> when count is 99. All 50 pass the <code>< 100</code> check, resulting in 149 requests processed.
<br>2. <strong>Key Expiration Reset Race:</strong> Every request calls <code>expire()</code>, resetting the TTL to 1 minute from the latest request! An active user will never have their window reset and will be locked out permanently.
<br><br>
<strong>Part B (Boundary Burst Problem vs Token Bucket):</strong>
<br>• <strong>Fixed Window Flaw:</strong> If quota is 100 req/min, a user can send 100 requests at 10:00:59 and another 100 requests at 10:01:01. In that 2-second span, 200 requests pass &mdash; a 2x burst that can crash backend databases.
<br>• <strong>Token Bucket:</strong> Tokens refill smoothly at a constant rate (e.g. 1.66 tokens/sec) up to bucket capacity (100). Accommodates brief bursts without exceeding configured throughput.
<br><br>
<strong>Part C (Atomic Redis Lua Script & Standard Headers):</strong>
<br>By executing within a Redis Lua script, the sliding window check, increment, and expiration execute <strong>atomically</strong> on the single-threaded Redis engine without client-server network roundtrips.
<br>Standard headers returned on 429:
<br>• <code>X-RateLimit-Limit: 100</code>
<br>• <code>X-RateLimit-Remaining: 0</code>
<br>• <code>X-RateLimit-Reset: 1735689660</code> (epoch seconds)
<br>• <code>Retry-After: 42</code> (seconds until retry permitted).""",
        "optimized_code": """-- Redis Lua Script for Sliding Window Rate Limiter
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])

redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
local current = redis.call('ZCARD', key)

if current < limit then
    redis.call('ZADD', key, now, now)
    redis.call('EXPIRE', key, math.ceil(window / 1000))
    return 1
else
    return 0
end""",
        "junior_eval": "Uses an in-memory HashMap/AtomicInteger (useless across multiple load-balanced pods) or fails to see the race condition between Redis get, increment, and expire.",
        "expert_eval": "Identifies the multi-command race condition, diagrams the 2x boundary burst flaw of fixed windows, writes atomic Redis Lua scripts with sorted sets (ZSET), and supplies RFC rate-limiting headers."
    })

    # Q8: gRPC & Protobuf vs REST & JSON
    questions.append({
        "id": 8,
        "badge": "High-Performance RPC & Protocols",
        "keywords": "grpc protobuf rest json http2 multiplexing binary serialization schema evolution",
        "concept": "High-performance inter-service communication, gRPC over HTTP/2 vs REST over HTTP/1.1, binary Protocol Buffers serialization, multiplexing, and bidirectional streaming.",
        "question": """An IoT microservices backend ingests sensor metrics and dispatches internal calculations between 150 backend services. Look at the code snippet.
<br><br>
<strong>Part A:</strong> Why does REST over HTTP/1.1 with JSON cause CPU and network bottlenecks at millions of requests per second compared to gRPC with Protocol Buffers?
<br>
<strong>Part B:</strong> How does HTTP/2 multiplexing eliminate Head-of-Line (HoL) blocking at the application transport layer, and what is the difference between TCP HoL blocking and HTTP/1.1 HoL blocking?
<br>
<strong>Part C:</strong> How does Protobuf achieve backward and forward schema compatibility without breaking deployed clients when new fields are added or existing fields are deprecated?""",
        "snippet_title": "TelemetryIngestController.java",
        "snippet_code": """@RestController
@RequestMapping("/api/v1/telemetry")
public class TelemetryIngestController {

    @Autowired
    private RestTemplate restTemplate;

    @PostMapping("/stream")
    public ResponseEntity<Void> receiveReading(@RequestBody SensorReadingPayload payload) {
        // Dispatches to internal compute engine via REST
        restTemplate.postForLocation("http://internal-compute/calc", payload);
        return ResponseEntity.accepted().build();
    }
}""",
        "rating_concept": "gRPC vs REST, Protobuf binary encoding efficiency, and HTTP/2 multiplexing",
        "solution": """<strong>Part A (JSON & HTTP/1.1 Inefficiencies):</strong>
<br>• <strong>Text Parsing CPU Overhead:</strong> JSON serialization and deserialization (Jackson) involves heavy string parsing, reflection, and character encoding, consuming 4-8x more CPU cycles than binary Protobuf.
<br>• <strong>Wire Size:</strong> JSON payload includes repetitive ASCII field names (e.g. <code>\"sensorIdentifier\"</code>) on every packet. Protobuf uses compact tag-length-value binary encoding (varints).
<br>• <strong>Socket Thrashing:</strong> HTTP/1.1 requires one TCP connection per concurrent in-flight request (or connection keep-alive queuing).
<br><br>
<strong>Part B (Multiplexing & Head-of-Line Blocking):</strong>
<br>• <strong>HTTP/1.1 HoL Blocking:</strong> A client can only send one request at a time per TCP connection; subsequent requests must wait in line until the first response arrives.
<br>• <strong>HTTP/2 Multiplexing:</strong> Binary streams are interleaved as independent frames over a <strong>single persistent TCP connection</strong>. Multiple requests and responses fly concurrently without blocking each other.
<br>• <em>Note:</em> TCP HoL blocking can still occur at the kernel packet loss level (fixed in HTTP/3 QUIC over UDP).
<br><br>
<strong>Part C (Protobuf Field Tag Compatibility Rules):</strong>
<br>• Protobuf identifies fields by <strong>numeric field tags</strong> (e.g., <code>string device_id = 1;</code>), never by variable name.
<br>• When adding fields, allocate new tag numbers. Old clients encountering new tags safely skip them.
<br>• <strong>Never change existing tag numbers</strong> or data types. Deprecated fields are marked <code>reserved</code> to prevent reuse.""",
        "optimized_code": """syntax = "proto3";
package telemetry;

message SensorReading {
    int64 timestamp = 1;
    string device_id = 2;
    double temperature = 3;
    double pressure = 4;
    reserved 5, 6; // Reserved retired tags
}

service TelemetryComputeService {
    rpc StreamReadings (stream SensorReading) returns (ComputeSummary);
}""",
        "junior_eval": "Suggests compressing JSON with Gzip or adding more Tomcat threads, without understanding socket exhaustion, HTTP/1.1 pipeline stalls, or binary serialization gains.",
        "expert_eval": "Contrasts JSON reflection overhead with Protobuf varint binary parsing, explains HTTP/2 binary frame multiplexing, and outlines Protobuf field tag backwards compatibility rules."
    })

    # Q9: Dynamic Configuration & @RefreshScope
    questions.append({
        "id": 9,
        "badge": "Configuration & Cloud Native Operations",
        "keywords": "refreshscope spring cloud config actuator refresh dynamic configuration vault",
        "concept": "Runtime configuration reloading without pod restarts, Spring Cloud Config / HashiCorp Vault, <code>@RefreshScope</code> proxy mechanics, and thread-safe dynamic property updates.",
        "question": """A microservice needs to dynamically reload feature toggles and database connection timeouts fetched from HashiCorp Vault or Git without restarting the Kubernetes pods. Look at the code snippet.
<br><br>
<strong>Part A:</strong> Why does modifying <code>payment.gateway.timeoutMs</code> in the config server fail to take effect in <code>PaymentClientService</code> even after triggering <code>POST /actuator/refresh</code>?
<br>
<strong>Part B:</strong> Explain the internal lifecycle and proxy mechanics of Spring's <code>@RefreshScope</code>. What happens to active threads calling a bean when a refresh event is triggered?
<br>
<strong>Part C:</strong> What are the risks of using <code>@RefreshScope</code> on beans that manage stateful thread pools or database connection pools (such as HikariCP)?""",
        "snippet_title": "PaymentClientService.java",
        "snippet_code": """@Service
public class PaymentClientService {

    @Value("${payment.gateway.timeoutMs:3000}")
    private int timeoutMs;

    @Value("${feature.enableInstantSettlement:false}")
    private boolean instantSettlement;

    public void processPayment(PaymentRequest req) {
        if (instantSettlement) {
            executeInstant(req, timeoutMs);
        } else {
            executeStandard(req);
        }
    }

    private void executeInstant(PaymentRequest req, int timeout) {}
    private void executeStandard(PaymentRequest req) {}
}""",
        "rating_concept": "@RefreshScope proxy lifecycle, runtime config reload, and connection pool risks",
        "solution": """<strong>Part A (Singleton Bean Initialization Immobility):</strong>
<br>Spring beans are <strong>singletons</strong> by default. During container startup, <code>@Value</code> properties are resolved and injected into the fields once.
<br>When <code>/actuator/refresh</code> is called, the <code>Environment</code> properties in memory are updated, but already instantiated singleton beans are <strong>never reinjected</strong>. Their fields remain permanently frozen with initial startup values.
<br><br>
<strong>Part B (@RefreshScope CGLIB Proxy Mechanics):</strong>
<br>• When a class is annotated with <code>@RefreshScope</code>, Spring wraps it in a CGLIB lazy proxy.
<br>• The proxy maintains a target bean cache. When client code calls a method on the proxy, it fetches the real bean instance from <code>GenericScope</code>.
<br>• When <code>/actuator/refresh</code> triggers a <code>RefreshEvent</code>, <code>RefreshScope.destroy()</code> clears the bean cache.
<br>• On the very next method invocation, the proxy detects a cache miss, reinstantiates the bean, and reinjects the fresh properties from the updated <code>Environment</code>.
<br><br>
<strong>Part C (Risks with Pools and Stateful Resources):</strong>
<br>Reinstantiating a bean holding a database connection pool (HikariCP) or an Executor thread pool destroys the underlying sockets and worker threads. In-flight transactions can be abruptly aborted with <code>SocketException</code>. Dynamic reload should only be applied to stateless configurations or bound via <code>@ConfigurationProperties</code>.""",
        "optimized_code": """@Service
@RefreshScope
public class PaymentClientService {

    @Autowired
    private PaymentProperties props;

    public void processPayment(PaymentRequest req) {
        if (props.isInstantSettlement()) {
            executeInstant(req, props.getTimeoutMs());
        } else {
            executeStandard(req);
        }
    }
}

@ConfigurationProperties(prefix = "payment.gateway")
public class PaymentProperties {
    private int timeoutMs = 3000;
    private boolean instantSettlement = false;
    // getters and setters
}""",
        "junior_eval": "Assumes @Value updates automatically at runtime or recommends restarting the entire Kubernetes deployment to change a feature flag.",
        "expert_eval": "Explains CGLIB proxy target destruction on RefreshEvent, warns against placing @RefreshScope on connection pools, and advocates @ConfigurationProperties binding."
    })

    # Q10: CQRS & Read-Your-Own-Writes Consistency
    questions.append({
        "id": 10,
        "badge": "Distributed Data & Read Optimization",
        "keywords": "cqrs read your own writes eventual consistency elasticsearch event sourcing lag",
        "concept": "Command Query Responsibility Segregation (CQRS), dual datastores (RDBMS write vs Elasticsearch/Redis read), replication lag, and guaranteeing Read-Your-Own-Writes consistency.",
        "question": """In a high-scale e-commerce platform, write commands persist orders into PostgreSQL, while search queries hit an optimized Elasticsearch cluster synced asynchronously via Kafka. Look at the code snippet.
<br><br>
<strong>Part A:</strong> A customer completes an order and is immediately redirected to the \"Recent Orders\" page. The page displays \"No Orders Found!\" because of a 300ms Kafka-to-Elasticsearch replication lag. What is this user experience anomaly called?
<br>
<strong>Part B:</strong> What are three architectural strategies to guarantee <strong>Read-Your-Own-Writes</strong> consistency in an eventually consistent CQRS system without crippling read performance?
<br>
<strong>Part C:</strong> Under what conditions does the complexity of CQRS outweigh its benefits? When should an architect reject CQRS in favor of a unified relational database?""",
        "snippet_title": "OrderCommandQueryController.java",
        "snippet_code": """@RestController
@RequestMapping("/api/v1/orders")
public class OrderCommandQueryController {

    @Autowired
    private OrderCommandService commandService;

    @Autowired
    private OrderElasticsearchRepository searchRepo;

    @PostMapping
    public ResponseEntity<OrderCreatedResponse> placeOrder(@RequestBody OrderRequest req) {
        Long orderId = commandService.createOrder(req);
        return ResponseEntity.ok(new OrderCreatedResponse(orderId));
    }

    @GetMapping("/user/{userId}")
    public ResponseEntity<List<OrderDocument>> getCustomerOrders(@PathVariable String userId) {
        List<OrderDocument> orders = searchRepo.findByUserIdOrderByDateDesc(userId);
        return ResponseEntity.ok(orders);
    }
}""",
        "rating_concept": "CQRS architecture, eventual consistency replication lag, and Read-Your-Own-Writes solutions",
        "solution": """<strong>Part A (Replication Lag & Inconsistent Read Anomaly):</strong>
<br>This is the classic <strong>Eventual Consistency Read-After-Write Anomaly</strong> (or lack of Read-Your-Own-Writes guarantee).
<br>Because the asynchronous pipeline (PostgreSQL &rarr; Outbox &rarr; Kafka &rarr; Consumer &rarr; Elasticsearch) takes 100&ndash;500ms to index, a rapid user redirect hits an outdated search index replica before synchronization finishes.
<br><br>
<strong>Part B (Architectural Strategies for Read-Your-Own-Writes):</strong>
<br>1. <strong>Session/Version Token Pinning:</strong> Return an updated transaction version ID or timestamp in the POST response. The client passes this token on GET. If the read replica has not caught up to this version, the query routes temporarily to the <strong>primary PostgreSQL database</strong>.
<br>2. <strong>Time-Window Primary Routing:</strong> If the user modified records within the last $N$ seconds (tracked via Redis or client cookies), direct their personal dashboard reads to PostgreSQL; all other users and broad searches read from Elasticsearch.
<br>3. <strong>Optimistic Client-Side State:</strong> Immediately inject the newly created order into the client UI state (Redux/Angular Signal) on HTTP 200, bypassing the immediate read query entirely.
<br><br>
<strong>Part C (When to Reject CQRS):</strong>
<br>Reject CQRS if the domain has low read-to-write ratio (1:1), simple CRUD queries, small datasets, or strict real-time consistency requirements across all users. Adding separate write/read stores introduces event loss risks, schema sync overhead, and operational maintenance.""",
        "optimized_code": """@GetMapping("/user/{userId}")
public ResponseEntity<List<OrderDTO>> getCustomerOrders(
        @PathVariable String userId,
        @RequestHeader(value = "X-Recent-Write-Time", required = false) Long lastWriteTime) {

    long threshold = System.currentTimeMillis() - 5000; // 5 second grace window
    if (lastWriteTime != null && lastWriteTime > threshold) {
        return ResponseEntity.ok(orderPostgresService.findByUserId(userId));
    }
    return ResponseEntity.ok(orderSearchService.findByUserId(userId));
}""",
        "junior_eval": "Suggests making the write method wait (Thread.sleep(500)) or synchronously writes to both PostgreSQL and Elasticsearch in the HTTP request thread.",
        "expert_eval": "Identifies eventual consistency read-after-write hazards, implements version token or time-windowed routing to primary datastore, and evaluates CQRS complexity trade-offs."
    })

    # Q11: OAuth2 & Token Relay
    questions.append({
        "id": 11,
        "badge": "Microservices Security & Identity",
        "keywords": "oauth2 jwt jwk token relay api gateway authorization header mtls zero trust",
        "concept": "Microservices security architecture, OAuth 2.0 / OIDC Token Relay pattern via API Gateway, stateless JWT validation vs JWK Set caching, and downstream service-to-service zero-trust identity.",
        "question": """In a microservices ecosystem, client requests enter via Spring Cloud Gateway and call Microservice A, which calls Microservice B. Look at the code snippet.
<br><br>
<strong>Part A:</strong> Microservice A accepts incoming user requests, but when it invokes Microservice B via <code>WebClient</code>, Microservice B rejects the call with <code>HTTP 401 Unauthorized</code>. Why does this happen, and how does the <strong>Token Relay Pattern</strong> solve it?
<br>
<strong>Part B:</strong> What is the danger of downstream microservices blindly calling the Identity Provider (IdP) <code>/oauth/check_token</code> or re-downloading JWKs on every single internal HTTP request? How should JWK caching and rotation be handled?
<br>
<strong>Part C:</strong> If Microservice A strips the user's JWT and passes plain headers like <code>X-User-Id: 1042</code> to internal microservices, what security vulnerability does this introduce?""",
        "snippet_title": "OrderToInventoryClient.java",
        "snippet_code": """@Service
public class OrderToInventoryClient {

    @Autowired
    private WebClient webClient;

    public InventoryStatus checkStock(String sku) {
        return webClient.get()
            .uri("http://inventory-service/api/stock/{sku}", sku)
            .retrieve()
            .bodyToMono(InventoryStatus.class)
            .block();
    }
}""",
        "rating_concept": "OAuth2 Token Relay pattern, JWK caching, and internal service identity propagation",
        "solution": """<strong>Part A (Header Dropping Across Network Hops):</strong>
<br>• By default, <code>WebClient</code> or <code>RestTemplate</code> does not inherit headers from the incoming Servlet/Reactive request.
<br>• The <code>Authorization: Bearer &lt;JWT&gt;</code> header is dropped. When Microservice B receives the request with no Authorization header, its Spring Security filter rejects it with 401 Unauthorized.
<br>• <strong>Token Relay Pattern:</strong> An interceptor or filter extracts the active OAuth2 token from the SecurityContext and attaches it to the outgoing HTTP client headers.
<br><br>
<strong>Part B (IdP Overload & JWK Set Caching):</strong>
<br>• Downstream microservices must <strong>never</strong> make synchronous network calls to the IdP to validate stateless JWTs for every request; doing so turns the IdP into a catastrophic bottleneck and single point of failure.
<br>• Microservices should validate JWT signatures locally using the IdP's public keys fetched via <code>/.well-known/jwks.json</code>.
<br>• Keys are cached in memory with a TTL (e.g. 24 hours). If an unknown key ID (<code>kid</code>) is encountered, the cache initiates a single refresh to support key rotation without breaking existing tokens.
<br><br>
<strong>Part C (Header Spoofing & Broken Object Level Authorization):</strong>
<br>Passing raw unauthenticated headers like <code>X-User-Id</code> without cryptographic signatures allows any compromised service, container, or malicious insider on the private network to spoof any user ID, leading to massive privilege escalation and data theft.""",
        "optimized_code": """@Bean
public WebClient webClient(ServletOAuth2AuthorizedClientExchangeFilterFunction oauth2) {
    return WebClient.builder()
        .apply(oauth2.oauth2Configuration())
        .filter((request, next) -> {
            ServletRequestAttributes attrs = (ServletRequestAttributes) 
                RequestContextHolder.getRequestAttributes();
            if (attrs != null) {
                String token = attrs.getRequest().getHeader("Authorization");
                ClientRequest newReq = ClientRequest.from(request)
                    .header("Authorization", token).build();
                return next.exchange(newReq);
            }
            return next.exchange(request);
        }).build();
}""",
        "junior_eval": "Passes unverified user ID plaintext headers or suggests calling the IdP introspection endpoint synchronously on every internal hop.",
        "expert_eval": "Configures Token Relay filter across internal clients, validates JWT signatures locally with cached JWK Sets, and enforces Zero-Trust mTLS between internal pods."
    })

    # Q12: Reactive Backpressure & WebFlux
    questions.append({
        "id": 12,
        "badge": "Reactive Systems & Flow Control",
        "keywords": "reactive backpressure project reactor webflux flux mono onbackpressurebuffer outofmemoryerror",
        "concept": "Reactive Streams specification, backpressure flow control (<code>onBackpressureBuffer</code>, <code>onBackpressureDrop</code>), demand signaling via <code>Subscription.request(n)</code>, and memory overflow mitigation.",
        "question": """A financial market ticker microservice consumes a high-frequency real-time stock pricing feed emitting 50,000 updates/sec and streams it to client consumers. Look at the code snippet.
<br><br>
<strong>Part A:</strong> The downstream client writes quotes to a disk archive at only 5,000 records/sec. Within 2 minutes, the streaming microservice crashes with <code>java.lang.OutOfMemoryError: Java heap space</code>. Explain how the absence of backpressure caused this crash.
<br>
<strong>Part B:</strong> How does the Reactive Streams specification solve this problem through <strong>Demand Signaling</strong> (<code>request(n)</code>)?
<br>
<strong>Part C:</strong> Compare the architectural trade-offs of <code>onBackpressureDrop()</code>, <code>onBackpressureBuffer(maxSize)</code>, and <code>sample(duration)</code>. Which strategy is appropriate for financial real-time dashboards?""",
        "snippet_title": "MarketDataStreamService.java",
        "snippet_code": """@Service
public class MarketDataStreamService {

    @Autowired
    private MarketDataProvider externalFeed;

    public Flux<StockQuote> streamQuotes() {
        return Flux.create(emitter -> {
            externalFeed.registerListener(quote -> {
                emitter.next(quote);
            });
        });
    }
}""",
        "rating_concept": "Reactive Streams backpressure, demand signaling request(n), and flow control strategies",
        "solution": """<strong>Part A (Unbounded In-Memory Accumulation):</strong>
<br>• The publisher generates 50,000 objects per second while the consumer can only drain 5,000 per second.
<br>• <code>Flux.create()</code> by default uses an <strong>unbounded internal queue buffer</strong>.
<br>• In just 60 seconds, $45,000 \\times 60 = 2,700,000$ large Java objects accumulate in JVM Young/Old Gen memory. The GC goes into full stop-the-world cycles, throughput collapses, and the process dies of <code>OutOfMemoryError</code>.
<br><br>
<strong>Part B (Demand Signaling via Subscription.request(n)):</strong>
<br>• Reactive Streams inverts flow control: the <strong>Subscriber dictates the pace</strong> by calling <code>subscription.request(n)</code>.
<br>• The Publisher is not allowed to emit more than $n$ items until the Subscriber explicitly demands more.
<br>• If the data source is hot (hardware sensors, raw sockets), backpressure tells the intermediary layer how to discard, sample, or buffer items gracefully.
<br><br>
<strong>Part C (Backpressure Strategies Comparison):</strong>
<br>• <code>onBackpressureBuffer(size, BufferOverflowStrategy.DROP_OLDEST)</code>: Retains up to $N$ latest quotes, prevents memory exhaustion.
<br>• <code>onBackpressureDrop()</code>: Discards quotes immediately if consumer is saturated.
<br>• <code>sample(Duration.ofMillis(100))</code>: For financial dashboards, human eyes cannot see 50,000 updates/sec; sampling emits the most recent quote every 100ms, slashing load by 99% while preserving freshest price.""",
        "optimized_code": """@Service
public class ResilientMarketStream {

    public Flux<StockQuote> streamSafeQuotes() {
        return Flux.create(this::registerFeed, FluxSink.OverflowStrategy.DROP)
            .sample(Duration.ofMillis(100))
            .onBackpressureBuffer(1000, 
                dropped -> log.warn("Dropped stale quote for: {}", dropped.getSymbol()),
                BufferOverflowStrategy.DROP_OLDEST);
    }
}""",
        "junior_eval": "Suggests increasing JVM heap with -Xmx16g or switching to a standard Java BlockingQueue, missing the fundamental push-vs-pull flow mismatch.",
        "expert_eval": "Explains Reactive Streams pull-based demand signaling, diagnoses unbounded Flux.create memory buffers, and applies sampling and bounded buffer overflow policies."
    })

    # Q13: API Gateway & BFF Pattern
    questions.append({
        "id": 13,
        "badge": "Edge Architecture & Routing",
        "keywords": "api gateway bff backend for frontend spring cloud gateway esb single point of failure",
        "concept": "API Gateway design, Backend-For-Frontend (BFF) pattern, non-blocking routing engines (Netty), avoiding the Enterprise Service Bus (ESB) anti-pattern, and cross-cutting edge filters.",
        "question": """An enterprise migrates from a monolith to microservices and builds a single centralized Spring Cloud Gateway. Look at the code snippet.
<br><br>
<strong>Part A:</strong> Over time, the centralized API Gateway team has implemented JSON payload aggregation, customer eligibility calculation, and database lookups directly inside custom Gateway Filters. Why is this considered a dangerous <strong>ESB (Enterprise Service Bus) anti-pattern</strong>?
<br>
<strong>Part B:</strong> What is the <strong>Backend-For-Frontend (BFF)</strong> pattern, and why is having distinct BFFs for Mobile Clients vs Web Single-Page Applications (SPAs) preferable to a one-size-fits-all API Gateway?
<br>
<strong>Part C:</strong> What specific responsibilities belong strictly at the Edge Gateway layer versus internal downstream domain services?""",
        "snippet_title": "HeavyGatewayFilter.java",
        "snippet_code": """@Component
public class HeavyGatewayFilter implements GlobalFilter {

    @Autowired
    private RestTemplate restTemplate;

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String path = exchange.getRequest().getURI().getPath();
        
        if (path.startsWith("/api/checkout")) {
            // Synchronously querying customer credit and inventory in gateway
            CustomerCredit credit = restTemplate.getForObject("http://credit-svc/api/calc", CustomerCredit.class);
            if (credit.getScore() < 600) {
                exchange.getResponse().setStatusCode(HttpStatus.FORBIDDEN);
                return exchange.getResponse().setComplete();
            }
        }
        return chain.filter(exchange);
    }
}""",
        "rating_concept": "API Gateway architecture, BFF pattern, and ESB anti-pattern prevention",
        "solution": """<strong>Part A (The ESB Anti-Pattern & Organizational Bottleneck):</strong>
<br>• <strong>Blocking Netty Event Loop:</strong> Spring Cloud Gateway runs on an asynchronous non-blocking Netty engine. Using blocking <code>RestTemplate</code> inside a Gateway filter blocks Netty worker threads, crippling routing performance for all endpoints.
<br>• <strong>Coupling & Monolithic Rebirth:</strong> Encoding domain business rules into the gateway turns it into a \"smart pipe\" (ESB). The gateway team becomes a bottleneck for every feature release across all domain teams.
<br>• <strong>Blast Radius:</strong> A bug in checkout business logic can crash the gateway, taking down login, search, and the entire public infrastructure.
<br><br>
<strong>Part B (The Backend-For-Frontend Pattern):</strong>
<br>• Mobile clients require minimal JSON wire size, aggressive payload trimming, and batched endpoints to save cellular battery and bandwidth.
<br>• Web desktop clients have high bandwidth and need rich, multi-faceted data.
<br>• BFF creates dedicated, lightweight aggregation layers owned by the specific UI teams (e.g., <code>Mobile-BFF</code>, <code>Web-BFF</code>) rather than polluting domain services or the core gateway.
<br><br>
<strong>Part C (Gateway Responsibilities Matrix):</strong>
<br>• <em>Belongs in Gateway:</em> SSL termination, CORS, DDoS rate limiting, dynamic routing, edge JWT authentication, global request ID generation.
<br>• <em>Belongs in Domain/BFF:</em> Business validation, domain orchestration, payload aggregation, database access.""",
        "optimized_code": """// Clean Spring Cloud Gateway Configuration
@Configuration
public class GatewayRoutesConfig {

    @Bean
    public RouteLocator cleanRoutes(RouteLocatorBuilder builder) {
        return builder.routes()
            .route("mobile_bff", r -> r.path("/mobile/**")
                .filters(f -> f.stripPrefix(1)
                               .requestRateLimiter(c -> c.setRateLimiter(redisLimiter())))
                .uri("lb://MOBILE-BFF-SERVICE"))
            .route("web_bff", r -> r.path("/web/**")
                .filters(f -> f.stripPrefix(1))
                .uri("lb://WEB-BFF-SERVICE"))
            .build();
    }
}""",
        "junior_eval": "Places heavy business logic, database queries, and blocking HTTP calls inside the API Gateway, recreating a brittle Enterprise Service Bus.",
        "expert_eval": "Maintains 'Dumb Pipes, Smart Endpoints', prevents Netty event-loop blocking, articulates the BFF architectural model, and segregates edge concerns from domain logic."
    })

    # Q14: Consumer-Driven Contract Testing (Pact)
    questions.append({
        "id": 14,
        "badge": "Testing & Contract Verification",
        "keywords": "contract testing pact spring cloud contract consumer provider breaking changes ci cd",
        "concept": "Consumer-Driven Contract Testing (Pact / Spring Cloud Contract), preventing breaking API regressions, verifying provider expectations in CI/CD, and eliminating fragile end-to-end integration environments.",
        "question": """Order Service (Consumer) consumes the Customer Service (Provider) API. Look at the code snippet.
<br><br>
<strong>Part A:</strong> Customer Service refactors its internal model and renames the field <code>userId</code> to <code>accountId</code>. All unit tests in both repositories pass with 100% success. Why did production break immediately upon deployment?
<br>
<strong>Part B:</strong> Why are full end-to-end (E2E) testing environments across 50 deployed microservices considered slow, expensive, and unreliable for verifying API compatibility?
<br>
<strong>Part C:</strong> How does <strong>Consumer-Driven Contract Testing</strong> with Pact work? Explain the role of the Pact file, the Pact Broker, and how provider verification stops broken deployments in CI/CD.""",
        "snippet_title": "OrderCustomerClient.java",
        "snippet_code": """@Service
public class OrderCustomerClient {

    @Autowired
    private RestTemplate restTemplate;

    public CustomerDetails fetchCustomer(Long customerId) {
        // Expects: {"userId": 101, "tier": "GOLD", "email": "alice@corp.com"}
        return restTemplate.getForObject(
            "http://customer-service/api/customers/" + customerId, 
            CustomerDetails.class
        );
    }
}

public class CustomerDetails {
    private Long userId;
    private String tier;
    private String email;
    // getters and setters
}""",
        "rating_concept": "Consumer-Driven Contract Testing, Pact Broker, and breaking API change detection",
        "solution": """<strong>Part A (The Static Mocking Trap):</strong>
<br>In microservice testing, Consumer unit tests use mocked HTTP servers (WireMock) returning hard-coded static JSON.
<br>Provider unit tests mock their database and return their new entity.
<br>Both builds pass independently in isolation because neither tests against the other's real contract. When deployed to production, the Consumer deserializes <code>userId</code> as <code>null</code>, triggering <code>NullPointerException</code>.
<br><br>
<strong>Part B (Why Full E2E Environments Fail at Scale):</strong>
<br>• <strong>Flakiness:</strong> 50 microservices running concurrently suffer intermittent network blips, database state pollution, and deployment races.
<br>• <strong>Slow CI/CD:</strong> Deploying 50 containers to execute tests takes hours, stalling pull request velocity.
<br>• <strong>Environment Drift:</strong> Test environments rarely mirror production versions accurately.
<br><br>
<strong>Part C (Consumer-Driven Contract Testing Workflow):</strong>
<br>1. <strong>Consumer defines expectation:</strong> Order Service writes a test specifying exact requests it makes and minimal response fields it requires (Pact specification).
<br>2. <strong>Pact generation & publication:</strong> Test generates a JSON contract file, published to a central <strong>Pact Broker</strong>.
<br>3. <strong>Provider Verification in CI:</strong> When Customer Service runs its CI pipeline, it downloads the consumer contracts and replays real HTTP calls against its controllers. If <code>userId</code> is missing, provider build fails immediately &mdash; before deployment!""",
        "optimized_code": """// Consumer Pact Test
@Pact(consumer = "OrderService", provider = "CustomerService")
public V4Pact createCustomerPact(PactDslWithProvider builder) {
    return builder
        .given("Customer 101 exists")
        .uponReceiving("A request for customer details")
        .path("/api/customers/101")
        .method("GET")
        .willRespondWith()
        .status(200)
        .body(new PactDslJsonBody()
            .integerType("userId", 101)
            .stringType("tier", "GOLD")
            .stringType("email", "alice@corp.com"))
        .toPact(V4Pact.class);
}""",
        "junior_eval": "Advocates for a dedicated shared staging environment with all 50 services deployed or relies on brittle manual Postman smoke tests.",
        "expert_eval": "Explains why isolated mocks mask breaking schema drifts, contrasts E2E flakiness with contract testing, and describes the Pact Broker verification pipeline in CI/CD."
    })

    # Q15: Service Discovery & Client-Side Load Balancing
    questions.append({
        "id": 15,
        "badge": "Service Discovery & Topology",
        "keywords": "service discovery eureka consul spring cloud loadbalancer client side load balancing stale cache",
        "concept": "Service Discovery (Eureka, Consul, K8s CoreDNS), Client-Side Load Balancing (Spring Cloud LoadBalancer), heartbeat lease evictions, and stale cache race conditions.",
        "question": """In a high-throughput microservices architecture, Service A calls Service B using Spring Cloud LoadBalancer and Eureka/Consul. Look at the code snippet.
<br><br>
<strong>Part A:</strong> During a rolling deployment, an old pod of Service B is terminated by Kubernetes. For the next 30 seconds, 5% of requests from Service A fail with <code>ConnectException: Connection refused</code>. Why does this stale routing window occur?
<br>
<strong>Part B:</strong> What are the pros and cons of Client-Side Load Balancing (Spring Cloud LoadBalancer) versus Server-Side Load Balancing (AWS Application Load Balancer / Nginx)?
<br>
<strong>Part C:</strong> How do you eliminate the stale pod routing window during rolling deployments using Kubernetes readiness probes, preStop lifecycle hooks, and client-side retry policies?""",
        "snippet_title": "LoadBalancedClientConfig.java",
        "snippet_code": """@Configuration
public class LoadBalancedClientConfig {

    @Bean
    @LoadBalanced
    public WebClient.Builder loadBalancedWebClientBuilder() {
        return WebClient.builder();
    }
}

@Service
public class OrderDispatcherService {

    @Autowired
    private WebClient.Builder webClientBuilder;

    public void dispatch(OrderNotification notification) {
        webClientBuilder.build()
            .post()
            .uri("http://notification-service/api/notify")
            .bodyValue(notification)
            .retrieve()
            .toBodilessEntity()
            .block();
    }
}""",
        "rating_concept": "Service discovery stale cache eviction, client-side load balancing, and zero-downtime rolling deploys",
        "solution": """<strong>Part A (The Multi-Tier Cache Invalidation Lag):</strong>
<br>A stale routing window happens due to compound cache expiration delays:
<br>1. Service B terminates, but Eureka/Consul server only evicts it after missing heartbeats (default 30&ndash;90 seconds).
<br>2. Service A caches the Eureka server registry locally and only refreshes every 30 seconds.
<br>3. Until Service A's local cache expires, Spring Cloud LoadBalancer continues routing round-robin requests to the dead pod's dead IP address.
<br><br>
<strong>Part B (Client-Side vs Server-Side Load Balancing):</strong>
<br>• <strong>Client-Side (Spring Cloud LoadBalancer):</strong>
<br><em>Pros:</em> Direct pod-to-pod networking (zero intermediate network hop, lower latency), smart application-aware routing algorithms.
<br><em>Cons:</em> Language-dependent libraries, requires local discovery cache management, client library maintenance.
<br>• <strong>Server-Side (ALB / Envoy):</strong>
<br><em>Pros:</em> Polyglot, language-agnostic, centralized TLS/health management.
<br><em>Cons:</em> Extra network hop, higher infrastructure cost, potential central bottleneck.
<br><br>
<strong>Part C (Eliminating the Stale Window):</strong>
<br>1. <strong>Kubernetes preStop Hook:</strong> Add <code>sleep 15</code> in pod <code>preStop</code> so pod deregisters from endpoints before Kubernetes sends SIGTERM to the application.
<br>2. <strong>Readiness Probe:</strong> Fail readiness probe before shutdown.
<br>3. <strong>Client-Side Retry Policy:</strong> Configure Spring Cloud LoadBalancer with automatic retry on <code>ConnectException</code> to immediately re-route to an alternate instance.""",
        "optimized_code": """# Kubernetes Deployment preStop hook
spec:
  containers:
  - name: notification-service
    lifecycle:
      preStop:
        exec:
          command: ["/bin/sh", "-c", "sleep 15"]

# Spring Retry Configuration
spring:
  cloud:
    loadbalancer:
      retry:
        enabled: true
        retry-on-next-instance: 1""",
        "junior_eval": "Suggests completely disabling caching in Service Discovery (which will crash Eureka/Consul under heavy traffic with millions of registry requests).",
        "expert_eval": "Pinpoints the multi-tiered cache invalidation delay, compares Client-Side vs Server-Side proxy trade-offs, and aligns Kubernetes preStop hooks with client-side retry policies."
    })

    # Q16: Dead Letter Queues & Retry Storms
    questions.append({
        "id": 16,
        "badge": "Messaging & Asynchronous Resilience",
        "keywords": "dead letter queue dlq poison pill kafka retry storm exponential backoff jitter non blocking retry",
        "concept": "Dead Letter Queues (DLQ), poison pill handling in Kafka consumers, avoiding partition-blocking retries, exponential backoff with full jitter, and non-blocking retry topics.",
        "question": """A billing microservice consumes payment events from an Apache Kafka partition. Look at the code snippet.
<br><br>
<strong>Part A:</strong> A malformed event with corrupted JSON (a \"poison pill\") arrives on partition 0. What happens to the consumer under the default Spring Kafka / Kafka listener error handling? How does this block all subsequent valid payments?
<br>
<strong>Part B:</strong> If 1,000 consumers encounter a transient third-party outage and all retry simultaneously on a fixed 1-second timer, explain what a <strong>Retry Storm</strong> (Thundering Herd) is and how <strong>Exponential Backoff with Full Jitter</strong> mitigates it.
<br>
<strong>Part C:</strong> Describe how to implement <strong>Non-Blocking Retry Topics</strong> in Spring Kafka (e.g. <code>topic-order-retry-10s</code>, <code>topic-order-dlt</code>) so that slow or retried messages do not block head-of-line processing for other customers.""",
        "snippet_title": "BillingEventConsumer.java",
        "snippet_code": """@Component
public class BillingEventConsumer {

    @Autowired
    private BillingProcessor processor;

    @KafkaListener(topics = "billing-events", groupId = "billing-group")
    public void consume(ConsumerRecord<String, String> record) {
        // Unhandled exception thrown here on malformed JSON or downstream 500
        BillingEvent event = JsonUtil.deserialize(record.value(), BillingEvent.class);
        processor.process(event);
    }
}""",
        "rating_concept": "Dead Letter Queues (DLQ), Kafka poison pill recovery, and non-blocking retry topics",
        "solution": """<strong>Part A (The Poison Pill & Head-of-Line Partition Lock):</strong>
<br>• Kafka partitions maintain an ordered offset. An offset is only committed when a record is successfully processed.
<br>• When <code>deserialize()</code> throws an unhandled exception, Kafka's default listener attempts to re-read the exact same offset.
<br>• Because the message is permanently corrupt, it will fail every retry forever.
<br>• As a result, the consumer partition is <strong>completely halted</strong>. All subsequent valid customer transactions behind that offset on the same partition are blocked indefinitely.
<br><br>
<strong>Part B (Retry Storms & Full Jitter):</strong>
<br>• When downstream dependencies experience transient failures, thousands of worker threads retrying at fixed synchronized intervals (e.g., exactly every 2 seconds) produce massive synchronized spikes of traffic, crushing the recovering downstream service.
<br>• <strong>Full Jitter Formula:</strong> <code>Sleep = random(0, min(max_sleep, base * 2 ^ attempt))</code>
<br>• Jitter smooths the retry distribution evenly across time, eliminating synchronized thundering herd spikes.
<br><br>
<strong>Part C (Non-Blocking Retry Topics via @RetryableTopic):</strong>
<br>• If a message fails, instead of pausing the main partition, forward the message to a delayed retry topic (e.g. <code>billing-events-retry-10s</code>) and commit the main offset.
<br>• Healthy messages on the main partition continue flowing with zero latency.
<br>• After max attempts, forward the message to the Dead Letter Topic (DLT) for engineering triage and alerting.""",
        "optimized_code": """@Component
public class ResilientBillingConsumer {

    @RetryableTopic(
        attempts = "4",
        backoff = @Backoff(delay = 1000, multiplier = 2.0, maxDelay = 10000, random = true),
        dltStrategy = DltStrategy.FAIL_ON_ERROR,
        include = { TransientApiException.class }
    )
    @KafkaListener(topics = "billing-events", groupId = "billing-group")
    public void consume(BillingEvent event) {
        processor.process(event);
    }

    @DltHandler
    public void handleDlt(BillingEvent event, @Header(KafkaHeaders.RECEIVED_TOPIC) String topic) {
        log.error("Event permanently failed and routed to DLT: {}", event);
        alertManager.notifyOnCall(event);
    }
}""",
        "junior_eval": "Catches the exception and swallows it (silent message loss) or enters an infinite retry loop that freezes the entire Kafka partition.",
        "expert_eval": "Diagnoses Head-of-Line partition blocking, applies exponential backoff with full jitter, configures @RetryableTopic for non-blocking retry topics, and establishes Dead Letter Topic alerting."
    })

    # Q17: Bulkhead Pattern & Resource Isolation
    questions.append({
        "id": 17,
        "badge": "Fault Isolation & Resource Management",
        "keywords": "bulkhead pattern resource isolation thread pool semaphore cataclysmic failure tomcat",
        "concept": "The Bulkhead Pattern, preventing single-dependency failure from consuming shared JVM resources, Thread Pool Isolation vs Semaphore Isolation, and protecting critical revenue paths.",
        "question": """A single monolithic Spring Boot microservice handles both high-frequency Order Placement and long-running PDF Invoice Generation. Look at the code snippet.
<br><br>
<strong>Part A:</strong> At the end of the month, corporate users request 300 large PDF invoices simultaneously. Within seconds, customer order placement (<code>/api/orders</code>) grinds to a halt and times out, even though the order database is completely healthy. Explain why.
<br>
<strong>Part B:</strong> Compare <strong>Thread Pool Isolation</strong> versus <strong>Semaphore Isolation</strong> in implementing the Bulkhead pattern. What are the CPU and memory trade-offs?
<br>
<strong>Part C:</strong> How do you configure a Resilience4j Bulkhead to guarantee that slow PDF generation requests can never consume more than 10 concurrent slots, leaving the remaining 190 server threads for customer orders?""",
        "snippet_title": "OrderAndInvoiceService.java",
        "snippet_code": """@RestController
@RequestMapping("/api")
public class OrderAndInvoiceService {

    @Autowired
    private OrderService orderService;
    @Autowired
    private PdfGeneratorService pdfService;

    @PostMapping("/orders")
    public ResponseEntity<OrderResult> placeOrder(@RequestBody OrderCommand cmd) {
        return ResponseEntity.ok(orderService.submit(cmd));
    }

    @GetMapping("/invoices/{id}/download")
    public ResponseEntity<byte[]> downloadInvoice(@PathVariable String id) {
        // Takes 8-15 seconds of CPU and memory per call
        byte[] pdf = pdfService.generateHeavyReport(id);
        return ResponseEntity.ok(pdf);
    }
}""",
        "rating_concept": "Bulkhead Pattern, Thread Pool vs Semaphore isolation, and thread starvation prevention",
        "solution": """<strong>Part A (Unbounded Resource Contention in Shared Thread Pool):</strong>
<br>• Tomcat handles all incoming HTTP requests via a single shared thread pool (default 200 threads).
<br>• When 200 users hit <code>/invoices/download</code>, all 200 worker threads become blocked performing heavy CPU rendering and I/O for 15 seconds.
<br>• When a high-priority customer calls <code>/orders</code> (which takes only 20ms), there are <strong>zero free threads</strong> available in the pool. The order request waits in the operating system socket backlog until it times out.
<br><br>
<strong>Part B (Thread Pool vs Semaphore Isolation):</strong>
<br>• <strong>Thread Pool Bulkhead:</strong>
<br>Executes task on a separate dedicated thread pool.
<br><em>Pros:</em> Supports asynchronous execution and hard timeouts (thread interruption).
<br><em>Cons:</em> High memory overhead per thread (1MB stack) and CPU context switching overhead.
<br>• <strong>Semaphore Bulkhead:</strong>
<br>Limits concurrent callers using an atomic counter on the calling thread.
<br><em>Pros:</em> Extremely fast, zero context switching overhead, sub-microsecond latency.
<br><em>Cons:</em> Executes on the caller's thread; cannot enforce hard preemptive timeouts.
<br><br>
<strong>Part C (Resilience4j Bulkhead Configuration):</strong>
<br>Apply <code>@Bulkhead(name = "pdfBulkhead", type = Bulkhead.Type.SEMAPHORE)</code> with <code>maxConcurrentCalls = 10</code>. The 11th concurrent caller is immediately rejected with HTTP 429 or queued with a strict maxWaitDuration (e.g. 50ms).""",
        "optimized_code": """// application.yml Resilience4j Bulkhead
resilience4j:
  bulkhead:
    instances:
      pdfReport:
        maxConcurrentCalls: 10
        maxWaitDuration: 10ms

// Controller
@GetMapping("/invoices/{id}/download")
@Bulkhead(name = "pdfReport", fallbackMethod = "reportBusyFallback")
public ResponseEntity<byte[]> downloadInvoice(@PathVariable String id) {
    return ResponseEntity.ok(pdfService.generateHeavyReport(id));
}

public ResponseEntity<byte[]> reportBusyFallback(String id, BulkheadFullException ex) {
    return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
        .header("Retry-After", "30").body(null);
}""",
        "junior_eval": "Suggests increasing server.tomcat.threads.max from 200 to 2,000, worsening CPU context switching and accelerating OutOfMemoryError.",
        "expert_eval": "Explains thread starvation across disparate workloads, compares Thread Pool vs Semaphore isolation mechanics, and configures bounded Bulkheads to protect critical revenue endpoints."
    })

    # Q18: Service Mesh & Zero-Trust mTLS
    questions.append({
        "id": 18,
        "badge": "Infrastructure & Service Mesh",
        "keywords": "service mesh istio envoy mtls spiffe zero trust authorization policy sidecar",
        "concept": "Service Mesh architecture (Istio / Envoy), Zero-Trust security model, transparent mutual TLS (mTLS) with SPIFFE/SPIRE cryptographic identities, and L7 AuthorizationPolicies.",
        "question": """An enterprise deploys 80 microservices onto an Amazon EKS (Kubernetes) cluster. Look at the architecture and code snippet.
<br><br>
<strong>Part A:</strong> Historically, teams assumed internal cluster network traffic (pod-to-pod) was secure and communicated via plaintext HTTP. What attack vectors exist in a shared Kubernetes cluster under this flawed assumption?
<br>
<strong>Part B:</strong> How does a <strong>Service Mesh</strong> (like Istio using Envoy sidecar proxies) implement automatic mutual TLS (mTLS) without requiring a single line of security code inside the Java application?
<br>
<strong>Part C:</strong> How do SPIFFE IDs and Istio <code>AuthorizationPolicy</code> enable fine-grained Zero-Trust access control (e.g. allowing Payment Service to call Billing Service, while blocking Marketing Service)?""",
        "snippet_title": "InternalOrderClient.java",
        "snippet_code": """@Service
public class InternalOrderClient {

    @Autowired
    private RestTemplate restTemplate;

    public void invokePayment(PaymentCommand cmd) {
        // Plain HTTP communication between Kubernetes pods
        String url = "http://payment-service.default.svc.cluster.local:8080/charge";
        restTemplate.postForLocation(url, cmd);
    }
}""",
        "rating_concept": "Service Mesh architecture, Istio Envoy sidecars, and Zero-Trust mTLS with SPIFFE IDs",
        "solution": """<strong>Part A (The Fallacy of the Perimeter Defense):</strong>
<br>• <strong>Packet Sniffing:</strong> Pods on the same Kubernetes worker node share network namespaces/bridges. A compromised container running <code>tcpdump</code> can capture unencrypted traffic containing JWTs, passwords, and PII.
<br>• <strong>Lateral Movement:</strong> An attacker compromising a vulnerable frontend pod (e.g., via Log4Shell or SSRF) can pivot laterally across the cluster and invoke any internal database or payment endpoint without authentication.
<br><br>
<strong>Part B (Transparent Sidecar mTLS via Envoy & iptables):</strong>
<br>• Istio injects an <strong>Envoy sidecar container</strong> into every application pod.
<br>• <code>iptables</code> rules transparently redirect all inbound and outbound TCP traffic to the local Envoy proxy (port 15001/15006).
<br>• The Java application continues speaking plain HTTP locally to <code>localhost</code>.
<br>• Envoy negotiates an mTLS handshake with the destination pod's Envoy proxy, using short-lived x509 certificates automatically issued and rotated by Istio's control plane (Istiod).
<br><br>
<strong>Part C (SPIFFE Identity & L7 AuthorizationPolicy):</strong>
<br>• Every pod receives a <strong>SPIFFE ID</strong> embedded in its certificate SAN: <code>spiffe://cluster.local/ns/prod/sa/payment-service-sa</code>.
<br>• Istio's <code>AuthorizationPolicy</code> evaluates this cryptographic identity at Layer 7:
<br>It permits requests to <code>payment-service</code> ONLY if the caller's SPIFFE principal matches <code>order-service-sa</code>, rejecting all other pods with HTTP 403.""",
        "optimized_code": """apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: payment-access-policy
  namespace: prod
spec:
  selector:
    matchLabels:
      app: payment-service
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/prod/sa/order-service-sa"]
    to:
    - operation:
        methods: ["POST"]
        paths: ["/charge"]""",
        "junior_eval": "Suggests managing SSL certificates in Java keystores (JKS) manually in each microservice or relies entirely on Kubernetes private IP isolation.",
        "expert_eval": "Articulates lateral movement risks in Kubernetes, explains transparent Envoy iptables interception, diagrams mTLS certificate issuance, and configures SPIFFE-based AuthorizationPolicies."
    })

    # Q19: RFC 7807 Problem Details
    questions.append({
        "id": 19,
        "badge": "API Standards & REST Ergonomics",
        "keywords": "rfc 7807 problem details error handling 422 409 400 rest anti patterns spring boot 3",
        "concept": "Standardized REST API error handling via <strong>RFC 7807 (Problem Details for HTTP APIs)</strong>, semantic status code distinctions (400 vs 409 vs 422), and Spring Boot 3 ProblemDetail integration.",
        "question": """A public API returns error responses across different microservices. Look at the code snippet.
<br><br>
<strong>Part A:</strong> Explain why returning <code>HTTP 200 OK</code> with a body containing <code>{\"status\": \"ERROR\", \"code\": 500}</code> is a severe REST anti-pattern that breaks HTTP caches, API gateways, and client circuit breakers.
<br>
<strong>Part B:</strong> What is the standard structure of an <strong>RFC 7807</strong> Problem Details response? Explain the role of <code>type</code>, <code>title</code>, <code>status</code>, <code>detail</code>, and <code>instance</code>.
<br>
<strong>Part C:</strong> Distinguish the semantic differences between <strong>400 Bad Request</strong>, <strong>409 Conflict</strong>, and <strong>422 Unprocessable Entity</strong>. Which status code should be returned when a balance is insufficient to complete a transfer?""",
        "snippet_title": "LegacyErrorResponse.java",
        "snippet_code": """@RestController
@RequestMapping("/api/accounts")
public class AccountController {

    @PostMapping("/{id}/debit")
    public ResponseEntity<Map<String, Object>> debit(
            @PathVariable Long id, @RequestBody DebitRequest request) {
        
        if (request.getAmount() <= 0) {
            Map<String, Object> err = new HashMap<>();
            err.put("success", false);
            err.put("errorCode", "INVALID_AMOUNT");
            err.put("message", "Amount must be positive");
            return ResponseEntity.ok(err);
        }
        // ...
        return ResponseEntity.ok(Map.of("success", true));
    }
}""",
        "rating_concept": "RFC 7807 Problem Details, HTTP status code ergonomics, and REST error standards",
        "solution": """<strong>Part A (The HTTP 200 OK Error Anti-Pattern):</strong>
<br>• <strong>Broken Edge Caching:</strong> CDNs and reverse proxies cache HTTP 200 responses, causing an error returned to one user to potentially be served to subsequent users.
<br>• <strong>Blind Circuit Breakers:</strong> Resilience4j, Envoy, and AWS ALBs evaluate HTTP response codes. A 200 status is counted as a successful call, meaning failing backends never trigger circuit breakers or automated alarm triggers.
<br>• <strong>Client Deserialization Failures:</strong> Standard client SDKs expect domain response schemas on 200 and throw deserialization crashes when receiving unexpected error payloads.
<br><br>
<strong>Part B (RFC 7807 Specification Standard):</strong>
<br>Media Type: <code>application/problem+json</code>
<br>• <code>type</code>: A URI reference identifying the problem type (e.g. <code>https://api.mycorp.com/errors/insufficient-funds</code>).
<br>• <code>title</code>: Short, human-readable summary that does not change between occurrences.
<br>• <code>status</code>: The HTTP status code generated by origin server.
<br>• <code>detail</code>: Human-readable explanation specific to this occurrence.
<br>• <code>instance</code>: A URI reference identifying the specific occurrence/request ID.
<br><br>
<strong>Part C (Semantic Status Code Distinctions):</strong>
<br>• <strong>400 Bad Request:</strong> Malformed syntax, invalid JSON formatting, or unparseable headers.
<br>• <strong>409 Conflict:</strong> Concurrency conflicts, optimistic locking version mismatch, or duplicate unique keys.
<br>• <strong>422 Unprocessable Entity:</strong> Syntactically valid JSON, but business logic validation fails (e.g. Insufficient account balance).""",
        "optimized_code": """@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(InsufficientBalanceException.class)
    public ProblemDetail handleInsufficientFunds(
            InsufficientBalanceException ex, HttpServletRequest req) {
        
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.UNPROCESSABLE_ENTITY, ex.getMessage());
        problem.setType(URI.create("https://api.bank.com/errors/insufficient-funds"));
        problem.setTitle("Insufficient Account Balance");
        problem.setProperty("currentBalance", ex.getBalance());
        problem.setProperty("requestedAmount", ex.getRequestedAmount());
        problem.setInstance(URI.create(req.getRequestURI()));
        return problem;
    }
}""",
        "junior_eval": "Returns 200 OK with custom status flags or throws generic 500 Internal Server Errors with raw stack traces exposed to clients.",
        "expert_eval": "Critiques HTTP 200 anti-patterns on edge infrastructure, standardizes on RFC 7807 ProblemDetail, and precisely distinguishes 400 vs 409 vs 422 semantic usages."
    })

    # Q20: Multi-Region Active-Active & Disaster Recovery
    questions.append({
        "id": 20,
        "badge": "High Availability & Multi-Region DR",
        "keywords": "active active multi region disaster recovery rpo rto split brain crdt route53",
        "concept": "Multi-Region Active-Active microservices architecture, RPO (Recovery Point Objective) vs RTO (Recovery Time Objective), asynchronous cross-region data replication lag, and conflict resolution (CRDTs).",
        "question": """A global tier-1 retail bank requires an Active-Active deployment across two AWS regions (<code>us-east-1</code> and <code>us-west-2</code>) with RPO < 1 second and RTO < 5 seconds. Look at the architecture snippet.
<br><br>
<strong>Part A:</strong> Define <strong>RPO (Recovery Point Objective)</strong> and <strong>RTO (Recovery Time Objective)</strong> in the context of a catastrophic regional cloud outage.
<br>
<strong>Part B:</strong> If both regions accept writes concurrently for the same user account with asynchronous database replication (500ms cross-country latency), what happens during a network partition (Split-Brain)?
<br>
<strong>Part C:</strong> Detail two production architectural patterns to make Active-Active viable: <strong>Regional Data Pinning (User Home Region)</strong> and <strong>Conflict-Free Replicated Data Types (CRDTs)</strong>.""",
        "snippet_title": "MultiRegionAccountRouting.java",
        "snippet_code": """public class MultiRegionAccountRouting {

    public void routeUserTransaction(TransactionCommand cmd) {
        String primaryRegion = cmd.getPreferredRegion();
        executeOnDatabase(cmd, primaryRegion);
    }

    private void executeOnDatabase(TransactionCommand cmd, String region) {}
}""",
        "rating_concept": "Multi-Region Active-Active DR, RPO/RTO objectives, and cross-region write conflict resolution",
        "solution": """<strong>Part A (RPO vs RTO):</strong>
<br>• <strong>RPO (Recovery Point Objective):</strong> The maximum acceptable data loss measured in time. (RPO = 1s means you cannot lose more than 1 second of committed transactions).
<br>• <strong>RTO (Recovery Time Objective):</strong> The maximum acceptable downtime before the service is fully restored. (RTO = 5s means failover must restore operational traffic within 5 seconds).
<br><br>
<strong>Part B (The CAP Theorem & Split-Brain Hazard):</strong>
<br>According to the CAP Theorem, across a wide-area network partition ($P$), a distributed system must choose between Consistency ($C$) and Availability ($A$).
<br>If both regions allow concurrent writes with asynchronous replication:
<br>1. Conflicting writes occur (Last-Write-Wins overwrites data silently).
<br>2. Account balances can be double-spent in two regions simultaneously before replication catches up.
<br>3. When the partition heals, reconciling diverged relational database states requires complex manual reconciliation.
<br><br>
<strong>Part C (Architectural Mitigation Strategies):</strong>
<br>1. <strong>User Pinning (Home Region Partitioning):</strong> Users are cryptographically or geographically assigned to a primary home region (e.g. based on Account ID modulo or residence). All write transactions for User X are routed strictly to their home region. In disaster failover, traffic shifts to the standby region only after fencing old writes.
<br>2. <strong>CRDTs (Conflict-Free Replicated Data Types):</strong> For collaborative or counter-based services (e.g. shopping carts, inventory counters), use State-based or Operation-based CRDTs where operations are mathematically commutative and converge automatically without locks.""",
        "optimized_code": """@Component
public class RegionAwareRoutingFilter implements Filter {

    @Value("${cloud.aws.region.current}")
    private String currentRegion;

    @Autowired
    private UserRegionLocator regionLocator;

    public void doFilter(HttpServletRequest req, HttpServletResponse res, FilterChain chain) {
        String accountId = req.getHeader("X-Account-Id");
        String homeRegion = regionLocator.determineHomeRegion(accountId);

        if (!currentRegion.equals(homeRegion)) {
            // Forward write request to user's canonical Home Region
            res.setStatus(HttpServletResponse.SC_MOVED_TEMPORARILY);
            res.setHeader("Location", "https://" + homeRegion + ".bank.com" + req.getRequestURI());
            return;
        }
        chain.doFilter(req, res);
    }
}""",
        "junior_eval": "Assumes database replication across continents is instantaneous or suggests synchronous two-phase commit over 3,000 miles (which adds 100ms+ network latency to every single write).",
        "expert_eval": "Defines RPO/RTO rigorously, applies the CAP theorem to cross-region partitions, designs User Home Region pinning, and utilizes CRDTs for commutative data convergence."
    })

    return questions

def generate_rest_html():
    from create_rest_page import html_header, html_footer
    questions = get_rest_questions()

    cards_html = []
    snippets_hidden_html = []

    for q in questions:
        q_id = q["id"]
        keywords = html.escape(q["keywords"])
        badge = html.escape(q["badge"])
        concept = q["concept"]
        question_text = q["question"]
        snippet_title = html.escape(q["snippet_title"])
        clean_lines = []
        for line in q["snippet_code"].split("\n"):
            # strip single-line comments if not part of http://
            if "//" in line and "http://" not in line and "https://" not in line:
                idx = line.find("//")
                line = line[:idx].rstrip()
            if line.strip():
                clean_lines.append(line)
        clean_snippet = "\n".join(clean_lines)
        snippet_code_escaped = html.escape(clean_snippet)
        rating_concept_escaped = html.escape(q["rating_concept"]).replace("'", "\\'")
        solution_text = q["solution"]
        optimized_code = html.escape(q["optimized_code"])
        junior_eval = html.escape(q["junior_eval"])
        expert_eval = html.escape(q["expert_eval"])

        card = f"""                <!-- QUESTION {q_id}: {badge} -->
                <div class="question-card" id="q-{q_id}" data-keywords="{keywords}">
                    <div class="card-header">
                        <span class="concept-badge">{badge}</span>
                        <span class="q-number">Question {q_id} of 20</span>
                    </div>
                    <div class="card-body">
                        <div class="section-block">
                            <div class="section-title">📌 1. Concept Covered</div>
                            <div class="concept-text">
                                {concept}
                            </div>
                        </div>

                        <div class="section-block">
                            <div class="section-title">❓ 2. Question</div>
                            <div class="question-title">
                                {question_text}
                            </div>
                        </div>

                        <div class="section-block">
                            <div class="section-title">💻 3. Code Challenge</div>
                            <button class="btn-view-code" onclick="openCodeSnippetModal('{q_id}', '{snippet_title}')">
                                💻 View Code Snippet (Popup)
                            </button>
                            <div id="snippet-{q_id}" style="display:none;">{snippet_code_escaped}</div>
                        </div>

                        <!-- 1-4 Answer Quality Rating -->
                        <div class="question-rating-panel">
                            <span class="rating-panel-label">🎯 Answer Quality:</span>
                            <div class="star-rating-group" id="star-group-{q_id}">
                                <button class="star-btn" data-rating="1" onclick="setQuestionRating('rest', {q_id}, 1, '{rating_concept_escaped}')">
                                    <span class="star-num">1</span>
                                    <span class="star-label">Cannot Explain</span>
                                </button>
                                <button class="star-btn" data-rating="2" onclick="setQuestionRating('rest', {q_id}, 2, '{rating_concept_escaped}')">
                                    <span class="star-num">2</span>
                                    <span class="star-label">Partial</span>
                                </button>
                                <button class="star-btn" data-rating="3" onclick="setQuestionRating('rest', {q_id}, 3, '{rating_concept_escaped}')">
                                    <span class="star-num">3</span>
                                    <span class="star-label">Good</span>
                                </button>
                                <button class="star-btn" data-rating="4" onclick="setQuestionRating('rest', {q_id}, 4, '{rating_concept_escaped}')">
                                    <span class="star-num">4</span>
                                    <span class="star-label">Expert</span>
                                </button>
                            </div>
                            <span class="q-score-display" id="q-score-{q_id}">Not Rated</span>
                        </div>

                        <button class="solution-toggle" onclick="toggleSolution(this)">
                            <span>👁️ Show Solution & Candidate Evaluation</span>
                            <span>▼</span>
                        </button>
                        <div class="solution-content">
                            <div class="solution-heading">Answer Key & Deep-Dive Explanation</div>
                            <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 8px;">
                                {solution_text}
                            </p>
                            <div class="code-wrapper">
                                <div class="code-header"><span>Architectural / Code Solution</span><span class="code-lang">Java / Config</span></div>
                                <pre><code>{optimized_code}</code></pre>
                            </div>
                            <div class="evaluation-grid">
                                <div class="eval-box eval-bad">
                                    <div class="eval-title">⚠️ Junior / Beginner Response</div>
                                    {junior_eval}
                                </div>
                                <div class="eval-box eval-good">
                                    <div class="eval-title">🌟 Advanced / Expert Response</div>
                                    {expert_eval}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
"""
        cards_html.append(card)

    all_cards_str = "\n".join(cards_html)
    full_html = html_header + all_cards_str + html_footer

    out_path = "/Users/barvepan/Pandharinath/Developer/Workspace/interview-questions/rest-api-microservices.html"
    with open(out_path, "w") as f:
        f.write(full_html)
    print(f"Generated {out_path} with {len(questions)} questions successfully!")

if __name__ == "__main__":
    generate_rest_html()
