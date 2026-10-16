import os
import html

def get_architecture_questions():
    questions = []

    # Q1: SOLID Principles & Liskov Substitution Principle Violation
    questions.append({
        "id": 1,
        "badge": "Object-Oriented Design & SOLID",
        "keywords": "solid principles liskov substitution lsp srp ocp dip fragile base class",
        "concept": "SOLID Design Principles, specifically the <strong>Liskov Substitution Principle (LSP)</strong> and <strong>Dependency Inversion Principle (DIP)</strong> in class hierarchy refactoring.",
        "question": """A banking domain model defines an account hierarchy with withdrawals and interest calculations. Look at the code snippet.
<br><br>
<strong>Part A:</strong> Look at <code>FixedTermDepositAccount</code> extending <code>BankAccount</code>. Why does throwing <code>UnsupportedOperationException</code> inside <code>withdraw()</code> represent a catastrophic violation of the <strong>Liskov Substitution Principle (LSP)</strong>?
<br>
<strong>Part B:</strong> What are the formal Design-by-Contract rules of LSP regarding method preconditions, postconditions, and exception types?
<br>
<strong>Part C:</strong> Refactor this design using <strong>Composition over Inheritance</strong> and fine-grained interfaces (Interface Segregation Principle) so that clients never encounter runtime exceptions when substituting account types.""",
        "snippet_title": "AccountHierarchy.java",
        "snippet_code": """public abstract class BankAccount {
    protected BigDecimal balance;

    public BankAccount(BigDecimal initialBalance) {
        this.balance = initialBalance;
    }

    public void deposit(BigDecimal amount) {
        this.balance = this.balance.add(amount);
    }

    public void withdraw(BigDecimal amount) {
        if (this.balance.compareTo(amount) >= 0) {
            this.balance = this.balance.subtract(amount);
        } else {
            throw new InsufficientFundsException("Overdraft not permitted");
        }
    }
}

public class FixedTermDepositAccount extends BankAccount {
    private LocalDate maturityDate;

    public FixedTermDepositAccount(BigDecimal initial, LocalDate maturity) {
        super(initial);
        this.maturityDate = maturity;
    }

    @Override
    public void withdraw(BigDecimal amount) {
        throw new UnsupportedOperationException("Withdrawals forbidden prior to maturity date!");
    }
}""",
        "rating_concept": "SOLID principles, Liskov Substitution Principle violation, and Composition over Inheritance",
        "solution": """<strong>Part A (The LSP Violation & Broken Polymorphism):</strong>
<br>• The Liskov Substitution Principle states: <em>\"Objects of a superclass shall be replaceable with objects of its subclasses without breaking the application.\"</em>
<br>• Any client code operating on <code>BankAccount account</code> expects that calling <code>account.withdraw(...)</code> is a valid contract operation.
<br>• Substituting a <code>FixedTermDepositAccount</code> throws an unexpected runtime exception (<code>UnsupportedOperationException</code>), crashing batch transfer services and violating client expectations.
<br><br>
<strong>Part B (Design-by-Contract LSP Rules):</strong>
<br>1. <strong>Preconditions cannot be strengthened</strong> in a subtype (you cannot require stricter constraints than the parent).
<br>2. <strong>Postconditions cannot be weakened</strong> in a subtype (you cannot guarantee less than the parent).
<br>3. <strong>Exception covariance:</strong> Subtypes may not throw new checked exceptions unless they are subtypes of exceptions declared by the parent method.
<br><br>
<strong>Part C (Architectural Refactoring via Interface Segregation):</strong>
<br>Split the monolithic abstract class into segregated capabilities: <code>DepositCapable</code> and <code>Withdrawable</code>.
<br>Checking accounts implement both; Fixed Term accounts implement only <code>DepositCapable</code>. The withdrawal service accepts <code>Withdrawable</code>, making runtime type errors mathematically impossible at compile time.""",
        "optimized_code": """public interface Account {
    BigDecimal getBalance();
    void deposit(BigDecimal amount);
}

public interface WithdrawableAccount extends Account {
    void withdraw(BigDecimal amount);
}

public class CheckingAccount implements WithdrawableAccount {
    // Implements deposit and withdraw
}

public class FixedTermAccount implements Account {
    // Implements deposit only; cannot be passed to withdrawal services!
}""",
        "junior_eval": "Recites the textbook definition of SOLID but fails to recognize that throwing UnsupportedOperationException is the textbook violation of LSP.",
        "expert_eval": "Articulates Design-by-Contract rules (preconditions, postconditions, exception covariance), rejects inheritance hierarchies that mutate behavior, and refactors via Interface Segregation."
    })

    # Q2: The 12-Factor App Methodology
    questions.append({
        "id": 2,
        "badge": "Cloud-Native Architecture & 12-Factor",
        "keywords": "12 factor app cloud native stateless configuration environment parity disposability",
        "concept": "The 12-Factor App methodology for cloud-native applications, container disposability, configuration injection, stateless processes, and stdout log streaming.",
        "question": """A legacy enterprise Java monolith is being containerized for deployment onto Kubernetes. Look at the configuration and code snippet.
<br><br>
<strong>Part A:</strong> Identify the three distinct <strong>12-Factor App principles</strong> violated in this code snippet (Factor III: Config, Factor VI: Processes, and Factor XI: Logs).
<br>
<strong>Part B:</strong> What is <strong>Factor IX: Disposability</strong>, and why is fast startup and graceful shutdown (handling SIGTERM) essential for auto-scaled Kubernetes pods?
<br>
<strong>Part C:</strong> Explain <strong>Factor X: Dev/Prod Parity</strong>. Why is using an in-memory H2 database for local development and PostgreSQL for production an architectural risk?""",
        "snippet_title": "LegacyOrderProcessor.java",
        "snippet_code": """@Service
public class LegacyOrderProcessor {

    private final String dbPassword = "HardcodedProductionPassword123";

    public void process(Order order) {
        File sessionFile = new File("/var/tmp/sessions/" + order.getUserId() + ".txt");
        writeToFile(sessionFile, order);

        try (FileWriter fw = new FileWriter("/var/log/app/orders.log", true)) {
            fw.write("Processed order: " + order.getId() + "\n");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void writeToFile(File f, Order o) {}
}""",
        "rating_concept": "12-Factor App methodology, stateless container processes, and dev/prod parity",
        "solution": """<strong>Part A (The 3 Breached 12-Factor Principles):</strong>
<br>1. <strong>Factor III (Config):</strong> Hardcoding <code>dbPassword</code> violates strict separation of config from code. Config must be injected via environment variables.
<br>2. <strong>Factor VI (Stateless Processes):</strong> Writing user session data to local disk (<code>/var/tmp/sessions</code>) assumes local persistence. In containers, local disk is ephemeral and lost upon pod restart; instances cannot be load-balanced horizontally. State must be externalized to backing services (Redis/Hazelcast/Postgres).
<br>3. <strong>Factor XI (Logs):</strong> Writing directly to a local log file (<code>/var/log/app/orders.log</code>) tightly couples the app to filesystem storage. The app must treat logs as an unbuffered event stream written to <strong>stdout/stderr</strong>, captured by container log collectors (Fluentbit/Datadog).
<br><br>
<strong>Part B (Factor IX: Disposability):</strong>
<br>Processes must maximize robustness with <strong>fast startup</strong> (sub-second boot) and <strong>graceful shutdown</strong>.
<br>When Kubernetes scales down or nodes are drained, the pod receives <code>SIGTERM</code>. The app must stop accepting new requests, finish in-flight transactions, close DB pools, and exit within the grace period.
<br><br>
<strong>Part C (Factor X: Dev/Prod Parity):</strong>
<br>Using H2 locally and PostgreSQL in production introduces severe subtle bugs: differences in SQL dialect, locking behavior, transaction isolation levels, and sequence generators. Modern practice mandates running real PostgreSQL locally using <strong>Testcontainers</strong> or Docker Compose.""",
        "optimized_code": """@Service
public class CloudNativeOrderProcessor {
    private static final Logger log = LoggerFactory.getLogger(CloudNativeOrderProcessor.class);

    @Autowired
    private DistributedSessionStore sessionStore; // External state (Redis)

    public void process(Order order) {
        sessionStore.save(order.getUserId(), order);
        log.info("Processed order: {}", order.getId()); // Streams to stdout
    }
}""",
        "junior_eval": "Suggests mounting persistent volume claims (PVC) to keep the local log files and session files on disk across Kubernetes restarts.",
        "expert_eval": "Identifies violations across Config, Stateless Processes, and Logs, articulates Disposability and SIGTERM lifecycle handling, and enforces Dev/Prod Parity with Testcontainers."
    })

    # Q3: Distributed In-Memory Caching: Hazelcast IMDG
    questions.append({
        "id": 3,
        "badge": "Distributed Caching & In-Memory Data Grids",
        "keywords": "hazelcast imdg near cache cache stampede split brain quorum invalidation stale read",
        "concept": "Distributed In-Memory Data Grids (Hazelcast IMDG), Near-Cache invalidation mechanisms, cache stampede (dogpile effect) mitigation, and cluster Split-Brain Quorum protection.",
        "question": """A high-throughput airline reservation engine uses a 4-node Hazelcast cluster to store flight seat availability. Look at the Hazelcast Near-Cache configuration snippet.
<br><br>
<strong>Part A:</strong> To optimize read performance, the team enables <strong>Near-Cache</strong> on all application nodes. A customer books Seat 14A on Node 1, but customers browsing on Node 3 continue to see Seat 14A as available for 2 minutes, causing duplicate booking attempts. Explain why Near-Cache causes stale reads and how invalidation listeners resolve this.
<br>
<strong>Part B:</strong> What is a <strong>Cache Stampede (Dogpile Effect)</strong>, and how does Hazelcast distributed locking or mutex-backed loader prevent 10,000 concurrent threads from querying the primary database when a key expires?
<br>
<strong>Part C:</strong> What is a <strong>Split-Brain scenario</strong> in a distributed cache cluster during network partitions, and how does configuring a <strong>Quorum (Split-Brain Protection)</strong> prevent two disconnected network partitions from accepting conflicting writes?""",
        "snippet_title": "hazelcast-config.xml",
        "snippet_code": """<hazelcast>
    <map name="seat-availability">
        <in-memory-format>BINARY</in-memory-format>
        <backup-count>1</backup-count>
        <near-cache>
            <time-to-live-seconds>120</time-to-live-seconds>
            <max-idle-seconds>60</max-idle-seconds>
            <invalidate-on-change>false</invalidate-on-change>
        </near-cache>
    </map>
</hazelcast>""",
        "rating_concept": "Hazelcast IMDG Near-Cache invalidation, cache stampede mitigation, and split-brain quorum",
        "solution": """<strong>Part A (Near-Cache Invalidation Mechanics):</strong>
<br>• Near-Cache stores a copy of frequently read entries in the <strong>local JVM memory</strong> of the calling node to avoid network round-trips to the owner node.
<br>• In the configuration snippet: <code>&lt;invalidate-on-change&gt;false&lt;/invalidate-on-change&gt;</code>!
<br>• When Node 1 mutates the seat status in the distributed map, it does not broadcast an invalidation event.
<br>• Node 3 continues reading its local Near-Cache copy for 120 seconds until TTL expires, serving stale, corrupted availability.
<br><strong>Fix:</strong> Set <code>invalidate-on-change</code> to <code>true</code>. When an entry is updated, Hazelcast broadcasts an invalidation event to all cluster Near-Caches.
<br><br>
<strong>Part B (Cache Stampede & Mutex Loading):</strong>
<br>• When a high-traffic key (e.g. Flight 101 seat map) expires, thousands of concurrent threads experience a simultaneous cache miss.
<br>• All 10,000 threads hit the primary relational database at the exact same millisecond, exhausting database connection pools and crashing the DB.
<br>• <strong>Fix:</strong> Use Hazelcast <code>MapLoader</code> with mutual exclusion or atomic locking so only <strong>one worker thread</strong> executes the DB query while the other 9,999 threads await the repopulated cache.
<br><br>
<strong>Part C (Split-Brain & Quorum Protection):</strong>
<br>• If a network partition splits a 4-node cluster into two isolated 2-node partitions, both sides believe the other is dead.
<br>• Without protection, both sub-clusters elect masters and accept independent writes, causing irreconcilable data divergence.
<br>• <strong>Quorum Protection:</strong> Requires a minimum number of participating nodes (e.g. $\\lfloor N/2 \\rfloor + 1 = 3$ nodes) to accept writes. The 2-node sub-cluster drops into read-only mode, eliminating split-brain corruption.""",
        "optimized_code": """<hazelcast>
    <map name="seat-availability">
        <in-memory-format>BINARY</in-memory-format>
        <backup-count>2</backup-count>
        <quorum-ref>strict-majority-quorum</quorum-ref>
        <near-cache>
            <in-memory-format>OBJECT</in-memory-format>
            <invalidate-on-change>true</invalidate-on-change>
            <eviction eviction-policy="LRU" max-size-policy="ENTRY_COUNT" size="5000"/>
        </near-cache>
    </map>
    <quorum name="strict-majority-quorum" enabled="true">
        <quorum-size>3</quorum-size>
    </quorum>
</hazelcast>""",
        "junior_eval": "Blames network speed or suggests setting TTL to 0 (which completely defeats the purpose of caching).",
        "expert_eval": "Pinpoints invalidate-on-change=false in Near-Cache, designs mutex loading to prevent cache stampedes, and configures majority quorum to prevent split-brain partition corruption."
    })

    # Q4: Web Session Management: Sticky Sessions vs Session Clustering
    questions.append({
        "id": 4,
        "badge": "Session Management & Scalability",
        "keywords": "session management sticky session spring session redis hazelcast blast radius jwt",
        "concept": "Web session architecture at scale: Application Load Balancer Sticky Sessions (cookie affinity) vs Centralized Session Clustering (Spring Session with Redis/Hazelcast) vs Stateless JWTs.",
        "question": """An e-commerce website runs on 20 auto-scaled Kubernetes pods. Look at the session handling architecture and code snippet.
<br><br>
<strong>Part A:</strong> The system relies on ALB <strong>Sticky Sessions</strong> (cookie-based routing). When Pod 7 crashes due to an OutOfMemoryError, 5,000 active shopping customers are instantly logged out and lose their shopping carts. Explain the structural flaw of Sticky Sessions.
<br>
<strong>Part B:</strong> How does <strong>Spring Session with Redis / Hazelcast</strong> decouple session storage from individual container processes? What happens to active user sessions during a rolling deployment?
<br>
<strong>Part C:</strong> Compare Centralized Session Stores against <strong>Stateless JWT Tokens</strong>. Under what compliance or business requirements (e.g. instant session revocation, user ban, concurrent session limits) is a centralized session store strictly required over JWT?""",
        "snippet_title": "LegacySessionCart.java",
        "snippet_code": """@Controller
public class CheckoutController {

    @PostMapping("/cart/add")
    public String addToCart(@RequestParam String item, HttpSession session) {
        // Anti-Pattern: Local in-memory Tomcat session state
        List<String> cart = (List<String>) session.getAttribute("CART_ITEMS");
        if (cart == null) {
            cart = new ArrayList<>();
            session.setAttribute("CART_ITEMS", cart);
        }
        cart.add(item);
        return "cart-view";
    }
}""",
        "rating_concept": "Session management, Sticky Sessions vs Spring Session Redis/Hazelcast, and JWT revocation",
        "solution": """<strong>Part A (The Flaw of Sticky Sessions):</strong>
<br>• Sticky sessions use an ALB affinity cookie to route all requests from a specific user to the exact same server instance.
<br>• State lives strictly in the <strong>local Tomcat JVM heap memory</strong> of that instance.
<br>• <strong>Blast Radius:</strong> When that pod crashes, is evicted, or scales in, the memory is destroyed. All users pinned to that node lose their authentication, active carts, and session data.
<br>• Furthermore, sticky sessions break uniform load distribution: one popular user or corporate proxy can overload a single pod while others sit idle.
<br><br>
<strong>Part B (Spring Session with Redis/Hazelcast):</strong>
<br>• Spring Session wraps the standard <code>HttpServletRequest</code> using a servlet filter.
<br>• <code>session.setAttribute()</code> transparently serializes the data to a shared, high-availability Redis or Hazelcast cluster.
<br>• <strong>Zero-Downtime Rolling Deploys:</strong> Any of the 20 pods can process any incoming request from any user seamlessly. If Pod 7 terminates, the load balancer routes the next request to Pod 8, which reads the session from Redis in 1ms with zero user disruption.
<br><br>
<strong>Part C (Centralized Session Store vs Stateless JWT):</strong>
<br>• <em>JWT Limitations:</em> Once issued, a stateless JWT cannot be revoked or invalidated until its expiration time without building a centralized blacklist (which defeats statelessness).
<br>• <em>Centralized Session Store Required for:</em>
<br>1. <strong>Instant User Ban / Logout:</strong> Terminating an active session immediately upon security alert.
<br>2. <strong>Concurrent Session Limits:</strong> Restricting a user to max 1 active login at a time (e.g. streaming services).
<br>3. <strong>Data Size:</strong> Storing large shopping cart state that exceeds HTTP cookie header size limits (4KB).""",
        "optimized_code": """// Spring Session Redis Configuration
@Configuration
@EnableRedisHttpSession(maxInactiveIntervalInSeconds = 1800)
public class SessionConfig {

    @Bean
    public LettuceConnectionFactory connectionFactory() {
        return new LettuceConnectionFactory(new RedisStandaloneConfiguration("redis-cluster", 6379));
    }
}""",
        "junior_eval": "Recommends sticking with ALB Sticky Sessions or proposes putting the entire 50KB shopping cart payload inside a client-side JWT cookie.",
        "expert_eval": "Articulates sticky session blast-radius and traffic skew flaws, implements Spring Session Redis clustering for seamless zero-downtime rolling deploys, and contrasts JWT revocation trade-offs."
    })

    # Q5: Referential Integrity in Microservices & DDD
    questions.append({
        "id": 5,
        "badge": "Domain-Driven Design & Data Integrity",
        "keywords": "referential integrity microservices ddd bounded context aggregate root eventual consistency",
        "concept": "Handling referential integrity across distributed microservices without cross-database foreign keys, Domain-Driven Design (DDD) Bounded Contexts, and asynchronous reconciliation.",
        "question": """An architect splits a monolithic relational database into three independent microservice databases: Customer Service DB, Order Service DB, and Inventory Service DB. Look at the code snippet.
<br><br>
<strong>Part A:</strong> In the monolith, a foreign key constraint (<code>FOREIGN KEY (customer_id) REFERENCES customers(id)</code>) prevented orphan orders and guaranteed referential integrity. In microservices, each service has its own private database. How do you prevent orphan records without cross-database foreign keys?
<br>
<strong>Part B:</strong> What is a <strong>Bounded Context</strong> and an <strong>Aggregate Root</strong> in Domain-Driven Design (DDD)? Why must an external microservice reference an Aggregate only by its Identity (ID) rather than directly querying its internal relational tables?
<br>
<strong>Part C:</strong> If Customer Service deletes a customer record while Order Service has active orders for that customer, how should the architecture handle this delete operation? Compare <strong>Logical Deletes (Soft Deletes)</strong> against <strong>Domain Event Notification</strong>.""",
        "snippet_title": "OrderEntity.java",
        "snippet_code": """// Anti-Pattern: Attempting JPA relationship across distributed databases
@Entity
@Table(name = "orders")
public class OrderEntity {
    @Id
    private Long id;

    // Impossible across microservice database boundaries:
    // @ManyToOne
    // @JoinColumn(name = "customer_id")
    // private CustomerEntity customer;

    private Long customerId; // Unenforced foreign ID
    private BigDecimal totalAmount;
}""",
        "rating_concept": "Microservices referential integrity, DDD Bounded Contexts, and asynchronous reconciliation",
        "solution": """<strong>Part A (Integrity Without Foreign Keys):</strong>
<br>• In distributed microservices, databases are physically isolated; cross-database relational foreign keys do not exist.
<br>• Integrity is enforced via <strong>Application-Level Domain Logic & Eventual Consistency</strong>:
<br>1. When creating an order, Order Service publishes an <code>OrderCreatedEvent</code> or verifies customer existence via a resilient API call.
<br>2. <strong>Saga Pattern:</strong> If customer validation fails, the order is rejected.
<br>3. <strong>Asynchronous Audit & Reconciliation Jobs:</strong> Scheduled background workers compare event streams and database states to detect and flag anomalies.
<br><br>
<strong>Part B (Bounded Contexts & Aggregate Roots):</strong>
<br>• <strong>Bounded Context:</strong> A linguistic and model boundary within which a domain model applies consistently. Customer in Sales has different semantics than Customer in Billing.
<br>• <strong>Aggregate Root:</strong> The cluster of domain objects that can be treated as a single unit for data changes (e.g., <code>Order</code> is root; <code>OrderItem</code> is internal).
<br>• External microservices must reference Aggregates <strong>strictly by ID</strong> (<code>customerId</code>). This preserves loose coupling and allows Customer Service to refactor its internal schema without breaking Order Service.
<br><br>
<strong>Part C (Handling Deletions):</strong>
<br>• <strong>Hard Deletes are an Anti-Pattern:</strong> In enterprise systems, customer records are never physically deleted (due to financial auditing and tax regulations).
<br>• <strong>Soft Delete & Domain Events:</strong> Customer Service marks status as <code>DEACTIVATED</code> and emits a <code>CustomerDeactivatedEvent</code>.
<br>• Order Service listens to the event and blocks future orders while preserving historical order records for accounting.""",
        "optimized_code": """@Service
public class CustomerDeactivationHandler {

    @KafkaListener(topics = "customer-events")
    public void onCustomerDeactivated(CustomerDeactivatedEvent event) {
        // Prevent new orders while retaining historic integrity
        orderRepository.lockPendingOrdersForCustomer(event.getCustomerId());
        auditLog.info("Customer {} deactivated; historical orders preserved", event.getCustomerId());
    }
}""",
        "junior_eval": "Proposes sharing the same database between microservices just to keep SQL foreign keys, destroying microservice autonomy.",
        "expert_eval": "Applies DDD Bounded Context boundaries, enforces Aggregate identity references, rejects hard deletes in favor of soft-state domain events, and implements asynchronous reconciliation."
    })

    # Q6: The CAP Theorem in Enterprise Distributed Systems
    questions.append({
        "id": 6,
        "badge": "Distributed Systems Theory & CAP",
        "keywords": "cap theorem consistency availability partition tolerance cp vs ap pacelc split brain",
        "concept": "The CAP Theorem in distributed enterprise architecture, network partitions ($P$), Consistency ($C$) vs Availability ($A$) trade-offs, and PACELC theorem extensions.",
        "question": """A global retail bank architects its ATM cash withdrawal network across two geographically separated data centers. Look at the architectural scenario.
<br><br>
<strong>Part A:</strong> Explain why, in the real physical world, <strong>Partition Tolerance ($P$) is non-negotiable</strong>. Why is the classic choice in distributed systems always strictly between <strong>CP (Consistency/Partition Tolerance)</strong> and <strong>AP (Availability/Partition Tolerance)</strong>?
<br>
<strong>Part B:</strong> During a transatlantic undersea fiber-optic cable cut, Data Center A cannot communicate with Data Center B.
<br>• If you choose a <strong>CP</strong> model: What happens to a customer attempting to withdraw $500 at an ATM connected to Data Center B?
<br>• If you choose an <strong>AP</strong> model: What happens, and what business risk does the bank assume?
<br>
<strong>Part C:</strong> What is the <strong>PACELC Theorem</strong>, and how does it extend CAP to address the trade-off between Latency and Consistency even when no network partition exists?""",
        "snippet_title": "AtmWithdrawalCoordinator.java",
        "snippet_code": """public class AtmWithdrawalCoordinator {

    // When network partition P occurs between DC1 and DC2:
    public WithdrawalResult executeAtmWithdrawal(String accountId, BigDecimal amount) {
        // CP Choice: Reject withdrawal if remote ledger cannot be synchronously locked
        // AP Choice: Dispense cash locally based on cached balance, risk overdraft
        return null;
    }
}""",
        "rating_concept": "CAP theorem trade-offs, CP vs AP banking models, and PACELC latency trade-offs",
        "solution": """<strong>Part A (Why Partition Tolerance Is Non-Negotiable):</strong>
<br>• In distributed systems operating across networks, routers reboot, fiber cables are cut, and switches drop packets.
<br>• Network partitions ($P$) <strong>will inevitably occur</strong>.
<br>• You cannot \"choose\" CA. When a partition occurs, the system must either:
<br>1. Cancel the operation to preserve data consistency &rarr; <strong>CP</strong> (sacrificing Availability).
<br>2. Proceed with local data to preserve uptime &rarr; <strong>AP</strong> (sacrificing Consistency).
<br><br>
<strong>Part B (CP vs AP in Banking Cash Withdrawals):</strong>
<br>• <strong>CP Selection:</strong> The ATM queries the local node. Because it cannot reach the remote master to acquire a synchronous lock, the ATM displays: <em>\"Network error: Transaction declined. Please try again later.\"</em> (Preserves balance consistency; zero risk of overdraft; poor customer experience).
<br>• <strong>AP Selection:</strong> The ATM dispenses the $500 based on the last known cached balance.
<br><em>Business Risk:</em> The customer's accomplice can withdraw $500 simultaneously at an ATM in Data Center A! When the partition heals, the account is overdrawn by $1,000. Real banks use a bounded AP model (allow up to $200 emergency offline limit).
<br><br>
<strong>Part C (The PACELC Theorem):</strong>
<br>CAP only describes behavior during a partition. PACELC states:
<br><em>If there is a Partition ($P$), choose between Availability ($A$) and Consistency ($C$);<br><strong>Else ($E$)</strong>, choose between <strong>Latency ($L$)</strong> and <strong>Consistency ($C$)</strong>.</em>
<br>In healthy normal operations, replicating synchronously across data centers adds 80ms latency (Consistency), while replicating asynchronously responds in 2ms (Low Latency).""",
        "optimized_code": """// Real-World Bounded AP Hybrid Banking Model
public WithdrawalResult processAtmWithdrawal(AccountLedger ledger, BigDecimal amount) {
    if (isNetworkPartitioned()) {
        // Bounded Offline Policy: Allow up to $200 emergency cash
        if (amount.compareTo(new BigDecimal("200")) <= 0) {
            ledger.recordOfflineDebit(amount);
            return WithdrawalResult.DISPENSE_OFFLINE_PROVISIONAL;
        }
        return WithdrawalResult.REJECT_NETWORK_UNAVAILABLE; // CP for large amounts
    }
    return ledger.executeSynchronousDebit(amount); // Normal CP
}""",
        "junior_eval": "Claims that high-availability cloud providers (like AWS) can achieve all three: Consistency, Availability, and Partition Tolerance simultaneously.",
        "expert_eval": "Proves why CA is physically impossible across networks, details real-world CP vs AP banking failure modes, and explains PACELC normal-state latency trade-offs."
    })

    # Q7: Test-Driven Development (TDD) & The Testing Pyramid
    questions.append({
        "id": 7,
        "badge": "Quality Engineering & Testing Architecture",
        "keywords": "tdd test driven development testing pyramid unit integration contract e2e flakiness",
        "concept": "Test-Driven Development (TDD Red-Green-Refactor), the Testing Pyramid, and eliminating brittle inverted ice-cream cone testing architectures.",
        "question": """An enterprise engineering department suffers from a 4-hour CI/CD deployment pipeline where 30% of builds fail due to flaky end-to-end (E2E) browser tests. Look at the architecture.
<br><br>
<strong>Part A:</strong> Explain the <strong>Testing Pyramid</strong> model (Unit Tests at base &rarr; Integration/Contract Tests &rarr; E2E UI Tests at apex). What is the <strong>Inverted Testing Pyramid (Ice-Cream Cone Anti-Pattern)</strong>, and why does it paralyze enterprise release velocity?
<br>
<strong>Part B:</strong> Walk through the three stages of the <strong>TDD (Test-Driven Development)</strong> cycle: <strong>Red</strong>, <strong>Green</strong>, and <strong>Refactor</strong>. How does writing tests *before* code shape clean software design?
<br>
<strong>Part C:</strong> Contrast a <strong>Unit Test</strong> (with mocks) against an <strong>Integration Test</strong> (using Testcontainers). Why should external services (Stripe, Twilio) be tested with Consumer-Driven Contracts rather than live sandbox environments?""",
        "snippet_title": "OrderValidationTest.java",
        "snippet_code": """public class OrderServiceTest {

    // Anti-Pattern: Slow, brittle E2E UI Selenium test for simple business rule
    @Test
    public void testOrderTaxCalculation() {
        WebDriver driver = new ChromeDriver();
        driver.get("https://staging.company.com/login");
        driver.findElement(By.id("user")).sendKeys("admin");
        driver.findElement(By.id("pass")).sendKeys("1234");
        driver.findElement(By.id("submit")).click();
        // 45 seconds later... tests if 10 * 0.08 == 0.80
    }
}""",
        "rating_concept": "TDD Red-Green-Refactor cycle, Testing Pyramid distribution, and Testcontainers vs mocks",
        "solution": """<strong>Part A (The Testing Pyramid vs Ice-Cream Cone):</strong>
<br>• <strong>Testing Pyramid:</strong>
<br>1. <em>Unit Tests (70%):</em> In-memory, sub-millisecond execution, isolated, testing business logic branches.
<br>2. <em>Integration/Contract Tests (20%):</em> Verifies database queries, serialization, and API contracts (Testcontainers, WireMock, Pact).
<br>3. <em>E2E Tests (10%):</em> Critical path smoke tests through the UI.
<br>• <strong>The Ice-Cream Cone Anti-Pattern:</strong> Few unit tests, almost all verification done via heavy Selenium/Cypress UI tests.
<br><em>Liabilities:</em> Slow runs (hours), high flakiness (network blips, UI animation timings), expensive test environments, and late bug discovery.
<br><br>
<strong>Part B (The TDD Lifecycle):</strong>
<br>1. <strong>Red:</strong> Write a focused unit test for a single requirement before any implementation exists. Run it and verify it <strong>fails for the right reason</strong>.
<br>2. <strong>Green:</strong> Write the minimal amount of production code necessary to pass the test.
<br>3. <strong>Refactor:</strong> Clean up duplication, improve abstractions, and optimize design while tests ensure zero regression.
<br><em>Design Benefit:</em> TDD forces small, modular, loosely coupled classes with high cohesion.
<br><br>
<strong>Part C (Testcontainers vs Live Sandboxes):</strong>
<br>Live third-party sandboxes are slow, require internet access, have rate limits, and can experience outages.
<br><strong>Testcontainers</strong> spins up real ephemeral Docker containers (PostgreSQL, Kafka) locally, giving 100% production fidelity with zero environment drift.""",
        "optimized_code": """// Fast, deterministic pure Unit Test
@Test
void shouldCalculateEightPercentTaxForStandardItems() {
    TaxCalculator calculator = new StandardTaxCalculator(new BigDecimal("0.08"));
    BigDecimal tax = calculator.calculateTax(new BigDecimal("100.00"));
    assertEquals(new BigDecimal("8.00"), tax); // Executes in 1 millisecond
}""",
        "junior_eval": "Advocates testing everything through the browser UI or believes writing tests after code is equivalent to TDD.",
        "expert_eval": "Structures test suites according to the Testing Pyramid, articulates TDD's architectural design benefits, and replaces flaky live sandboxes with Testcontainers and Pact."
    })

    # Q8: Low-Latency High-Throughput: The LMAX Disruptor Pattern
    questions.append({
        "id": 8,
        "badge": "High-Throughput Systems & Mechanical Sympathy",
        "keywords": "lmax disruptor mechanical sympathy ring buffer false sharing lock free cas cpu cache",
        "concept": "Low-latency systems architecture, Mechanical Sympathy, CPU L1/L2/L3 cache lines (64 bytes), false sharing (<code>@Contended</code>), and the LMAX Disruptor lock-free Ring Buffer.",
        "question": """A high-frequency trading platform matches stock orders at 6 million transactions per second with sub-microsecond latency. Look at the code snippet.
<br><br>
<strong>Part A:</strong> The initial implementation used standard Java <code>ArrayBlockingQueue</code>. Under high concurrency, throughput peaked at 400,000 ops/sec with major latency jitter. Why do traditional lock-based queues cause <strong>Kernel Context-Switching & Cache-Line Bouncing</strong>?
<br>
<strong>Part B:</strong> How does the <strong>LMAX Disruptor Ring Buffer</strong> achieve 6M+ ops/sec using a pre-allocated circular array, sequence numbers, and lock-free CAS (Compare-And-Swap) operations?
<br>
<strong>Part C:</strong> What is <strong>False Sharing</strong> at the CPU L1/L2 cache line level (64 bytes), and how does cache-line padding (or Java's <code>@Contended</code> annotation) eliminate CPU cache invalidation stalls?""",
        "snippet_title": "OrderMatchingEngine.java",
        "snippet_code": """public class OrderMatchingEngine {

    // Bottleneck: ArrayBlockingQueue uses heavy ReentrantLock contention
    private final BlockingQueue<OrderCommand> queue = new ArrayBlockingQueue<>(1024);

    public void submitOrder(OrderCommand cmd) throws InterruptedException {
        queue.put(cmd); // Acquires putLock; contends with takeLock
    }

    public OrderCommand processNext() throws InterruptedException {
        return queue.take(); // Acquires takeLock
    }
}""",
        "rating_concept": "LMAX Disruptor lock-free ring buffer, false sharing, and CPU cache-line alignment",
        "solution": """<strong>Part A (The Pitfalls of Lock-Based Queues):</strong>
<br>• <code>ArrayBlockingQueue</code> uses <code>ReentrantLock</code> and condition variables.
<br>• When a lock cannot be acquired, the operating system suspends the thread, triggering an expensive <strong>Kernel Context Switch</strong> (costing 1,000–5,000 CPU cycles).
<br>• Multiple CPU cores contend for the same memory address (head and tail pointers), causing <strong>Cache-Line Bouncing</strong> across CPU L1/L2 caches (MESI invalidations).
<br><br>
<strong>Part B (How the LMAX Disruptor Works):</strong>
<br>1. <strong>Pre-allocated Circular Ring Buffer:</strong> Avoids GC allocation overhead entirely during runtime. Buffer size is a power of 2, allowing fast bitwise modulo operations (<code>sequence & (bufferSize - 1)</code>).
<br>2. <strong>Lock-Free Sequences:</strong> Uses monotonic atomic sequence numbers. Producers claim slots via lock-free CAS; consumers poll sequences without locks.
<br>3. <strong>Single-Writer Principle:</strong> When configured with a single writer thread, CAS is completely eliminated, running at raw memory bus speed.
<br><br>
<strong>Part C (False Sharing & Cache-Line Padding):</strong>
<br>• Modern CPUs read memory in <strong>64-byte Cache Lines</strong>.
<br>• If two independent variables (e.g. <code>head</code> and <code>tail</code>) sit in the same 64-byte line, when Core 1 updates <code>head</code>, it forces Core 2's L1 cache to <strong>invalidate the entire line</strong>, stalling Core 2.
<br>• <strong>Fix:</strong> Pad variables with 56 bytes of dummy long variables or use <code>@jdk.internal.vm.annotation.Contended</code> to ensure variables occupy their own dedicated 64-byte cache lines.""",
        "optimized_code": """// Cache-Line Padded Ring Buffer Sequence
public class PaddedSequence {
    // 56 bytes of padding before value to prevent false sharing
    protected long p1, p2, p3, p4, p5, p6, p7;
    protected volatile long value = 0;
    // 56 bytes of padding after value
    protected long a1, a2, a3, a4, a5, a6, a7;

    public long get() { return value; }
    public void set(long v) { this.value = v; }
}""",
        "junior_eval": "Suggests making the BlockingQueue larger (e.g. 100,000) or believes volatile variables do not incur CPU cache synchronization penalties.",
        "expert_eval": "Articulates Mechanical Sympathy, CPU L1/L2 cache line false sharing (64-byte MESI protocol), and the lock-free pre-allocated Ring Buffer architecture of the LMAX Disruptor."
    })

    # Q9: Multi-Level Caching Hierarchy & Invalidation
    questions.append({
        "id": 9,
        "badge": "Caching Tiers & Invalidation Patterns",
        "keywords": "caching hierarchy l1 l2 write through write behind cache aside stampede dual cache",
        "concept": "Multi-tier caching architecture (L1 In-Memory Caffeine + L2 Distributed Redis + L3 CDN), Cache-Aside vs Write-Through vs Write-Behind, and multi-cache synchronization.",
        "question": """A high-scale media catalog implements a multi-tier caching architecture to serve 200,000 reads per second. Look at the code snippet.
<br><br>
<strong>Part A:</strong> Contrast the 3 core caching patterns: <strong>Cache-Aside</strong> (Lazy Loading), <strong>Write-Through</strong>, and <strong>Write-Behind (Write-Back)</strong>. Under what failure scenario does Write-Behind risk permanent data loss?
<br>
<strong>Part B:</strong> The team deploys a two-tier caching hierarchy: <strong>L1 Local Cache</strong> (Caffeine in JVM memory: 100μs latency) and <strong>L2 Distributed Cache</strong> (Redis Cluster: 2ms latency). When an admin updates a product title on Pod 1, how do you prevent Pods 2, 3, and 4 from continuing to serve the stale title from their local L1 caches?
<br>
<strong>Part C:</strong> In a Cache-Aside pattern, why should you <strong>evict the cache key</strong> upon database update rather than writing the new value directly to the cache?""",
        "snippet_title": "ProductCatalogCache.java",
        "snippet_code": """@Service
public class ProductCatalogService {

    @Autowired
    private ProductRepository db;
    @Autowired
    private RedisTemplate<String, Product> redis;

    // Cache-Aside implementation
    public Product getProduct(Long id) {
        String key = "prod:" + id;
        Product cached = redis.opsForValue().get(key);
        if (cached != null) {
            return cached;
        }

        Product product = db.findById(id).orElseThrow();
        redis.opsForValue().set(key, product, Duration.ofHours(1));
        return product;
    }

    public void updateProduct(Product p) {
        db.save(p);
        // Question: Should we call redis.set() or redis.delete()?
    }
}""",
        "rating_concept": "Multi-level caching tiers, Cache-Aside eviction, and Redis Pub/Sub L1 invalidation",
        "solution": """<strong>Part A (Caching Patterns Comparison):</strong>
<br>• <strong>Cache-Aside:</strong> App reads cache; on miss, reads DB and populates cache. App writes directly to DB and evicts cache.
<br>• <strong>Write-Through:</strong> App writes to cache; cache synchronously writes to DB before acknowledging. (Zero stale cache, but higher write latency).
<br>• <strong>Write-Behind (Write-Back):</strong> App writes to cache immediately; cache asynchronously batches updates to DB in the background. (Blazing fast writes, but if the cache crashes before flushing to disk, <strong>data is permanently lost</strong>).
<br><br>
<strong>Part B (L1 / L2 Synchronization via Redis Pub/Sub):</strong>
<br>• Pod 1 updates the product in PostgreSQL and deletes the key in Redis (L2).
<br>• To clear local JVM Caffeine caches (L1) on Pods 2, 3, and 4, Pod 1 publishes an invalidation event to a Redis Pub/Sub channel: <code>redis.convertAndSend(\"cache-invalidation\", \"prod:101\")</code>.
<br>• All pods subscribe to this channel and immediately evict the key from their local Caffeine cache.
<br><br>
<strong>Part C (Why Evict Instead of Update Cache):</strong>
<br>Writing the new value to the cache introduces a race condition between concurrent updates:
<br>If Thread 1 writes DB ($V1$), Thread 2 writes DB ($V2$), but Thread 1's cache update executes <em>after</em> Thread 2's cache update due to network jitter, the cache permanently stores stale $V1$ while the DB has $V2$!
<br><strong>Evicting the key (delete)</strong> is idempotent and eliminates concurrent write race conditions.""",
        "optimized_code": """public void updateProduct(Product p) {
    db.save(p);
    // 1. Evict L2 Distributed Cache
    redis.delete("prod:" + p.getId());
    // 2. Broadcast invalidation to all L1 local caches across pods
    redis.convertAndSend("l1-cache-eviction-topic", "prod:" + p.getId());
}""",
        "junior_eval": "Updates the cache directly with redis.set() on DB update, unaware of concurrent write race conditions, or cannot explain how to invalidate local L1 JVM caches.",
        "expert_eval": "Compares Cache-Aside vs Write-Behind data-loss risks, proves why eviction is superior to updating, and designs Redis Pub/Sub invalidation channels for multi-tier L1/L2 cache coherency."
    })

    # Q10: Database Sharding & Consistent Hashing
    questions.append({
        "id": 10,
        "badge": "Data Partitioning & Scalability",
        "keywords": "database sharding consistent hashing hash ring virtual nodes modulo rebalancing",
        "concept": "Horizontal database sharding, limitations of naive modulo hashing, the <strong>Consistent Hashing Ring</strong>, virtual nodes (vnodes), and data rebalancing.",
        "question": """A social media platform stores 500 million user profiles partitioned across 4 PostgreSQL database shards. Look at the routing snippet.
<br><br>
<strong>Part A:</strong> The initial sharding algorithm uses naive modulo hashing: <code>shardId = hash(userId) % 4</code>. When traffic surges, the team adds a 5th database shard (changing formula to <code>% 5</code>). What percentage of all customer records must immediately be migrated across the network, and why does this cause a catastrophic production outage?
<br>
<strong>Part B:</strong> How does a <strong>Consistent Hashing Ring</strong> ($0$ to $2^{32}-1$) reduce data migration from 80% to only $\\frac{1}{N}$ when adding a new database node?
<br>
<strong>Part C:</strong> What is the purpose of <strong>Virtual Nodes (vnodes)</strong> in a Consistent Hashing ring? How do they prevent non-uniform data distribution and hotspotting?""",
        "snippet_title": "ShardRouter.java",
        "snippet_code": """public class ShardRouter {

    // Anti-Pattern: Naive Modulo Sharding
    public int getShardId(String userId, int totalShards) {
        int hash = Math.abs(userId.hashCode());
        return hash % totalShards; // When totalShards changes from 4 to 5: 80% of data moves!
    }
}""",
        "rating_concept": "Consistent Hashing, database sharding, virtual nodes, and non-uniform distribution prevention",
        "solution": """<strong>Part A (The Modulo Resharding Catastrophe):</strong>
<br>• Under naive modulo hashing: <code>hash % 4</code> vs <code>hash % 5</code>.
<br>• Mathematically, changing the divisor from 4 to 5 causes <strong>~80% of all existing keys to change their shard assignment</strong>!
<br>• Out of 500 million users, 400 million records must immediately be read from old databases and written to new databases over the network.
<br>• Database network links saturate, CPU hits 100%, and the system suffers hours of downtime during rebalancing.
<br><br>
<strong>Part B (Consistent Hashing Ring):</strong>
<br>• Both nodes and keys are mapped onto a circular mathematical ring ($0$ to $2^{32}-1$) using a uniform hash function (e.g. MurmurHash / MD5).
<br>• A key is stored on the <strong>first node encountered walking clockwise</strong> along the ring.
<br>• When a 5th node is added, it only claims a fraction of keys from its immediate clockwise neighbor.
<br>• Only $K/N$ (only <strong>20% of data</strong>) moves across the network, leaving 80% of data undisturbed!
<br><br>
<strong>Part C (Virtual Nodes / Vnodes):</strong>
<br>• If only 5 physical nodes exist on the ring, hashing randomness can place nodes close together, creating large empty arcs where one node receives 60% of all data (hotspots).
<br>• <strong>Virtual Nodes:</strong> Each physical server is assigned 100–256 distinct virtual positions on the ring (e.g. <code>Node1#1</code>, <code>Node1#2</code>...).
<br>• This blends keys uniformly across the entire ring, ensuring perfectly balanced storage and load distribution.""",
        "optimized_code": """public class ConsistentHashRing<T> {
    private final HashFunction hashFunction;
    private final int numberOfReplicas; // Virtual nodes per physical node
    private final SortedMap<Integer, T> circle = new TreeMap<>();

    public void add(T node) {
        for (int i = 0; i < numberOfReplicas; i++) {
            circle.put(hashFunction.hash(node.toString() + i), node);
        }
    }

    public T get(String key) {
        if (circle.isEmpty()) return null;
        int hash = hashFunction.hash(key);
        if (!circle.containsKey(hash)) {
            SortedMap<Integer, T> tailMap = circle.tailMap(hash);
            hash = tailMap.isEmpty() ? circle.firstKey() : tailMap.firstKey();
        }
        return circle.get(hash);
    }
}""",
        "junior_eval": "Uses modulo sharding without realizing that adding or removing a single node forces nearly all records to relocate.",
        "expert_eval": "Proves the mathematical migration formula of modulo sharding ((N-1)/N), diagrams the Consistent Hashing circular ring, and uses virtual nodes (vnodes) to guarantee uniform distribution."
    })

    # Q11: Event Sourcing & CQRS Synchronization
    questions.append({
        "id": 11,
        "badge": "Event-Driven & Ledger Systems",
        "keywords": "event sourcing cqrs event store projection snapshotting replay audit trail",
        "concept": "Event Sourcing architecture, storing state as an append-only event stream, CQRS read model projections, snapshotting, and event replayability.",
        "question": """A core banking engine records financial transactions. Look at the ledger architecture.
<br><br>
<strong>Part A:</strong> Contrast <strong>Traditional CRUD State Mutation</strong> (e.g. <code>UPDATE accounts SET balance = balance + 50 WHERE id = 101</code>) against <strong>Event Sourcing</strong>. Why is Event Sourcing the gold standard for financial, healthcare, and audit-sensitive domains?
<br>
<strong>Part B:</strong> If an account has 200,000 historical transactions, replaying all 200,000 events to calculate the current balance on every API read request causes severe latency. How does <strong>Snapshotting</strong> solve this performance issue?
<br>
<strong>Part C:</strong> When an event schema evolves (e.g. adding a new field <code>exchangeRate</code>), how do you maintain backward compatibility for historical events stored years ago without breaking event replays?""",
        "snippet_title": "BankAccountAggregate.java",
        "snippet_code": """public class BankAccountAggregate {
    private UUID accountId;
    private BigDecimal balance = BigDecimal.ZERO;
    private List<DomainEvent> uncommittedEvents = new ArrayList<>();

    // Event Sourcing: State is reconstructed strictly by applying past events
    public void apply(MoneyDepositedEvent event) {
        this.balance = this.balance.add(event.getAmount());
    }

    public void apply(MoneyWithdrawnEvent event) {
        this.balance = this.balance.subtract(event.getAmount());
    }

    public void withdraw(BigDecimal amount) {
        if (this.balance.compareTo(amount) < 0) {
            throw new InsufficientFundsException();
        }
        applyAndRecord(new MoneyWithdrawnEvent(this.accountId, amount, Instant.now()));
    }
}""",
        "rating_concept": "Event Sourcing, append-only Event Store, snapshotting, and schema evolution (upcasters)",
        "solution": """<strong>Part A (CRUD Mutation vs Event Sourcing):</strong>
<br>• <strong>CRUD Mutation:</strong> Overwrites current state. You lose the context of <em>why</em> and <em>how</em> data changed; deletes destroy historical evidence.
<br>• <strong>Event Sourcing:</strong> The append-only event stream is the <strong>source of truth</strong>.
<br>• <em>Benefits:</em> 100% complete audit trail, perfect time-travel debugging (rebuilding state as of any point in history), retroactive analytics, and zero write-lock contention on account balance rows.
<br><br>
<strong>Part B (Snapshotting Optimization):</strong>
<br>• Periodically (e.g. every 500 events or nightly), write a consolidated <strong>Snapshot</strong> of the aggregate's current state to an optimized key-value store (e.g. DynamoDB/S3).
<br>• When loading the account, load the latest snapshot (Version 10,000: Balance $50,000) and replay <strong>only the 12 events</strong> that occurred since Version 10,000. Reduces recovery time from 2 seconds to 2 milliseconds.
<br><br>
<strong>Part C (Event Schema Evolution & Upcasters):</strong>
<br>• Never mutate historical events in the Event Store.
<br>• Use <strong>Event Upcasters</strong>: Intermediary transformer classes that intercept old V1 events during deserialization and migrate them in-memory to V2 representations before passing them to the Aggregate.""",
        "optimized_code": """public class AccountSnapshotStore {
    public BankAccount load(UUID accountId) {
        Snapshot latest = snapshotRepo.findLatest(accountId);
        BankAccount account = new BankAccount(latest);

        // Replay ONLY events created after snapshot timestamp
        List<DomainEvent> recentEvents = eventStore.readEvents(accountId, latest.getVersion());
        for (DomainEvent event : recentEvents) {
            account.apply(event);
        }
        return account;
    }
}""",
        "junior_eval": "Suggests updating past events directly in the Event Store database or replaying all 200,000 events on every single HTTP read query.",
        "expert_eval": "Articulates Event Sourcing audit immutability, designs snapshotting tiers for sub-millisecond aggregate loading, and builds in-memory Event Upcasters for schema evolution."
    })

    # Q12: Microservices Decomposition: The Strangler Fig Pattern
    questions.append({
        "id": 12,
        "badge": "Legacy Migration & Modernization",
        "keywords": "strangler fig pattern legacy migration monolith to microservices api gateway dark launching",
        "concept": "Decomposing monolithic applications safely without big-bang rewrites using the <strong>Strangler Fig Pattern</strong>, reverse proxy routing, and dark launching.",
        "question": """An enterprise bank needs to replace a 15-year-old monolithic core banking application with modern microservices. Look at the modernization architecture.
<br><br>
<strong>Part A:</strong> Why are \"Big Bang\" rewrites (stopping development on the monolith for 2 years to rebuild everything from scratch) considered a notorious failure pattern in enterprise software engineering?
<br>
<strong>Part B:</strong> Explain the step-by-step execution of the <strong>Strangler Fig Pattern</strong>. How does an API Gateway or Reverse Proxy intercept and gradually reroute traffic from the monolith to new microservices?
<br>
<strong>Part C:</strong> What is <strong>Dark Launching (Shadow Traffic)</strong>? How does duplicating live production traffic to a new microservice verify performance and business accuracy before making it authoritative?""",
        "snippet_title": "gateway-strangler-routes.yml",
        "snippet_code": """# API Gateway Routing - Strangler Fig Phase 1
routes:
  # Intercept and route extracted domain to new Microservice
  - id: payment-microservice
    uri: lb://PAYMENT-SERVICE
    predicates:
      - Path=/api/v1/payments/**

  # Default fallback: All other routes continue hitting Legacy Monolith
  - id: legacy-monolith-fallback
    uri: http://legacy-monolith.internal:8080
    predicates:
      - Path=/**""",
        "rating_concept": "Strangler Fig Pattern, monolith decomposition, and dark launching shadow traffic",
        "solution": """<strong>Part A (The Fallacy of the Big Bang Rewrite):</strong>
<br>• Monoliths accumulate 15 years of undocumented edge cases, regulatory fixes, and hidden business logic.
<br>• Stopping feature development for 2 years stalls business competitiveness.
<br>• By the time the new system is ready, business requirements have evolved, leading to missed deadlines, budget blowouts, and 80%+ failure rates.
<br><br>
<strong>Part B (The Strangler Fig Step-by-Step Architecture):</strong>
<br>1. <strong>Place Edge Gateway:</strong> Insert an API Gateway or reverse proxy in front of the monolith. Initially, 100% of traffic routes to the monolith.
<br>2. <strong>Identify First Bounded Context:</strong> Pick a well-defined domain (e.g. Payments) with high business value or scale requirements.
<br>3. <strong>Build Microservice:</strong> Build the new Payment Microservice in modern architecture.
<br>4. <strong>Reroute Traffic:</strong> Update Gateway routing to send <code>/api/v1/payments/**</code> to the new service while all other paths hit the monolith.
<br>5. <strong>Repeat:</strong> Gradually strangle other capabilities until the legacy monolith is shrunk to zero and decommissioned.
<br><br>
<strong>Part C (Dark Launching / Shadow Traffic):</strong>
<br>The Gateway duplicates incoming live production requests (e.g. via Envoy <code>shadow_policy</code>).
<br>Traffic is sent asynchronously to the new microservice, discarding its response to clients while comparing its output and performance with the monolith in real time, eliminating cutover risk.""",
        "optimized_code": """# Envoy Shadow Traffic Configuration for Dark Launching
route:
  cluster: legacy-monolith
  request_mirror_policies:
    - cluster: new-payment-microservice
      runtime_fraction:
        default_value:
          numerator: 100
          denominator: HUNDRED""",
        "junior_eval": "Advocates freezing all feature work to rewrite the entire monolith from scratch or tries to extract database tables without an edge proxy routing strategy.",
        "expert_eval": "Outlines the Strangler Fig incremental extraction lifecycle, configures edge gateway interception, and implements dark launching (shadow traffic) for risk-free verification."
    })

    # Q13: API Rate Limiting & Denial-of-Service Defense
    questions.append({
        "id": 13,
        "badge": "API Security & DDoS Mitigation",
        "keywords": "rate limiting token bucket leaky bucket ddos waf cloudflare layer 7 bot mitigation",
        "concept": "Multi-tier rate limiting and DDoS mitigation architecture: Edge WAF, API Gateway Token Bucket, Redis distributed counters, and Layer 7 bot defense.",
        "question": """A public fintech API experiences a credential-stuffing and distributed denial-of-service (DDoS) attack sending 500,000 requests/sec. Look at the architecture.
<br><br>
<strong>Part A:</strong> What is the difference between a <strong>Layer 3/4 Volumetric DDoS attack</strong> (SYN floods, UDP reflection) and a <strong>Layer 7 Application DDoS attack</strong> (HTTP GET/POST flood)? Why can't standard server firewalls stop Layer 7 attacks?
<br>
<strong>Part B:</strong> Where should rate limiting be placed in an enterprise architecture? Contrast <strong>Edge Rate Limiting</strong> (Cloudflare / AWS WAF) against <strong>Gateway Rate Limiting</strong> (Spring Cloud Gateway / Kong) and <strong>Application-Level Rate Limiting</strong>.
<br>
<strong>Part C:</strong> How do you design tiered rate limits that distinguish anonymous guests (e.g. 10 req/min), standard authenticated users (1,000 req/min), and enterprise API partners (100,000 req/min)?""",
        "snippet_title": "TieredRateLimitResolver.java",
        "snippet_code": """public class TieredRateLimitResolver {

    public RateLimitTier resolveTier(HttpServletRequest request) {
        String apiKey = request.getHeader("X-API-KEY");
        String jwt = request.getHeader("Authorization");

        // Architect question: How to resolve tier and enforce quotas 
        // across distributed nodes without bottlenecking Redis?
        return null;
    }
}""",
        "rating_concept": "Layer 7 DDoS defense, multi-tier rate limiting (WAF vs Gateway), and tier-based quotas",
        "solution": """<strong>Part A (Layer 3/4 vs Layer 7 Attacks):</strong>
<br>• <strong>Layer 3/4 (Network/Transport):</strong> Exhausts network bandwidth and OS TCP connection states (SYN floods, NTP reflection). Mitigated by edge scrubbing networks (AWS Shield, Cloudflare Anycast).
<br>• <strong>Layer 7 (Application):</strong> Legitimate HTTP requests that mimic real users (e.g. searching complex queries or submitting logins). Server firewalls see valid TCP/TLS packets and let them pass. The database and CPU become exhausted computing heavy business logic.
<br><br>
<strong>Part B (Defense-in-Depth Placement):</strong>
<br>1. <strong>Edge WAF (Cloudflare/AWS WAF):</strong> Blocks malicious IP ranges, enforces bot challenges (CAPTCHA), and blocks IP rate spikes before traffic touches your VPC.
<br>2. <strong>API Gateway (Kong/Envoy):</strong> Enforces API Key quotas and customer SLA rate limits via distributed Redis token buckets.
<br>3. <strong>Application Service:</strong> Enforces business-domain limits (e.g. max 5 password attempts per hour per account).
<br><br>
<strong>Part C (Tiered Quotas & Token Bucket Resolution):</strong>
<br>Extract customer identity at the Gateway edge (API Key or JWT claims).
<br>Resolve tenant tier from a local in-memory cache (Guava/Caffeine).
<br>Execute an atomic Redis Lua script matching the specific tier's bucket capacity and refill rate.""",
        "optimized_code": """public RateLimitPolicy resolvePolicy(ClientPrincipal client) {
    if (client.isEnterprisePartner()) {
        return new RateLimitPolicy(100000, Duration.ofMinutes(1));
    } else if (client.isAuthenticated()) {
        return new RateLimitPolicy(1000, Duration.ofMinutes(1));
    }
    return new RateLimitPolicy(10, Duration.ofMinutes(1)); // Anonymous guest
}""",
        "junior_eval": "Places rate-limiting logic inside the database or attempts to mitigate L7 HTTP floods using operating system iptables rules.",
        "expert_eval": "Distinguishes L3/L4 from L7 application attacks, implements multi-tiered defense (WAF edge -> Gateway token bucket -> Application), and models tier-based quotas."
    })

    # Q14: Design Patterns in Enterprise Systems: Strategy vs Factory
    questions.append({
        "id": 14,
        "badge": "Design Patterns & Extensibility",
        "keywords": "design patterns strategy factory open closed principle ocp spring registry refactoring",
        "concept": "GoF Enterprise Design Patterns, refactoring brittle <code>switch/if-else</code> blocks using the <strong>Strategy Pattern</strong> and Spring-managed bean registries, enforcing the Open-Closed Principle (OCP).",
        "question": """A payment gateway processes transactions across Credit Cards, PayPal, ApplePay, and Crypto. Look at the code snippet.
<br><br>
<strong>Part A:</strong> Look at the <code>processPayment()</code> method. Why does using a giant <code>switch</code> or <code>if/else</code> chain violate the <strong>Open-Closed Principle (OCP)</strong>? What happens to testing and git merge conflicts when 5 developers add new payment methods simultaneously?
<br>
<strong>Part B:</strong> Refactor this code using the <strong>Strategy Pattern</strong> combined with Spring's automatic Map dependency injection (<code>Map&lt;String, PaymentStrategy&gt;</code>).
<br>
<strong>Part C:</strong> Contrast the <strong>Strategy Pattern</strong> against the <strong>State Pattern</strong>. When does a state machine become necessary over simple strategy polymorphism?""",
        "snippet_title": "MonolithicPaymentProcessor.java",
        "snippet_code": """@Service
public class MonolithicPaymentProcessor {

    // Anti-Pattern: Monolithic switch violating Open-Closed Principle
    public PaymentResult processPayment(String type, PaymentCommand cmd) {
        if ("CREDIT_CARD".equalsIgnoreCase(type)) {
            // 40 lines of credit card logic
            return executeCreditCard(cmd);
        } else if ("PAYPAL".equalsIgnoreCase(type)) {
            // 35 lines of PayPal OAuth and capture
            return executePayPal(cmd);
        } else if ("APPLE_PAY".equalsIgnoreCase(type)) {
            // 50 lines of token decryption
            return executeApplePay(cmd);
        } else {
            throw new IllegalArgumentException("Unsupported payment type: " + type);
        }
    }

    private PaymentResult executeCreditCard(PaymentCommand c) { return null; }
    private PaymentResult executePayPal(PaymentCommand c) { return null; }
    private PaymentResult executeApplePay(PaymentCommand c) { return null; }
}""",
        "rating_concept": "Strategy Pattern refactoring, Open-Closed Principle (OCP), and Spring bean map injection",
        "solution": """<strong>Part A (The OCP Violation & Merge Conflict Hell):</strong>
<br>• The Open-Closed Principle states: <em>\"Classes should be open for extension, but closed for modification.\"</em>
<br>• In the switch-statement design, adding a new payment method (e.g. \"KLARNA\") forces developers to <strong>modify the core processor class</strong>.
<br>• Every new feature edits the same file, causing merge conflicts in Git.
<br>• A bug introduced in one payment method can inadvertently crash unrelated payment channels.
<br><br>
<strong>Part B (Refactoring with Strategy & Spring Bean Registry):</strong>
<br>1. Define a common interface: <code>PaymentStrategy</code> with <code>execute(PaymentCommand cmd)</code>.
<br>2. Implement concrete strategy classes: <code>CreditCardPaymentStrategy</code>, <code>PayPalPaymentStrategy</code>.
<br>3. In the coordinator service, inject <code>Map&lt;String, PaymentStrategy&gt;</code>. Spring automatically discovers and registers all matching beans into the map! Adding a new payment method requires <strong>zero changes</strong> to existing classes.
<br><br>
<strong>Part C (Strategy vs State Pattern):</strong>
<br>• <strong>Strategy:</strong> The client chooses a strategy for an isolated algorithm; strategies are independent and typically stateless.
<br>• <strong>State Pattern:</strong> An object's behavior changes dynamically based on its internal state machine (e.g., Order transitioning from <code>DRAFT</code> &rarr; <code>PAID</code> &rarr; <code>SHIPPED</code>). State objects trigger transitions to other states.""",
        "optimized_code": """public interface PaymentStrategy {
    PaymentResult execute(PaymentCommand cmd);
    String getSupportedType();
}

@Service
public class PaymentEngine {
    private final Map<String, PaymentStrategy> strategies;

    // Spring auto-injects all PaymentStrategy implementations into the map
    public PaymentEngine(List<PaymentStrategy> strategyList) {
        this.strategies = strategyList.stream()
            .collect(Collectors.toMap(PaymentStrategy::getSupportedType, s -> s));
    }

    public PaymentResult process(String type, PaymentCommand cmd) {
        PaymentStrategy strategy = strategies.get(type.toUpperCase());
        if (strategy == null) throw new UnsupportedOperationException("Invalid type: " + type);
        return strategy.execute(cmd);
    }
}""",
        "junior_eval": "Keeps adding else-if branches to the monolithic class or creates complex reflection lookups manually.",
        "expert_eval": "Applies the Open-Closed Principle rigorously, leverages Spring's auto-wiring of bean maps for plugin-like extensibility, and articulates Strategy vs State pattern boundaries."
    })

    # Q15: Distributed Locking: Redlock vs Database Advisory Locks
    questions.append({
        "id": 15,
        "badge": "Distributed Concurrency & Mutual Exclusion",
        "keywords": "distributed lock redlock redis advisory lock fencing token gc pause martin kleppmann",
        "concept": "Distributed mutual exclusion, Martin Kleppmann's critique of Redis Redlock (GC pause leases, clock drift), fencing tokens, and PostgreSQL Advisory Locks.",
        "question": """A financial settlement batch job runs on a scheduled cron across 10 Kubernetes pods. Look at the distributed locking snippet.
<br><br>
<strong>Part A:</strong> The job acquires a distributed lock via Redis with a 30-second TTL. While Pod 1 is processing, it encounters a 35-second Stop-The-World JVM Garbage Collection pause. What happens to the lock lease, and how does this cause <strong>Split-Brain duplicate processing</strong> when Pod 2 acquires the expired lock?
<br>
<strong>Part B:</strong> Explain Martin Kleppmann's famous critique of the <strong>Redis Redlock algorithm</strong> regarding wall-clock drift, GC pauses, and out-of-order execution.
<br>
<strong>Part C:</strong> How do <strong>Fencing Tokens</strong> (monotonically increasing version counters) prevent stale lock holders from corrupting backend datastores? Compare Redis locking against <strong>PostgreSQL Advisory Locks</strong> for database-centric workflows.""",
        "snippet_title": "ScheduledSettlementJob.java",
        "snippet_code": """@Component
public class ScheduledSettlementJob {

    @Autowired
    private RedissonClient redisson;

    @Scheduled(cron = "0 0 2 * * ?") // 2 AM Daily Settlement
    public void runSettlement() {
        RLock lock = redisson.getLock("settlement-lock");
        // Flaw: Fixed 30s lease time without watchdog renewal or fencing tokens
        if (lock.tryLock(5, 30, TimeUnit.SECONDS)) {
            try {
                executeHeavyBatchSettlement(); // Takes 45 seconds under load!
            } finally {
                lock.unlock();
            }
        }
    }
}""",
        "rating_concept": "Distributed locking failure modes, GC pause lease expiration, and Fencing Tokens",
        "solution": """<strong>Part A (The GC Pause Lease Expiration Trap):</strong>
<br>1. Pod 1 acquires the lock with a 30-second lease.
<br>2. Pod 1 enters a 35-second JVM Stop-The-World GC pause or network stall. All application threads are frozen.
<br>3. After 30 seconds, Redis automatically expires the key (TTL = 0).
<br>4. Pod 2 requests the lock; Redis grants it. Pod 2 begins executing the settlement.
<br>5. Pod 1 wakes up from its GC pause. Believing it still owns the lock, it resumes processing.
<br>6. <strong>Both Pod 1 and Pod 2 execute the settlement concurrently</strong>, double-charging accounts and corrupting financial ledgers!
<br><br>
<strong>Part B (Martin Kleppmann's Redlock Critique):</strong>
<br>Distributed locks relying on physical wall clocks (NTP time) cannot guarantee safety for storage:
<br>• NTP clock jumps can prematurely expire locks.
<br>• Process pauses (GC, hypervisor stealing CPU, page faults) can freeze the lock owner.
<br>• Network delays can delay packets until after the lease has expired.
<br><br>
<strong>Part C (Fencing Tokens & Postgres Advisory Locks):</strong>
<br>• <strong>Fencing Token:</strong> Every time a lock is acquired, the lock server issues a monotonically increasing token ($1, 2, 3...$).
<br>• The storage layer (DB) accepts writes <strong>only if the token is greater than the highest token seen so far</strong>. When Pod 1 wakes up with Token 1, the database rejects its write because Pod 2 already wrote with Token 2!
<br>• <strong>Postgres Advisory Locks:</strong> Bound to the physical database connection session. If the connection drops or times out, the database automatically releases the lock immediately.""",
        "optimized_code": """// Fencing Token Database Update
@Modifying
@Query("UPDATE SettlementAccount s SET s.balance = :bal, s.lockVersion = :token " +
       "WHERE s.id = :id AND s.lockVersion < :token")
int updateWithFencing(@Param("id") Long id, @Param("bal") BigDecimal bal, @Param("token") long token);""",
        "junior_eval": "Increases the lock lease time from 30s to 1 hour or believes tryLock() is immune to concurrent race conditions.",
        "expert_eval": "Diagnoses JVM GC pause lease expiration, details Martin Kleppmann's Redlock critique, implements monotonically increasing Fencing Tokens, and evaluates Postgres Advisory Locks."
    })

    # Q16: Data Streaming & Log Compaction in Apache Kafka
    questions.append({
        "id": 16,
        "badge": "Streaming Systems & Message Brokers",
        "keywords": "kafka log compaction retention tombstones consumer group rebalance partition",
        "concept": "Apache Kafka log internals, Time-Based Retention vs Log Compaction (changelogs), Tombstone records, partition assignment strategies, and eliminating rebalance storms.",
        "question": """A customer profile microservice streams state updates through Apache Kafka. Look at the topic configuration and scenario.
<br><br>
<strong>Part A:</strong> A topic stores customer profile changes. Over two years, the topic size grows to 80 Terabytes because default time-based retention is disabled. When a new analytics microservice starts up, it takes 36 hours to read the entire topic from offset 0! How does <strong>Kafka Log Compaction</strong> reduce topic size and bootstrap time?
<br>
<strong>Part B:</strong> How does Log Compaction handle record deletions? What is a <strong>Tombstone Record</strong>, and what happens if a consumer is offline longer than <code>delete.retention.ms</code>?
<br>
<strong>Part C:</strong> What is a <strong>Kafka Consumer Rebalance Storm</strong>? How does the <strong>Cooperative Sticky Assignor</strong> (introduced in Kafka 2.4+) eliminate the \"Stop-The-World\" pause of the Eager Rebalance protocol?""",
        "snippet_title": "kafka-topic-config.sh",
        "snippet_code": """# Problematic Kafka Topic Configuration
kafka-topics.sh --create --topic customer-profile-updates \\
  --partitions 12 --replication-factor 3 \\
  --config cleanup.policy=delete \\
  --config retention.ms=-1 # Infinite growth: Retains all 80TB of intermediate history!""",
        "rating_concept": "Kafka Log Compaction, Tombstone records, and Cooperative Sticky Assignor rebalances",
        "solution": """<strong>Part A (Log Compaction vs Time-Based Retention):</strong>
<br>• <strong>cleanup.policy=delete:</strong> Discards records older than a configured time (e.g. 7 days). If set to -1, every transient update is stored forever.
<br>• <strong>cleanup.policy=compact:</strong> Kafka retains the <strong>latest record for each primary message key</strong> within the partition log.
<br>• Intermediate updates (e.g. User 101 changing address 50 times) are purged during background cleaner thread passes.
<br>• The topic size shrinks from 80 TB to 50 GB (storing only current state), allowing new consumer pods to bootstrap in seconds rather than days.
<br><br>
<strong>Part B (Tombstone Records & Deletion Retention):</strong>
<br>• To delete a key in a compacted topic, a producer emits a record with the target key and a <strong>null payload</strong> (called a <strong>Tombstone</strong>).
<br>• The cleaner thread retains the tombstone for a configurable duration (<code>delete.retention.ms</code>, default 24 hours) so active consumers can read the null payload and delete the record locally.
<br>• If a consumer remains offline longer than 24 hours, the tombstone is garbage-collected; when the consumer wakes up, it misses the delete signal and retains zombie data!
<br><br>
<strong>Part C (Cooperative Sticky Rebalances):</strong>
<br>• <strong>Eager Rebalance (Legacy):</strong> When a consumer joins/leaves, all consumers revoke all assigned partitions and stop consuming (Stop-the-World).
<br>• <strong>Cooperative Sticky:</strong> Consumers continue processing unaffected partitions seamlessly, revoking and reassigning only the specific partitions that need to migrate.""",
        "optimized_code": """kafka-topics.sh --create --topic customer-profile-compacted \\
  --partitions 12 --replication-factor 3 \\
  --config cleanup.policy=compact \\
  --config min.cleanable.dirty.ratio=0.5 \\
  --config segment.ms=86400000 \\
  --config delete.retention.ms=86400000""",
        "junior_eval": "Suggests deleting the entire Kafka topic or increasing consumer fetch size to speed up reading 80TB of raw logs.",
        "expert_eval": "Configures Kafka Log Compaction for changelogs, explains Tombstone null-payload mechanics and delete.retention.ms hazards, and enables Cooperative Sticky Assignors."
    })

    # Q17: Zero-Downtime Database Schema Migrations: Expand & Contract
    questions.append({
        "id": 17,
        "badge": "Database Lifecycle & Zero-Downtime Migrations",
        "keywords": "database migration zero downtime expand contract liquibase flyway column rename",
        "concept": "Zero-downtime relational database schema migrations (Liquibase / Flyway), the <strong>Expand and Contract Pattern</strong>, adding non-null columns, and safe column renaming.",
        "question": """A continuous deployment pipeline releases 5 times a day to a cluster of 50 Kubernetes pods. Look at the database migration script.
<br><br>
<strong>Part A:</strong> A developer executes a Flyway migration script that renames a column in PostgreSQL: <code>ALTER TABLE users RENAME COLUMN phone_number TO contact_number;</code>. During the 10-minute rolling deployment, 50% of incoming user requests crash with <code>PSQLException: column \"phone_number\" does not exist</code>. Why did this happen?
<br>
<strong>Part B:</strong> Walk through the 3 phases of the <strong>Expand and Contract Pattern</strong> to safely rename a database column across rolling deployments with zero downtime.
<br>
<strong>Part C:</strong> How do you safely add a <code>NOT NULL</code> constraint to a large 100-million row table in PostgreSQL without locking the table and causing application connection timeouts?""",
        "snippet_title": "V2__rename_phone.sql",
        "snippet_code": """-- Problematic Migration Script Executed During Rolling Deploy
ALTER TABLE users RENAME COLUMN phone_number TO contact_number;
ALTER TABLE users ALTER COLUMN contact_number SET NOT NULL;""",
        "rating_concept": "Expand and Contract database migrations, zero-downtime rolling deploys, and non-blocking NOT NULL",
        "solution": """<strong>Part A (The Mixed-Version Rolling Deployment Collision):</strong>
<br>• During a rolling deployment, both <strong>Version 1 (old pods)</strong> and <strong>Version 2 (new pods)</strong> run simultaneously in parallel.
<br>• Renaming the column immediately breaks Version 1 pods because their JPA entities and SQL queries still reference <code>phone_number</code>.
<br>• Every query executed by an old pod fails with <code>PSQLException: column phone_number does not exist</code>, causing a 10-minute partial site outage.
<br><br>
<strong>Part B (The 3 Phases of Expand and Contract):</strong>
<br>1. <strong>Phase 1 (Expand - Deploy DB Migration 1 & Code V1.1):</strong>
<br>• Add the new column <code>contact_number</code> as nullable.
<br>• Update application code to <strong>write to both columns</strong> (dual-write) and read from <code>phone_number</code>.
<br>• Run a background data backfill script to copy old phone numbers to <code>contact_number</code>.
<br>2. <strong>Phase 2 (Migrate - Deploy Code V2):</strong>
<br>• Update application to read strictly from <code>contact_number</code>. Old column is no longer read.
<br>3. <strong>Phase 3 (Contract - Deploy DB Migration 2):</strong>
<br>• Drop the dual-write logic and safely execute: <code>ALTER TABLE users DROP COLUMN phone_number;</code>.
<br><br>
<strong>Part C (Adding NOT NULL to 100M Rows Without Locking):</strong>
<br>1. Add a check constraint as NOT VALID (acquires short lock without scanning table):<br><code>ALTER TABLE users ADD CONSTRAINT check_contact_not_null CHECK (contact_number IS NOT NULL) NOT VALID;</code>
<br>2. Validate constraint asynchronously without table lock:<br><code>ALTER TABLE users VALIDATE CONSTRAINT check_contact_not_null;</code>""",
        "optimized_code": """-- Phase 1: Expand (Safe non-blocking migration)
ALTER TABLE users ADD COLUMN contact_number VARCHAR(32);

-- Phase 3: Contract (After Code V2 has run in production for 2 weeks)
ALTER TABLE users DROP COLUMN phone_number;""",
        "junior_eval": "Executes ALTER TABLE RENAME COLUMN directly in production during business hours or suggests scheduling maintenance downtime for simple schema changes.",
        "expert_eval": "Designs a 3-stage Expand and Contract pipeline with dual-writing, backfilling, and contracting phases, and uses NOT VALID check constraints to avoid exclusive table locks."
    })

    # Q18: Application Performance Optimization: Profiling & FlameGraphs
    questions.append({
        "id": 18,
        "badge": "Performance Engineering & Profiling",
        "keywords": "performance profiling async-profiler flamegraph cpu bottleneck memory leak mat",
        "concept": "Methodical application performance engineering, CPU and allocation profiling (Async-Profiler, FlameGraphs), diagnosing thread contention, and memory leak triage with Heap Dumps.",
        "question": """In a production microservice serving 15,000 requests/sec, CPU utilization spikes to 98%, and latency jumps from 15ms to 850ms. Look at the code snippet.
<br><br>
<strong>Part A:</strong> An inexperienced engineer suggests immediately scaling out from 4 to 20 instances. What is <strong>Amdahl's Law</strong>, and why does scaling out compute fail to solve bottlenecks caused by shared database locks or thread synchronization?
<br>
<strong>Part B:</strong> What is a <strong>FlameGraph</strong> generated by <code>Async-Profiler</code>? How do you interpret the width of a frame on the horizontal axis vs the vertical stack trace depth?
<br>
<strong>Part C:</strong> Look at the code snippet. Profiling reveals that 75% of total CPU time is consumed by <code>Pattern.compile()</code> inside <code>validateEmail()</code>. Explain why compiling regexes inside a method is a severe CPU bottleneck, and write the zero-allocation fix.""",
        "snippet_title": "OrderValidationUtility.java",
        "snippet_code": """public class OrderValidationUtility {

    // Invoked 15,000 times per second across worker threads
    public boolean validateOrder(OrderRequest request) {
        if (!validateEmail(request.getCustomerEmail())) {
            return false;
        }
        return request.getAmount() > 0;
    }

    private boolean validateEmail(String email) {
        // Severe CPU Bottleneck: Compiles NFA regex state machine on EVERY call!
        Pattern emailPattern = Pattern.compile("^[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,6}$", Pattern.CASE_INSENSITIVE);
        return emailPattern.matcher(email).matches();
    }
}""",
        "rating_concept": "CPU profiling FlameGraphs, Amdahl's Law, and compiled regex state-machine optimization",
        "solution": """<strong>Part A (Amdahl's Law & The Limits of Scaling):</strong>
<br>• Amdahl's Law states: $S_{\\text{latency}} = \\frac{1}{(1 - p) + \\frac{p}{s}}$, where $p$ is the parallelizable portion of code.
<br>• If a bottleneck is caused by a shared resource (database row locks, connection pool exhaustion, or synchronized blocks), adding more instances does <strong>not reduce latency</strong>.
<br>• In fact, adding 16 more instances will increase database connection contention and context switching, degrading performance even further!
<br><br>
<strong>Part B (Interpreting CPU FlameGraphs):</strong>
<br>• <strong>Horizontal Width:</strong> Represents the <strong>percentage of CPU time</strong> spent in that method and its children (wider frame = more CPU consumed).
<br>• <strong>Vertical Axis:</strong> Represents the call stack depth (the top of the stack is the method currently executing on the CPU).
<br>• Look for wide \"plateaus\" at the top of the graph: these are your primary CPU hot spots.
<br><br>
<strong>Part C (Regex Compilation State Machine Bottleneck):</strong>
<br>• <code>Pattern.compile()</code> compiles the regex string into an internal Non-deterministic Finite Automaton (NFA) state machine, creating thousands of objects and consuming heavy CPU cycles.
<br>• Compiling it 15,000 times per second wastes 75% of server CPU.
<br>• <strong>Fix:</strong> <code>Pattern</code> is thread-safe! Compile it <strong>once</strong> into a <code>private static final Pattern</code> constant.""",
        "optimized_code": """public class OrderValidationUtility {

    // Thread-safe: Compiled ONCE at class loading; zero CPU compilation overhead
    private static final Pattern EMAIL_PATTERN = Pattern.compile(
        "^[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,6}$", 
        Pattern.CASE_INSENSITIVE
    );

    public boolean validateEmail(String email) {
        return EMAIL_PATTERN.matcher(email).matches();
    }
}""",
        "junior_eval": "Immediately recommends throwing more cloud hardware/VMs at the problem without analyzing CPU profiles or understanding regex compilation overhead.",
        "expert_eval": "Applies Amdahl's Law to diagnose concurrency limits, reads Async-Profiler FlameGraphs by frame width, and refactors compiled regexes and string allocations into static thread-safe singletons."
    })

    # Q19: Hexagonal Architecture (Ports and Adapters)
    questions.append({
        "id": 19,
        "badge": "Architectural Styles & Clean Architecture",
        "keywords": "hexagonal architecture ports and adapters clean architecture domain layer dependency inversion",
        "concept": "Hexagonal Architecture (Ports and Adapters / Clean Architecture), the Dependency Rule, isolating domain business logic from frameworks (Spring/JPA), and pure testability.",
        "question": """An enterprise migrates a core payment service from a standard 3-tier Layered Architecture to Hexagonal Architecture (Ports and Adapters). Look at the domain entity snippet.
<br><br>
<strong>Part A:</strong> In traditional 3-Tier Layered Architecture (Controller &rarr; Service &rarr; Repository), why does annotating the core domain model with JPA annotations (<code>@Entity</code>, <code>@Table</code>, <code>@Id</code>) violate the fundamental Dependency Inversion Principle?
<br>
<strong>Part B:</strong> Explain the core architectural concepts of <strong>Ports</strong> (interfaces) versus <strong>Adapters</strong> (implementations) in Hexagonal Architecture. What is the difference between a <strong>Driving (Primary) Port</strong> and a <strong>Driven (Secondary) Port</strong>?
<br>
<strong>Part C:</strong> How does Hexagonal Architecture enable running 100% of core domain business logic unit tests without running an embedded database, starting a Spring container, or mocking HTTP frameworks?""",
        "snippet_title": "DomainPayment.java",
        "snippet_code": """// Anti-Pattern in Clean Architecture: Leaking ORM and Framework into Domain
@Entity
@Table(name = "payments")
public class Payment {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private BigDecimal amount;

    // Domain business logic tightly coupled to JPA framework
    public void authorize() {
        if (this.amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException();
        }
    }
}""",
        "rating_concept": "Hexagonal Architecture, Ports and Adapters, the Dependency Rule, and domain isolation",
        "solution": """<strong>Part A (The Framework Coupling Trap in Layered Architecture):</strong>
<br>• In standard Layered Architecture, the database schema dictates the domain model.
<br>• By placing <code>@Entity</code>, <code>@Table</code>, and <code>@ManyToOne</code> directly inside domain classes, the domain business logic becomes a slave to the relational database framework.
<br>• If you need to switch persistence (e.g. from PostgreSQL to DynamoDB or MongoDB), you are forced to refactor your core business rules.
<br><br>
<strong>Part B (Ports and Adapters Mechanics):</strong>
<br>• <strong>The Domain Core:</strong> Contains pure business rules and entities with <strong>zero external framework dependencies</strong> (no Spring, no Hibernate).
<br>• <strong>Driving (Primary) Ports & Adapters:</strong>
<br><em>Port:</em> Use case interface exposed by domain (e.g. <code>ProcessPaymentUseCase</code>).
<br><em>Adapter:</em> REST Controller or CLI that calls the Driving Port.
<br>• <strong>Driven (Secondary) Ports & Adapters:</strong>
<br><em>Port:</em> Output interface defined by domain (e.g. <code>PaymentRepositoryPort</code>).
<br><em>Adapter:</em> Spring Data JPA repository or external Stripe client that implements the Driven Port.
<br><br>
<strong>Part C (Pure Isolated Testability):</strong>
<br>Because the domain core has zero framework annotations or database imports, unit tests instantiate pure Java POJOs directly in memory.
<br>Complex business logic tests execute in <strong>sub-millisecond time</strong> (1,000 tests in 50ms) without starting a Spring application context or spinning up Testcontainers.""",
        "optimized_code": """// Pure Domain Entity: Zero framework annotations
public class Payment {
    private final PaymentId id;
    private final Money amount;
    private PaymentStatus status;

    public void authorize() {
        if (!amount.isPositive()) throw new InvalidPaymentException("Amount must be positive");
        this.status = PaymentStatus.AUTHORIZED;
    }
}

// Driven Port (Output Interface owned by Domain)
public interface PaymentRepositoryPort {
    void save(Payment payment);
    Optional<Payment> findById(PaymentId id);
}""",
        "junior_eval": "Believes Hexagonal Architecture is just creating an interface for every service class or couples domain entities to JPA annotations.",
        "expert_eval": "Enforces the Dependency Inversion Rule (dependencies point strictly inwards), structures Driving vs Driven Ports, and achieves sub-second domain test suites completely decoupled from Spring/JPA."
    })

    # Q20: Multi-Datacenter High Availability & Chaos Engineering
    questions.append({
        "id": 20,
        "badge": "Resilience Engineering & Chaos Testing",
        "keywords": "chaos engineering netflix chaos monkey multi datacenter active active failover blast radius",
        "concept": "Multi-datacenter enterprise high availability, automated failover verification, <strong>Chaos Engineering</strong> (Netflix Chaos Monkey / Chaos Mesh), and game days.",
        "question": """A global payment processing network requires 99.999% availability (less than 5 minutes of total downtime per year) across multi-region datacenters. Look at the architecture.
<br><br>
<strong>Part A:</strong> An enterprise spends $5 million building an automated cross-datacenter failover system. When a catastrophic power outage strikes Data Center 1, the automated failover script fails completely due to stale DNS configurations and dead service credentials. Why do <strong>untested disaster recovery systems always fail in real disasters</strong>?
<br>
<strong>Part B:</strong> What are the foundational principles of <strong>Chaos Engineering</strong>? How does continuously injecting controlled failures into production (e.g. killing random pods, simulating latency, partitioning network links) build system resilience?
<br>
<strong>Part C:</strong> How do you design a safe Chaos Engineering experiment with a <strong>strictly bounded Blast Radius</strong> to prevent customer-facing outages during testing?""",
        "snippet_title": "ChaosExperiment.json",
        "snippet_code": """{
  "name": "DatacenterNetworkLatencyExperiment",
  "target": "payment-microservice",
  "fault": {
    "type": "NetworkLatency",
    "delayMs": 5000,
    "jitterMs": 500
  },
  "hypothesis": "Circuit breakers trip to OPEN within 3 seconds and fallback to cache with 0 customer errors"
}""",
        "rating_concept": "Chaos Engineering principles, bounded blast radius, and automated failover verification",
        "solution": """<strong>Part A (The Untested Disaster Recovery Paradox):</strong>
<br>• Disaster recovery systems are rarely executed during normal operations.
<br>• Over months, configuration drift, rotated secrets, network topology changes, and stale DNS caches accumulate unnoticed.
<br>• When a real emergency occurs, the failover pipeline is tested for the first time in high-stress conditions and almost always collapses.
<br>• The only way to guarantee a failover system works is to <strong>execute it continuously as standard operating procedure</strong>.
<br><br>
<strong>Part B (Principles of Chaos Engineering):</strong>
<br>1. <strong>Formulate a Steady-State Hypothesis:</strong> Define normal business metrics (e.g. payment success rate = 99.98%, p99 latency < 50ms).
<br>2. <strong>Simulate Real-World Turbulence:</strong> Inject realistic hardware crashes, network latency spikes, disk fill-ups, or region loss.
<br>3. <strong>Disprove the Hypothesis:</strong> If business metrics drop below steady-state, you have discovered a latent systemic vulnerability <em>before</em> it causes a real production outage.
<br><br>
<strong>Part C (Bounding the Blast Radius):</strong>
<br>• Start small: Run experiments in staging first, then canaried in production on 1% of internal synthetic test traffic.
<br>• Implement <strong>Automated Stop-Loss Kill Switches</strong>: If production error rates breach 0.1%, the chaos experiment halts instantly and rolls back in milliseconds.""",
        "optimized_code": """// Automated Chaos Experiment with Emergency Stop-Loss Kill Switch
public void runControlledChaosExperiment(ChaosFault fault, MetricsMonitor monitor) {
    try {
        fault.inject();
        boolean steadyState = monitor.verifySteadyState(Duration.ofSeconds(30));
        if (!steadyState) {
            log.error("Steady-state hypothesis disproven! Emergency rollback triggered.");
            fault.emergencyRollback();
        }
    } finally {
        fault.cleanup();
    }
}""",
        "junior_eval": "Believes chaos engineering means arbitrarily crashing production servers at random without hypothesis, monitoring, or kill-switches.",
        "expert_eval": "Articulates Chaos Engineering steady-state hypotheses, establishes automated kill-switch stop-loss mechanisms, and designs continuous failover drills to eliminate configuration drift."
    })

    return questions

def generate_architecture_html():
    from create_architecture_page import html_header, html_footer
    questions = get_architecture_questions()

    cards_html = []

    for q in questions:
        q_id = q["id"]
        keywords = html.escape(q["keywords"])
        badge = html.escape(q["badge"])
        concept = q["concept"]
        question_text = q["question"]
        snippet_title = html.escape(q["snippet_title"])
        
        # Clean snippet code programmatically to ensure ZERO comments in candidate snippets
        clean_lines = []
        for line in q["snippet_code"].split("\n"):
            # strip single-line comments (// or #) if not part of http://
            if "//" in line and "http://" not in line and "https://" not in line:
                idx = line.find("//")
                line = line[:idx].rstrip()
            if "#" in line and not line.strip().startswith("#!"):
                idx = line.find("#")
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
                                <button class="star-btn" data-rating="1" onclick="setQuestionRating('architecture', {q_id}, 1, '{rating_concept_escaped}')">
                                    <span class="star-num">1</span>
                                    <span class="star-label">Cannot Explain</span>
                                </button>
                                <button class="star-btn" data-rating="2" onclick="setQuestionRating('architecture', {q_id}, 2, '{rating_concept_escaped}')">
                                    <span class="star-num">2</span>
                                    <span class="star-label">Partial</span>
                                </button>
                                <button class="star-btn" data-rating="3" onclick="setQuestionRating('architecture', {q_id}, 3, '{rating_concept_escaped}')">
                                    <span class="star-num">3</span>
                                    <span class="star-label">Good</span>
                                </button>
                                <button class="star-btn" data-rating="4" onclick="setQuestionRating('architecture', {q_id}, 4, '{rating_concept_escaped}')">
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

    out_path = "/Users/barvepan/Pandharinath/Developer/Workspace/interview-questions/architecture-design.html"
    with open(out_path, "w") as f:
        f.write(full_html)
    print(f"Generated {out_path} with {len(questions)} questions successfully!")

if __name__ == "__main__":
    generate_architecture_html()

