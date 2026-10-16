import os
import html

def get_aws_questions():
    questions = []

    # Q1: VPC CIDR Blocks & Reserved IP Calculations
    questions.append({
        "id": 1,
        "badge": "VPC & IP Address Management",
        "keywords": "vpc cidr block reserved ip subnet 16 28 ip exhaustion autoscaling",
        "concept": "AWS VPC CIDR block constraints (/16 to /28), subnet allocation mathematics, the 5 AWS-reserved IP addresses per subnet, and preventing IP exhaustion under autoscaling.",
        "question": """A cloud engineering team provisions a dedicated microservices subnet using Terraform with a <code>/28</code> CIDR block. Look at the code snippet.
<br><br>
<strong>Part A:</strong> How many total IPv4 addresses exist in a <code>/28</code> subnet, and exactly how many are usable by EC2 instances, Lambda ENIs, or containers? List the 5 addresses reserved by AWS and their dedicated networking purposes.
<br>
<strong>Part B:</strong> During a traffic surge, the Auto Scaling Group fails to launch new instances, and Lambda functions in the VPC fail with <code>EC2ThrottledException</code>. Explain why a <code>/28</code> block is an anti-pattern for production microservices.
<br>
<strong>Part C:</strong> Can an existing VPC CIDR block be modified or expanded after creation? How does AWS Secondary CIDR allocation solve IP exhaustion without tearing down the VPC?""",
        "snippet_title": "vpc-subnet.tf",
        "snippet_code": """resource "aws_vpc" "app_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
}

resource "aws_subnet" "service_subnet_az1" {
  vpc_id            = aws_vpc.app_vpc.id
  cidr_block        = "10.0.1.0/28"
  availability_zone = "us-east-1a"
}""",
        "rating_concept": "VPC CIDR calculation, 5 AWS reserved IPs, and secondary CIDR scaling",
        "solution": """<strong>Part A (The Math of IPv4 Subnets & The 5 Reserved Addresses):</strong>
<br>A <code>/28</code> subnet has $2^{(32 - 28)} = 2^4 = 16$ total IPv4 addresses.
<br>However, AWS reserves exactly <strong>5 IP addresses</strong> in every subnet:
<br>1. <code>10.0.1.0</code>: Network address (first address).
<br>2. <code>10.0.1.1</code>: Reserved by AWS for the VPC default router.
<br>3. <code>10.0.1.2</code>: Reserved by AWS for the DNS resolver (AmazonProvidedDNS).
<br>4. <code>10.0.1.3</code>: Reserved by AWS for future internal use.
<br>5. <code>10.0.1.15</code>: Network broadcast address (AWS does not support broadcast, but reserves it).
<br>Usable IPs: $16 - 5 =$ <strong>only 11 usable IP addresses!</strong>
<br><br>
<strong>Part B (Why /28 Causes Outages Under Autoscaling):</strong>
<br>Each EC2 instance, Application Load Balancer ENI node, RDS endpoint, and Lambda VPC ENI consumes private IP addresses from the subnet.
<br>With only 11 usable IPs, if 2 ALBs and 5 EC2 instances are active, only 4 IPs remain. Any sudden spike in auto-scaling or rolling deployments triggers immediate <code>IP exhaustion</code>, preventing new pods/instances from launching.
<br><br>
<strong>Part C (Secondary CIDR Blocks):</strong>
<br>While you cannot alter an existing subnet's CIDR boundaries in place, AWS allows you to associate <strong>Secondary CIDR blocks</strong> (e.g. <code>100.64.0.0/16</code> carrier-grade NAT or additional <code>10.1.0.0/16</code>) to an existing VPC. You can then provision fresh, larger subnets (e.g. <code>/22</code> with 1,019 usable IPs) without rebuilding the VPC.""",
        "optimized_code": """resource "aws_subnet" "service_subnet_az1" {
  vpc_id            = aws_vpc.app_vpc.id
  cidr_block        = "10.0.4.0/22" # 1,024 IPs (1,019 usable)
  availability_zone = "us-east-1a"

  tags = {
    Name = "prod-microservices-az1"
    Tier = "Private"
  }
}""",
        "junior_eval": "Calculates 16 usable IPs (forgetting standard broadcast/network rules and unaware of AWS's 5 reserved addresses) and does not realize ALBs and Lambdas consume subnet IPs.",
        "expert_eval": "Accurately lists the 5 AWS reserved addresses by offset, identifies the IP exhaustion bottleneck for ALBs and rolling deployments, and designs properly sized /20-/22 subnets with secondary CIDRs."
    })

    # Q2: Public Subnets, Private Subnets & NAT Gateway
    questions.append({
        "id": 2,
        "badge": "VPC Routing & Egress Architecture",
        "keywords": "public subnet private subnet nat gateway internet gateway route table single az multi az",
        "concept": "Multi-tier VPC network topology, Public vs Private subnets, Route Table associations, Internet Gateways (IGW), NAT Gateways vs NAT Instances, and Multi-AZ high availability.",
        "question": """A private microservice running on EC2 needs to call an external third-party payment gateway over HTTPS. Look at the Terraform snippet.
<br><br>
<strong>Part A:</strong> EC2 instances in <code>app_private_subnet</code> cannot connect to the payment gateway; all outbound HTTPS requests time out. Explain the routing flaw in the route table configuration.
<br>
<strong>Part B:</strong> Compare a managed <strong>AWS NAT Gateway</strong> versus a self-managed <strong>NAT Instance</strong> across throughput scaling, high availability, patching overhead, and security groups.
<br>
<strong>Part C:</strong> If you deploy a single NAT Gateway in Availability Zone A, and an EC2 instance in Availability Zone B routes outbound traffic through it, what are the two major architectural liabilities (Availability & Cost)?""",
        "snippet_title": "vpc-routing.tf",
        "snippet_code": """resource "aws_route_table" "private_rt" {
  vpc_id = aws_vpc.app_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_gw.id
  }
}

resource "aws_nat_gateway" "nat_gw" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.app_private_subnet.id
}""",
        "rating_concept": "Public/Private subnets, NAT Gateway placement, route table configuration, and multi-AZ egress",
        "solution": """<strong>Part A (The Circular Routing Deadlock):</strong>
<br>In the Terraform snippet, <code>aws_nat_gateway.nat_gw</code> is deployed inside <code>aws_subnet.app_private_subnet</code>.
<br>• A NAT Gateway <strong>must always be located inside a PUBLIC subnet</strong> that has a direct route to an Internet Gateway (<code>igw</code>).
<br>• Because the NAT Gateway itself is in a private subnet with no path to the Internet, outbound packets loop into the NAT Gateway and die, causing immediate connection timeouts.
<br><br>
<strong>Part B (NAT Gateway vs NAT Instance):</strong>
<br>• <strong>NAT Gateway (AWS Managed):</strong> Auto-scales up to 45 Gbps bandwidth, zero OS patching or maintenance, native AWS monitoring, fully managed hardware redundancy. (Cannot attach Security Groups; acts strictly on subnet routing).
<br>• <strong>NAT Instance (EC2 based):</strong> Limited by EC2 instance size and network burst limits, requires manual script/software patching, requires disabling Source/Destination checks, no automatic failover unless custom failover scripts are deployed.
<br><br>
<strong>Part C (Single NAT Gateway Cross-AZ Liabilities):</strong>
<br>1. <strong>Single Point of Failure:</strong> If Availability Zone A suffers an outage, private subnets in AZ B and AZ C completely lose all outbound internet and payment connectivity.
<br>2. <strong>Cross-AZ Data Transfer Costs:</strong> AWS charges for inter-AZ data transfer ($0.01/GB). Routing gigabytes of outbound API traffic across AZ boundaries significantly inflates cloud bills. Best practice: Deploy one NAT Gateway per Availability Zone.""",
        "optimized_code": """resource "aws_nat_gateway" "nat_az1" {
  allocation_id = aws_eip.nat_az1_eip.id
  subnet_id     = aws_subnet.public_subnet_az1.id # Placed in PUBLIC subnet
  depends_on    = [aws_internet_gateway.igw]
}

resource "aws_route_table" "private_az1_rt" {
  vpc_id = aws_vpc.app_vpc.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_az1.id
  }
}""",
        "junior_eval": "Places the NAT Gateway in the private subnet or recommends attaching an Internet Gateway directly to the private subnet (destroying network isolation).",
        "expert_eval": "Diagnoses the public subnet requirement for NAT Gateways, articulates multi-AZ redundancy to avoid cross-AZ egress costs and single-point-of-failure risks, and utilizes VPC Endpoints for S3/DynamoDB."
    })

    # Q3: Security Groups vs Network ACLs
    questions.append({
        "id": 3,
        "badge": "Network Security & Defense-in-Depth",
        "keywords": "security group nacl stateful stateless ephemeral ports 1024 65535 defense in depth",
        "concept": "Security Groups (stateful, instance-level) versus Network Access Control Lists (NACLs - stateless, subnet-level), rule evaluation order, and ephemeral port requirements.",
        "question": """A security engineer locks down a VPC subnet by modifying its Network ACL (NACL). Look at the Terraform configuration.
<br><br>
<strong>Part A:</strong> Inbound HTTPS traffic (port 443) is explicitly permitted in the NACL, but external clients connecting to the web servers report total connection timeouts. Why does this happen in a stateless NACL?
<br>
<strong>Part B:</strong> What are <strong>ephemeral ports</strong>, what range do they occupy on Linux/AWS systems, and how must outbound NACL rules be configured to allow return traffic?
<br>
<strong>Part C:</strong> Contrast the fundamental security and architectural differences between <strong>Security Groups</strong> and <strong>Network ACLs</strong> across state tracking, scope, and rule evaluation.""",
        "snippet_title": "nacl-rules.tf",
        "snippet_code": """resource "aws_network_acl_rule" "inbound_https" {
  network_acl_id = aws_network_acl.web_nacl.id
  rule_number    = 100
  egress         = false
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = 443
  to_port        = 443
}

resource "aws_network_acl_rule" "outbound_default" {
  network_acl_id = aws_network_acl.web_nacl.id
  rule_number    = 100
  egress         = true
  rule_action    = "deny"
  cidr_block     = "0.0.0.0/0"
  protocol       = "-1"
}""",
        "rating_concept": "Security Groups vs NACLs, stateful connection tracking, and ephemeral port ranges",
        "solution": """<strong>Part A (Stateless NACLs & Blocked Response Packets):</strong>
<br>• Network ACLs are <strong>strictly stateless</strong>: they do not remember active inbound connections.
<br>• When a client initiates an HTTPS handshake on port 443, the inbound packet is allowed by Rule 100.
<br>• However, the web server's TCP ACK / response packet must be sent back to the client's temporary source port (an ephemeral port).
<br>• Because the outbound NACL rule is configured to <strong>DENY all traffic</strong> (Rule 100 egress deny), the server's response packet is silently dropped at the subnet boundary. The client times out.
<br><br>
<strong>Part B (Ephemeral Ports Specification):</strong>
<br>When a client opens an outbound TCP socket to port 443, the client operating system selects an arbitrary high-numbered port from the <strong>ephemeral port range</strong>:
<br>• Linux kernels / AWS NAT Gateways: <code>1024 - 65535</code> (or <code>32768 - 60999</code>).
<br>To allow return traffic in a stateless NACL, you must configure an outbound rule allowing TCP traffic to destination ports <code>1024 - 65535</code> for <code>0.0.0.0/0</code>.
<br><br>
<strong>Part C (Security Groups vs NACLs Comparison Matrix):</strong>
<br>• <strong>State:</strong> Security Groups are <em>stateful</em> (if inbound is allowed, outbound return traffic is automatically allowed regardless of outbound rules). NACLs are <em>stateless</em>.
<br>• <strong>Scope:</strong> SGs apply at the Elastic Network Interface (ENI / instance) level; NACLs apply at the subnet boundary.
<br>• <strong>Rules:</strong> SGs only support <em>allow</em> rules; NACLs support both <em>allow</em> and <em>deny</em> rules evaluated in numerical order.""",
        "optimized_code": """resource "aws_network_acl_rule" "outbound_ephemeral" {
  network_acl_id = aws_network_acl.web_nacl.id
  rule_number    = 100
  egress         = true
  protocol       = "tcp"
  rule_action    = "allow"
  cidr_block     = "0.0.0.0/0"
  from_port      = 1024
  to_port        = 65535
}""",
        "junior_eval": "Thinks Security Groups and NACLs are identical firewalls or cannot explain why response packets require an explicit outbound rule in a NACL.",
        "expert_eval": "Articulates the stateful vs stateless tracking mechanisms, identifies the client ephemeral port return path, and designs layered defense-in-depth using both SGs and NACLs."
    })

    # Q4: S3 Storage Classes, Lifecycle Rules & Multipart Cleanup
    questions.append({
        "id": 4,
        "badge": "Object Storage & Cost Optimization",
        "keywords": "s3 storage classes lifecycle policy multipart upload abort glacier intelligent tiering",
        "concept": "Amazon S3 storage tiering (Standard, Intelligent-Tiering, Glacier Flexible, Glacier Deep Archive), lifecycle transition rules, and preventing orphan multipart upload billing.",
        "question": """An enterprise uploads large PDF invoices and media assets to Amazon S3. Over time, monthly storage costs surge to $12,000/month despite only 2 TB of active files visible in the S3 console. Look at the configuration snippet.
<br><br>
<strong>Part A:</strong> Thousands of multi-gigabyte uploads failed halfway due to client disconnections. Why are these failed uploads continuing to be billed indefinitely, and why are they invisible in standard S3 bucket object listings?
<br>
<strong>Part B:</strong> What S3 Lifecycle rule must be configured to automatically purge failed multipart uploads and recover storage costs?
<br>
<strong>Part C:</strong> Compare <strong>S3 Intelligent-Tiering</strong> against manually managed lifecycle transition rules (Standard &rarr; Standard-IA &rarr; Glacier Deep Archive). Under what file size and access patterns does Intelligent-Tiering become uneconomical?""",
        "snippet_title": "s3-bucket-lifecycle.tf",
        "snippet_code": """resource "aws_s3_bucket" "invoice_bucket" {
  bucket = "enterprise-customer-invoices"
}

resource "aws_s3_bucket_lifecycle_configuration" "invoice_lifecycle" {
  bucket = aws_s3_bucket.invoice_bucket.id

  rule {
    id     = "archive-old-invoices"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}""",
        "rating_concept": "S3 storage classes, abort incomplete multipart uploads, and lifecycle cost optimization",
        "solution": """<strong>Part A (The Invisible Multipart Upload Leak):</strong>
<br>• When uploading files > 100MB via the S3 Multipart Upload API, S3 splits the payload into multiple parts.
<br>• If an upload aborts or disconnects, the uploaded parts remain stored in S3 <strong>indefinitely</strong>.
<br>• These orphan parts <strong>do not appear</strong> as objects in standard <code>s3:ListObjectsV2</code> API calls or console views, but AWS bills them at standard S3 storage rates ($0.023/GB/month). Over months, orphaned multi-part chunks accumulate terabytes of zombie data.
<br><br>
<strong>Part B (AbortIncompleteMultipartUpload Lifecycle Rule):</strong>
<br>Configure an explicit lifecycle rule using <code>abort_incomplete_multipart_upload</code> specifying <code>days_after_initiation = 7</code>.
<br>S3 will automatically delete any initiated multipart upload parts that fail to finalize within 7 days, reclaiming 100% of the leaked storage.
<br><br>
<strong>Part C (S3 Intelligent-Tiering Trade-offs):</strong>
<br>• <strong>Pros:</strong> Automatically moves objects between Frequent, Infrequent (30 days), and Archive Instant (90 days) tiers without retrieval fees or transition penalties.
<br>• <strong>Liabilities:</strong>
<br>1. <em>Monitoring Fee:</em> AWS charges a monthly per-object monitoring fee ($0.0025 per 1,000 objects).
<br>2. <em>Small Object Overhead:</em> Objects < 128KB are never transitioned to infrequent tiers and incur the monitoring fee, making Intelligent-Tiering uneconomical for buckets with millions of tiny thumbnail or JSON files.""",
        "optimized_code": """resource "aws_s3_bucket_lifecycle_configuration" "invoice_lifecycle" {
  bucket = aws_s3_bucket.invoice_bucket.id

  rule {
    id     = "cleanup-incomplete-uploads"
    status = "Enabled"

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }

    transition {
      days          = 90
      storage_class = "INTELLIGENT_TIERING"
    }
  }
}""",
        "junior_eval": "Blames bucket versioning or assumes failed uploads are automatically refunded and deleted by AWS.",
        "expert_eval": "Identifies the orphan multipart upload billing trap, writes the abort_incomplete_multipart_upload lifecycle rule, and evaluates the 128KB monitoring fee trade-offs of Intelligent-Tiering."
    })

    # Q5: Lambda Cold Starts & Java SnapStart (CRaC)
    questions.append({
        "id": 5,
        "badge": "Serverless Runtime & Performance",
        "keywords": "lambda cold start java snapstart crac checkpoint restore firecracker microvm",
        "concept": "AWS Lambda JVM cold starts (2–8 seconds), Java SnapStart using Firecracker microVM snapshotting, Coordinated Restore at Checkpoint (CRaC), and snapshot state uniqueness traps.",
        "question": """A high-frequency payment microservice is deployed as an AWS Lambda function on Java 17 / 21. Look at the code snippet.
<br><br>
<strong>Part A:</strong> Without optimization, the Lambda function exhibits a 6-second cold start on scaling bursts, causing client timeouts. What are the 3 distinct phases of an AWS Lambda cold start?
<br>
<strong>Part B:</strong> How does <strong>AWS Lambda SnapStart</strong> reduce Java cold starts from 6,000ms to under 200ms using Firecracker MicroVM snapshotting and CRaC?
<br>
<strong>Part C:</strong> Look at the <code>transactionSalt</code> and database connection in the code. What critical security and networking bugs occur when this function is restored from a SnapStart snapshot without CRaC lifecycle hooks?""",
        "snippet_title": "PaymentLambdaHandler.java",
        "snippet_code": """public class PaymentLambdaHandler implements RequestHandler<PaymentEvent, PaymentResult> {

    private static final byte[] transactionSalt = new byte[32];
    private static Connection dbConnection;

    static {
        new SecureRandom().nextBytes(transactionSalt);
        dbConnection = DriverManager.getConnection("jdbc:postgresql://db.internal:5432/pay");
    }

    @Override
    public PaymentResult handleRequest(PaymentEvent event, Context context) {
        return process(event, transactionSalt, dbConnection);
    }

    private PaymentResult process(PaymentEvent e, byte[] s, Connection c) {
        return new PaymentResult("SUCCESS");
    }
}""",
        "rating_concept": "AWS Lambda Java SnapStart, CRaC checkpoint restore, and snapshot state uniqueness traps",
        "solution": """<strong>Part A (The 3 Phases of Lambda Cold Starts):</strong>
<br>1. <strong>Init Phase:</strong> Spins up Firecracker MicroVM container, initializes Java runtime, downloads deployment package, runs static initializers, loads classpath classes, and constructs handler instance (takes 80% of total cold start time: 4-6 seconds for heavy Spring Boot / Quarkus).
<br>2. <strong>Invoke Phase:</strong> Executes the <code>handleRequest()</code> handler method.
<br>3. <strong>Shutdown Phase:</strong> Terminates the runtime.
<br><br>
<strong>Part B (How SnapStart & CRaC Work):</strong>
<br>• During deployment/version publishing, AWS initializes the function, loads classes, and runs static blocks.
<br>• AWS takes a memory and disk <strong>snapshot of the running Firecracker microVM</strong> and caches it in a multi-tier cache.
<br>• When a cold start invocation occurs, AWS skips the JVM bootstrap and memory-maps the snapshot directly into RAM in <strong>sub-200ms</strong>.
<br><br>
<strong>Part C (Snapshot Uniqueness & Stale Socket Traps):</strong>
<br>1. <strong>Broken Cryptographic Uniqueness:</strong> Because <code>transactionSalt</code> is initialized in <code>static {}</code>, the exact same random bytes are baked into the snapshot. 1,000 concurrent Lambda instances will share the <strong>identical cryptographic salt</strong>!
<br>2. <strong>Dead Sockets:</strong> The TCP connection to PostgreSQL was established during snapshot creation. Upon restoration minutes later, the remote database has timed out the connection, causing <code>SocketException: Broken pipe</code> on invocations.
<br><strong>Fix:</strong> Implement CRaC <code>Resource</code> (<code>afterRestore</code>) to reseed randomness and re-establish network sockets.""",
        "optimized_code": """public class SafePaymentHandler implements RequestHandler<PaymentEvent, PaymentResult>, Resource {

    private byte[] salt;

    public SafePaymentHandler() {
        Core.getGlobalContext().register(this);
        refresh();
    }

    @Override
    public void afterRestore(org.crac.Context context) {
        refresh(); // Regenerate random salt and reconnect DB upon VM restore
    }

    private void refresh() {
        this.salt = new byte[32];
        new SecureRandom().nextBytes(this.salt);
    }

    @Override public void beforeCheckpoint(org.crac.Context context) {}
    @Override public PaymentResult handleRequest(PaymentEvent e, Context ctx) { return null; }
}""",
        "junior_eval": "Suggests increasing Lambda memory to 10GB or setting up a scheduled ping every 5 minutes (which only keeps 1 container warm, failing under scaling bursts).",
        "expert_eval": "Explains Firecracker VM snapshot restoration, diagnoses the snapshot uniqueness trap for SecureRandom, and implements CRaC Resource lifecycle hooks to refresh state upon restoration."
    })

    # Q6: Serverless Database Connection Pooling: RDS Proxy
    questions.append({
        "id": 6,
        "badge": "Serverless Data & Connection Management",
        "keywords": "rds proxy lambda connection pooling max connections database exhaustion postgresql",
        "concept": "Serverless relational database connection bottlenecks, Lambda concurrency bursts exhausting PostgreSQL/MySQL <code>max_connections</code>, and RDS Proxy connection multiplexing.",
        "question": """A serverless order processing system processes black-Friday traffic bursts using AWS Lambda and Amazon Aurora PostgreSQL. Look at the code snippet.
<br><br>
<strong>Part A:</strong> During a flash sale, Lambda concurrency surges from 10 to 1,200 instances within 15 seconds. The database crashes with <code>FATAL: remaining connection slots are reserved for non-replication superuser connections</code>. Why does standard connection pooling (HikariCP) fail in serverless architectures?
<br>
<strong>Part B:</strong> How does <strong>AWS RDS Proxy</strong> solve this problem through connection multiplexing and queuing?
<br>
<strong>Part C:</strong> What is RDS Proxy <strong>Connection Pinning</strong>? List two common Java / SQL practices that cause pinning and prevent RDS Proxy from multiplexing connections.""",
        "snippet_title": "OrderDatabaseHandler.java",
        "snippet_code": """public class OrderDatabaseHandler implements RequestHandler<OrderEvent, String> {

    private static final HikariDataSource dataSource;

    static {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:postgresql://aurora-primary.internal:5432/orders");
        config.setMaximumPoolSize(10);
        dataSource = new HikariDataSource(config);
    }

    @Override
    public String handleRequest(OrderEvent event, Context context) {
        try (Connection conn = dataSource.getConnection();
             PreparedStatement ps = conn.prepareStatement("INSERT INTO orders VALUES (?)")) {
            ps.setString(1, event.getOrderId());
            ps.executeUpdate();
            return "SAVED";
        } catch (SQLException ex) {
            throw new RuntimeException(ex);
        }
    }
}""",
        "rating_concept": "RDS Proxy connection multiplexing, serverless connection exhaustion, and pinning traps",
        "solution": """<strong>Part A (Why HikariCP Collapses in Serverless):</strong>
<br>• In standard container/EC2 deployments, a few long-lived instances share a centralized connection pool.
<br>• In AWS Lambda, each concurrent execution runs in an <strong>isolated execution environment</strong>.
<br>• If 1,200 Lambda instances spin up, each running HikariCP with <code>maximumPoolSize = 10</code>, Lambda attempts to open $1,200 \\times 10 = 12,000$ active TCP connections to PostgreSQL!
<br>• PostgreSQL allocates 5–10MB of RAM per connection and defaults to <code>max_connections = 100 - 500</code>. Memory is exhausted, database CPU spikes to 100%, and the engine crashes.
<br><br>
<strong>Part B (RDS Proxy Multiplexing Architecture):</strong>
<br>• RDS Proxy sits between Lambda and Aurora as a managed, highly available proxy layer.
<br>• Lambda functions connect to RDS Proxy via fast local VPC connections.
<br>• RDS Proxy maintains a small, fixed pool of persistent connections (e.g. 50 connections) to the Aurora database and <strong>multiplexes (borrows and returns) connections at the individual transaction level</strong>.
<br>• If thousands of Lambdas make rapid queries, RDS Proxy queues incoming requests and drains them through the healthy 50 connections without overloading the DB.
<br><br>
<strong>Part C (Connection Pinning Traps):</strong>
<br>Pinning occurs when a client session executes an operation that binds the physical database connection to that specific client until the session ends, disabling multiplexing:
<br>1. Using PostgreSQL temporary tables (e.g. <code>CREATE TEMP TABLE ...</code>).
<br>2. Changing session state / transaction isolation level without resetting (e.g. <code>SET search_path</code>, <code>SET TIME ZONE</code>).
<br>3. Prepared statements that are not closed or formatted for proxy caching.""",
        "optimized_code": """// Connect to RDS Proxy Endpoint instead of Direct Cluster
String rdsProxyUrl = "jdbc:postgresql://orders-proxy.proxy-xxxx.us-east-1.rds.amazonaws.com:5432/orders";

HikariConfig config = new HikariConfig();
config.setJdbcUrl(rdsProxyUrl);
config.setMaximumPoolSize(1); // Set pool size to 1 in Lambda when using RDS Proxy
config.setInitializationFailTimeout(0);""",
        "junior_eval": "Suggests increasing PostgreSQL max_connections to 20,000 (which will cause the database to crash with OutOfMemory on startup).",
        "expert_eval": "Explains why shared pools fail across isolated Lambda containers, implements RDS Proxy connection multiplexing, sets Lambda pool size to 1, and avoids connection pinning traps."
    })

    # Q7: EC2 Auto Scaling Policies: Target Tracking vs Step Scaling
    questions.append({
        "id": 7,
        "badge": "Compute Scaling & Elasticity",
        "keywords": "ec2 auto scaling target tracking step scaling cooldown thrashing warm up",
        "concept": "EC2 Auto Scaling Groups (ASG), Target Tracking Scaling Policies vs Step Scaling, instance warmup periods, default cooldowns, and preventing scaling thrashing (flapping).",
        "question": """An e-commerce backend running on EC2 instances experiences massive traffic fluctuations. Look at the CloudFormation / Terraform snippet.
<br><br>
<strong>Part A:</strong> The Auto Scaling Group is configured with a Simple Scaling policy based on CPU utilization > 70% with a 0-second cooldown. When traffic spikes, the cluster scales from 4 to 40 instances, and then 3 minutes later scales down to 4 instances, repeating in a continuous loop. What is this phenomenon called, and what causes it?
<br>
<strong>Part B:</strong> Compare <strong>Target Tracking Scaling Policies</strong> against <strong>Step Scaling Policies</strong>. Which is preferred for tracking an ALB metric like <code>ALBRequestCountPerTarget</code>?
<br>
<strong>Part C:</strong> What is the purpose of the <strong>Instance Warmup Period</strong>, and how does it prevent premature over-provisioning while newly launched Java Spring Boot instances are booting?""",
        "snippet_title": "asg-policy.tf",
        "snippet_code": """resource "aws_autoscaling_policy" "flapping_cpu_policy" {
  name                   = "cpu-simple-policy"
  scaling_adjustment     = 5
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 0
  autoscaling_group_name = aws_autoscaling_group.app_asg.name
}

resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "cpu-utilization-high"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Average"
  threshold           = 70
  alarm_actions       = [aws_autoscaling_policy.flapping_cpu_policy.arn]
}""",
        "rating_concept": "EC2 Auto Scaling, Target Tracking vs Step Scaling, cooldowns, and scaling flapping prevention",
        "solution": """<strong>Part A (Scaling Thrashing / Flapping):</strong>
<br>This phenomenon is called <strong>Scaling Flapping (Thrashing)</strong>:
<br>• When CPU reaches 70%, the alarm fires and triggers the policy to add 5 instances.
<br>• Because <code>cooldown = 0</code>, the alarm evaluates again on the next 60s period before newly added instances have finished booting and taking load.
<br>• The alarm triggers again and again, scaling capacity up to 40 instances.
<br>• Once all 40 instances boot, aggregate CPU utilization plummets to 5%, triggering an immediate aggressive scale-down back to 4 instances.
<br>• The cycle repeats infinitely, destabilizing the application and driving up EC2 compute costs.
<br><br>
<strong>Part B (Target Tracking vs Step Scaling):</strong>
<br>• <strong>Target Tracking:</strong> Works like a home thermostat. You specify the target value (e.g. <code>ALBRequestCountPerTarget = 1000</code> or <code>CPU = 60%</code>). AWS automatically adds or removes capacity proportional to the deviation. It is the gold standard for ALB request metrics.
<br>• <strong>Step Scaling:</strong> Applies varying adjustments based on the size of the breach (e.g. +10% if CPU 70-80%, +30% if CPU > 85%).
<br><br>
<strong>Part C (Instance Warmup Period):</strong>
<br>A Java Spring Boot application can take 60–120 seconds to boot the JVM, warm up JIT, and pass health checks.
<br>The <strong>Instance Warmup Period</strong> tells the ASG to ignore newly launched instances in metric calculations until the warmup period expires, preventing premature extra scaling actions.""",
        "optimized_code": """resource "aws_autoscaling_policy" "target_tracking_alb" {
  name                   = "alb-requests-target-tracking"
  policy_type            = "TargetTrackingScaling"
  autoscaling_group_name = aws_autoscaling_group.app_asg.name
  estimated_instance_warmup = 180 # 3 minutes for Java JVM boot

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.app_alb.arn_suffix}/${aws_lb_target_group.app_tg.arn_suffix}"
    }
    target_value = 1200.0
  }
}""",
        "junior_eval": "Configures simple scaling with 0 cooldown or recommends turning off autoscaling and statically provisioning 50 EC2 instances permanently.",
        "expert_eval": "Diagnoses scaling thrashing/flapping, explains Target Tracking mathematical proportionality, and configures estimated_instance_warmup for JVM startup times."
    })

    # Q8: Application Load Balancer: Routing & Connection Draining
    questions.append({
        "id": 8,
        "badge": "Load Balancing & Traffic Management",
        "keywords": "alb nlb target group connection draining deregistration delay health checks 502",
        "concept": "Application Load Balancer (ALB) Layer 7 routing, Target Groups, Connection Draining (Deregistration Delay), health check tuning, and zero-downtime rolling deployments.",
        "question": """An e-commerce API runs behind an Application Load Balancer. Look at the Target Group configuration snippet.
<br><br>
<strong>Part A:</strong> During rolling deployments, users encounter intermittent <code>HTTP 502 Bad Gateway</code> errors for 15–30 seconds. Explain how an improperly configured <strong>Deregistration Delay (Connection Draining)</strong> causes in-flight requests to be severed.
<br>
<strong>Part B:</strong> What happens if the health check interval is 30 seconds with <code>HealthyThreshold = 5</code>, and an instance takes 45 seconds to boot its Spring context?
<br>
<strong>Part C:</strong> Compare an <strong>Application Load Balancer (ALB)</strong> against a <strong>Network Load Balancer (NLB)</strong>. When is an NLB strictly required over an ALB?""",
        "snippet_title": "alb-target-group.tf",
        "snippet_code": """resource "aws_lb_target_group" "api_tg" {
  name                 = "api-production-tg"
  port                 = 8080
  protocol             = "HTTP"
  vpc_id               = aws_vpc.app_vpc.id
  deregistration_delay = 0

  health_check {
    path                = "/actuator/health"
    protocol            = "HTTP"
    interval            = 5
    timeout             = 2
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}""",
        "rating_concept": "ALB connection draining, health check thresholds, and ALB vs NLB trade-offs",
        "solution": """<strong>Part A (Deregistration Delay & The 502 Drop):</strong>
<br>• When an instance is terminated by autoscaling or a deployment script, the ALB sets its state to <code>draining</code>.
<br>• In the configuration snippet, <code>deregistration_delay = 0</code>.
<br>• Setting delay to 0 causes the ALB to <strong>immediately sever active in-flight TCP connections</strong> and send TCP RST packets while requests are still being processed.
<br>• The ALB immediately returns <strong>HTTP 502 Bad Gateway</strong> to clients.
<br><strong>Fix:</strong> Configure <code>deregistration_delay</code> to 30–60 seconds, allowing active requests to finish while stopping new traffic.
<br><br>
<strong>Part B (Health Check Lag on Boot):</strong>
<br>If <code>HealthyThreshold = 5</code> with an interval of 30 seconds, an instance requires $5 \\times 30 = 150$ seconds (2.5 minutes) of consecutive passes before the ALB marks it healthy.
<br>If deployment scripts wait only 60 seconds before killing the old instance, the old instance is terminated while the new instance is still warming up &mdash; leaving <strong>zero healthy targets</strong> in the target group!
<br><br>
<strong>Part C (ALB vs NLB Selection):</strong>
<br>• <strong>ALB (Layer 7):</strong> Content-based routing (HTTP path, headers, query params), TLS termination, WebSocket support.
<br>• <strong>NLB (Layer 4):</strong> Extreme performance (millions of RPS with microsecond latency), static / Elastic IP addresses per subnet, TCP/UDP pass-through, and private link integration.""",
        "optimized_code": """resource "aws_lb_target_group" "api_tg" {
  name                 = "api-production-tg"
  port                 = 8080
  protocol             = "HTTP"
  vpc_id               = aws_vpc.app_vpc.id
  deregistration_delay = 30 # Grace period for in-flight requests

  health_check {
    path                = "/actuator/health"
    interval            = 10
    timeout             = 4
    healthy_threshold   = 2 # Fast promotion to healthy
    unhealthy_threshold = 3
  }
}""",
        "junior_eval": "Blames Spring Boot or Tomcat for the 502 errors, unaware of the ALB connection draining deregistration delay setting.",
        "expert_eval": "Tunes deregistration delay to match p99 API latencies, calculates health check propagation math, and articulates L4 vs L7 architectural selection criteria."
    })

    # Q9: IAM Least Privilege, Instance Profiles & Role Assumption
    questions.append({
        "id": 9,
        "badge": "Cloud Security & Identity Governance",
        "keywords": "iam least privilege instance profile assume role sts imdsv2 credentials blast radius",
        "concept": "IAM security governance, eliminating static credentials, EC2 Instance Profiles, AWS STS <code>AssumeRole</code>, IMDSv2 protection against SSRF, and Permission Boundaries.",
        "question": """A developer connects an EC2 backend to Amazon S3 and Amazon SQS. Look at the application configuration snippet.
<br><br>
<strong>Part A:</strong> Why is hardcoding AWS Access Keys in <code>application.properties</code> or environment variables considered a catastrophic cloud security vulnerability?
<br>
<strong>Part B:</strong> How do <strong>EC2 Instance Profiles</strong> and IAM Roles work mechanically to provide temporary, automatically rotated credentials via the Instance Metadata Service (IMDS)?
<br>
<strong>Part C:</strong> What is an <strong>SSRF (Server-Side Request Forgery)</strong> attack against IMDSv1, and how does <strong>IMDSv2</strong> use session-oriented tokens (<code>X-aws-ec2-metadata-token</code>) with hop-limit enforcement to defeat it?""",
        "snippet_title": "application.properties",
        "snippet_code": """# Insecure Anti-Pattern in Production
cloud.aws.credentials.access-key=AKIAIOSFODNN7EXAMPLE
cloud.aws.credentials.secret-key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
cloud.aws.region.static=us-east-1
cloud.aws.s3.bucket=company-finance-documents""",
        "rating_concept": "IAM Instance Profiles, STS temporary credentials, and IMDSv2 SSRF mitigation",
        "solution": """<strong>Part A (The Danger of Static Access Keys):</strong>
<br>• Static keys (<code>AKIA...</code>) never expire unless manually rotated.
<br>• They frequently leak into git repositories, container images, build logs, and third-party APM tools.
<br>• If compromised, attackers obtain permanent remote access to company infrastructure from anywhere in the world until keys are manually deleted.
<br><br>
<strong>Part B (EC2 Instance Profile & STS Rotation):</strong>
<br>• An IAM Role with specific least-privilege permissions is attached to an EC2 <strong>Instance Profile</strong>.
<br>• The AWS SDK automatically requests short-lived temporary security credentials from the local <strong>Instance Metadata Service (IMDS)</strong> at <code>http://169.254.169.254/latest/meta-data/iam/security-credentials/</code>.
<br>• AWS Security Token Service (STS) issues credentials valid for only 6 hours and rotates them automatically without application interruption.
<br><br>
<strong>Part C (IMDSv1 SSRF Vulnerability vs IMDSv2 Protection):</strong>
<br>• <strong>IMDSv1 Flaw:</strong> Any SSRF vulnerability in the web application (e.g. <code>/preview?url=http://169.254.169.254/...</code>) allowed an attacker to make a simple HTTP GET request to read the EC2 instance role credentials.
<br>• <strong>IMDSv2 Defense:</strong> Requires a <code>PUT</code> request with header <code>X-aws-ec2-metadata-token-ttl-seconds: 21600</code> to obtain a secret session token, and sets the IP packet <strong>TTL / hop limit to 1</strong> so container proxies or forwarded requests cannot escape the local OS.""",
        "optimized_code": """resource "aws_iam_role" "app_role" {
  name = "prod-invoice-processor-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_instance" "app_server" {
  ami                  = "ami-0c55b159cbfafe1f0"
  instance_type        = "t3.medium"
  iam_instance_profile = aws_iam_instance_profile.app_profile.name

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required" # Enforce IMDSv2
    http_put_response_hop_limit = 1
  }
}""",
        "junior_eval": "Suggests storing access keys in Kubernetes secrets or environment variables, unaware of EC2 Instance Profiles or IMDSv2 security protections.",
        "expert_eval": "Eliminates static credentials completely, explains STS temporary credential rotation, and enforces IMDSv2 token headers with hop-limit 1 against SSRF exploits."
    })

    # Q10: Amazon SQS: FIFO vs Standard Queues
    questions.append({
        "id": 10,
        "badge": "Asynchronous Messaging & Queueing",
        "keywords": "sqs fifo standard deduplication message group id throughput order processing",
        "concept": "Amazon SQS Standard (unlimited throughput, at-least-once) vs SQS FIFO (exactly-once processing, ordering, 300 msg/s ceiling), <code>MessageGroupId</code> partitioning, and deduplication IDs.",
        "question": """A financial transactions microservice processes trade executions via Amazon SQS. Look at the code snippet.
<br><br>
<strong>Part A:</strong> The team implements an SQS FIFO queue with <code>MessageGroupId = "TRADES"</code> hardcoded for all messages. In production, throughput peaks at 300 messages/sec and massive backlogs form. Why did this bottleneck occur?
<br>
<strong>Part B:</strong> How does SQS FIFO use <strong>Message Group ID</strong> to achieve high parallel throughput while still guaranteeing strict order preservation for individual accounts?
<br>
<strong>Part C:</strong> What is the difference between content-based deduplication (SHA-256 hash) and passing an explicit <code>MessageDeduplicationId</code>? What is the duration of the SQS deduplication window?""",
        "snippet_title": "TradeProducerService.java",
        "snippet_code": """@Service
public class TradeProducerService {

    @Autowired
    private SqsTemplate sqsTemplate;

    public void publishTrade(TradeExecution trade) {
        // Bottleneck: Single global MessageGroupId across all trades
        SendMessageRequest request = SendMessageRequest.builder()
            .queueUrl("https://sqs.us-east-1.amazonaws.com/12345/trades.fifo")
            .messageBody(JsonUtil.toJson(trade))
            .messageGroupId("TRADES")
            .messageDeduplicationId(trade.getTradeId())
            .build();

        sqsTemplate.send(request);
    }
}""",
        "rating_concept": "SQS FIFO vs Standard, MessageGroupId partitioning, and deduplication windows",
        "solution": """<strong>Part A (The Single Message Group Bottleneck):</strong>
<br>• SQS FIFO guarantees strict sequential processing <strong>per Message Group ID</strong>.
<br>• A single message group can only be processed by one consumer thread at a time to preserve order.
<br>• SQS FIFO has a hard throughput limit of <strong>300 transactions/second</strong> (or 3,000 with batching) per message group.
<br>• By hardcoding <code>messageGroupId("TRADES")</code>, all trades across all global customers are serialized into a single queue channel. Only one consumer can process at a time, throttling the entire platform.
<br><br>
<strong>Part B (Partitioning via Dynamic MessageGroupId):</strong>
<br>• Instead of a global constant, partition by the logical entity that requires strict ordering (e.g. <code>trade.getAccountId()</code> or <code>trade.getPortfolioId()</code>).
<br>• Different accounts execute concurrently across hundreds of consumer threads in parallel.
<br>• Trades within Account 101 are guaranteed strictly in order; trades for Account 202 process in parallel with zero contention.
<br><br>
<strong>Part C (Deduplication Mechanics & 5-Minute Window):</strong>
<br>• SQS FIFO enforces a <strong>5-minute deduplication interval</strong>.
<br>• If a message with the same <code>MessageDeduplicationId</code> is published within 5 minutes, SQS accepts the call (returns HTTP 200) but <strong>does not deliver</strong> the duplicate message.
<br>• Explicit deduplication ID is preferred over content hashing because it allows identifying business transactions even if timestamps or metadata change.""",
        "optimized_code": """public void publishTrade(TradeExecution trade) {
    SendMessageRequest request = SendMessageRequest.builder()
        .queueUrl(tradesFifoQueueUrl)
        .messageBody(JsonUtil.toJson(trade))
        .messageGroupId("ACCOUNT-" + trade.getAccountId()) # Partition by customer
        .messageDeduplicationId(trade.getTradeId())       # Business idempotency ID
        .build();

    sqsClient.sendMessage(request);
}""",
        "junior_eval": "Assumes SQS FIFO can never scale beyond 300 msgs/sec globally or suggests switching to SQS Standard (causing out-of-order execution and financial account corruption).",
        "expert_eval": "Partitions MessageGroupId by account/tenant ID for horizontal consumer scaling, details the 5-minute deduplication window, and tunes batching to achieve 3,000+ msg/sec."
    })

    # Q11: AWS Secrets Manager vs Parameter Store
    questions.append({
        "id": 11,
        "badge": "Secrets Management & Rotation",
        "keywords": "secrets manager parameter store ssm rotation lambda rate limit throttling caching",
        "concept": "AWS Secrets Manager versus SSM Parameter Store, automatic database password rotation via Lambda, and client-side secret caching to prevent API rate limit exhaustion.",
        "question": """A microservice running on EC2 connects to an RDS database and retrieves credentials from AWS Secrets Manager. Look at the code snippet.
<br><br>
<strong>Part A:</strong> Under peak traffic (5,000 requests/sec), the service begins throwing <code>ThrottlingException: Rate exceeded</code> from AWS Secrets Manager, and AWS invoices reflect thousands of dollars in Secrets Manager API costs. Explain the architectural flaw.
<br>
<strong>Part B:</strong> Compare <strong>AWS Secrets Manager</strong> against <strong>SSM Parameter Store (Standard & Advanced)</strong> across cost, automatic rotation, and cross-account access.
<br>
<strong>Part C:</strong> Describe the 4-step execution lifecycle of an AWS Lambda secret rotation function (<code>createSecret</code>, <code>setSecret</code>, <code>testSecret</code>, <code>finishSecret</code>). How does it prevent service downtime during password updates?""",
        "snippet_title": "DatabaseConnectionService.java",
        "snippet_code": """@Service
public class DatabaseConnectionService {

    @Autowired
    private AWSSecretsManager secretsClient;

    public Connection getConnection() throws SQLException {
        // Anti-Pattern: Fetching secret from AWS API on every request
        GetSecretValueRequest req = new GetSecretValueRequest().withSecretId("prod/rds/mysql");
        GetSecretValueResult result = secretsClient.getSecretValue(req);
        DbCredentials creds = JsonUtil.parse(result.getSecretString(), DbCredentials.class);

        return DriverManager.getConnection(creds.getUrl(), creds.getUser(), creds.getPassword());
    }
}""",
        "rating_concept": "Secrets Manager vs Parameter Store, client-side secret caching, and 4-step Lambda rotation",
        "solution": """<strong>Part A (The Synchronous Remote API Anti-Pattern):</strong>
<br>• AWS Secrets Manager is a remote web service with hard API rate limits (default: 10,000 requests/sec shared across an account) and bills <strong>$0.05 per 10,000 API calls</strong>.
<br>• Calling <code>getSecretValue()</code> on every single HTTP request adds 20–50ms of network latency per transaction, burns through AWS API rate limits, and racks up massive unnecessary bills.
<br>• <strong>Fix:</strong> Secrets must be cached in memory using a client-side caching library (like <code>aws-secretsmanager-caching-java</code>) with a TTL (e.g. 1 hour).
<br><br>
<strong>Part B (Secrets Manager vs SSM Parameter Store):</strong>
<br>• <strong>Parameter Store:</strong> Standard parameters are <strong>free</strong> ($0/parameter), max 4KB size, supports KMS encryption. Advanced parameters cost $0.05/month, up to 8KB size. Does not have native automated rotation.
<br>• <strong>Secrets Manager:</strong> $0.40/secret/month. Natively integrates with AWS Lambda for automatic credential rotation (RDS, DocumentDB, Redshift), and enables cross-account secret sharing easily.
<br><br>
<strong>Part C (The 4-Step Rotation Lifecycle):</strong>
<br>1. <code>createSecret</code>: Generates a new random password and stores it in Secrets Manager under the <code>AWSPENDING</code> version stage.
<br>2. <code>setSecret</code>: Connects to the database and alters the user's password to the new pending password.
<br>3. <code>testSecret</code>: Tests connecting to the database using the <code>AWSPENDING</code> password.
<br>4. <code>finishSecret</code>: Moves the <code>AWSPENDING</code> label to <code>AWSCURRENT</code>. Old connections continue running; new connections read the updated secret.""",
        "optimized_code": """// In-Memory Secret Caching using AWS SDK Caching Component
SecretCache cache = new SecretCache();

public Connection getConnection() {
    // Reads from memory; automatically refreshes when expired
    String secretJson = cache.getSecretString("prod/rds/mysql");
    DbCredentials creds = JsonUtil.parse(secretJson, DbCredentials.class);
    return dataSourcePool.getConnection();
}""",
        "junior_eval": "Calls getSecretValue() directly in business methods or suggests hardcoding secrets in application configs to avoid the API cost.",
        "expert_eval": "Implements local in-memory caching with TTL, contrasts Parameter Store free tier vs Secrets Manager, and details the 4-step AWSPENDING to AWSCURRENT rotation state machine."
    })

    # Q12: DynamoDB Partition Key Design & Hot Partitions
    questions.append({
        "id": 12,
        "badge": "NoSQL Architecture & High Throughput",
        "keywords": "dynamodb partition key hot partition throttling gsi write sharding salting",
        "concept": "Amazon DynamoDB partition key hashing, storage partition limits (1,000 WCU / 3,000 RCU per physical partition), hot partition throttling, and write sharding (salting).",
        "question": """An e-commerce platform uses Amazon DynamoDB to record order events. Look at the table schema and query snippet.
<br><br>
<strong>Part A:</strong> The table is provisioned with 10,000 Write Capacity Units (WCUs). During a flash sale, write traffic is only 1,500 requests/sec, but DynamoDB returns <code>ProvisionedThroughputExceededException</code> and throttles requests. Explain how the partition key design caused a <strong>Hot Partition</strong>.
<br>
<strong>Part B:</strong> What are the hard physical throughput and storage limits of an individual DynamoDB storage partition?
<br>
<strong>Part C:</strong> How does <strong>Write Sharding (Partition Salting)</strong> solve hot partitions for high-throughput write workloads?""",
        "snippet_title": "DynamoDbOrderRepository.java",
        "snippet_code": """// DynamoDB Table: OrderEvents
// Partition Key: Status ("PENDING", "APPROVED", "SHIPPED")
// Sort Key: Timestamp (Epoch milliseconds)

public void saveOrderEvent(OrderEvent event) {
    Item item = new Item()
        .withPrimaryKey("Status", event.getStatus(), "Timestamp", event.getTimestamp())
        .withString("OrderId", event.getOrderId())
        .withDouble("Amount", event.getAmount());

    table.putItem(item);
}""",
        "rating_concept": "DynamoDB partition key design, hot partition throttling, and write sharding (salting)",
        "solution": """<strong>Part A (The Hot Partition Bottleneck):</strong>
<br>• DynamoDB hashes the partition key to assign items to underlying physical storage partitions.
<br>• The table uses <code>Status</code> ("PENDING") as the partition key.
<br>• During a flash sale, 100% of newly created orders have status = "PENDING".
<br>• Therefore, <strong>all 1,500 writes hit the exact same physical partition</strong>.
<br>• Even though the total table capacity is 10,000 WCU, an individual partition cannot exceed its hard limits, so DynamoDB aggressively throttles writes.
<br><br>
<strong>Part B (Physical Partition Limits):</strong>
<br>Every physical DynamoDB partition has strict internal limits:
<br>• Max <strong>1,000 WCUs</strong> (Write Capacity Units).
<br>• Max <strong>3,000 RCUs</strong> (Read Capacity Units).
<br>• Max <strong>10 GB</strong> of data storage.
<br>When total table capacity or size exceeds these thresholds, DynamoDB automatically splits partitions, dividing total provisioned capacity evenly across all partitions.
<br><br>
<strong>Part C (Write Sharding / Salting Solution):</strong>
<br>Append a calculated or random suffix (salt) to the partition key (e.g. <code>PENDING_0</code> through <code>PENDING_9</code>).
<br>Writes are distributed evenly across 10 distinct physical partitions, multiplying throughput capacity by 10x ($10 \\times 1,000 = 10,000$ WCU).""",
        "optimized_code": """public void saveOrderEventSharded(OrderEvent event) {
    // Distribute across 10 shards (0-9)
    int shardId = ThreadLocalRandom.current().nextInt(10);
    String shardedPartitionKey = event.getStatus() + "_" + shardId;

    Item item = new Item()
        .withPrimaryKey("StatusShard", shardedPartitionKey, "Timestamp", event.getTimestamp())
        .withString("OrderId", event.getOrderId());

    table.putItem(item);
}""",
        "junior_eval": "Recommends switching to On-Demand capacity or paying for 50,000 WCUs (which will still throttle on the single hot partition).",
        "expert_eval": "Identifies low-cardinality partition keys, cites the 1,000 WCU / 10GB physical partition limit, and implements write sharding (salting) with parallel scatter-gather queries."
    })

    # Q13: Amazon API Gateway: Throttling & Lambda Authorizers
    questions.append({
        "id": 13,
        "badge": "API Management & Edge Gateways",
        "keywords": "api gateway throttling token bucket lambda authorizer usage plan caching",
        "concept": "Amazon API Gateway Token Bucket rate limiting, account-level burst limits, Usage Plans, and caching Lambda Authorizer evaluation results.",
        "question": """A public REST API is hosted on Amazon API Gateway fronting an AWS Lambda backend with a custom Lambda Token Authorizer. Look at the configuration snippet.
<br><br>
<strong>Part A:</strong> Explain how API Gateway enforces rate limiting using the <strong>Token Bucket algorithm</strong>. What is the difference between the Rate limit (e.g. 5,000 req/sec) and the Burst limit (e.g. 10,000 requests)?
<br>
<strong>Part B:</strong> In production, API latency spikes by 150ms on every single request, and costs explode. Inspection reveals that the Lambda Authorizer is being invoked for every single endpoint call. Why is authorizer result caching critical?
<br>
<strong>Part C:</strong> Compare an <strong>API Gateway REST API</strong> against an <strong>API Gateway HTTP API</strong>. Under what conditions should you choose HTTP API for modern microservices?""",
        "snippet_title": "api-gateway-authorizer.tf",
        "snippet_code": """resource "aws_api_gateway_authorizer" "jwt_authorizer" {
  name                   = "custom-jwt-authorizer"
  rest_api_id            = aws_api_gateway_rest_api.app_api.id
  authorizer_uri         = aws_lambda_function.authorizer_lambda.invoke_arn
  authorizer_result_ttl_in_seconds = 0 # Anti-Pattern: Disabled caching
  type                   = "TOKEN"
  identity_source        = "method.request.header.Authorization"
}""",
        "rating_concept": "API Gateway Token Bucket throttling, Lambda Authorizer caching, and REST vs HTTP APIs",
        "solution": """<strong>Part A (Token Bucket Rate vs Burst):</strong>
<br>• <strong>Rate Limit:</strong> The steady-state rate at which tokens are added to the bucket (e.g., 5,000 tokens/second). Represents the continuous sustained capacity.
<br>• <strong>Burst Limit:</strong> The total capacity of the bucket (e.g., 10,000 tokens). Allows sudden microsecond bursts of traffic without throwing HTTP 429 errors.
<br>• If a burst of 8,000 requests arrives in 100ms, the bucket drains immediately. The 8,001st request is throttled with <code>HTTP 429 Too Many Requests</code> until tokens refill.
<br><br>
<strong>Part B (Lambda Authorizer Caching TTL):</strong>
<br>• When <code>authorizer_result_ttl_in_seconds = 0</code>, API Gateway invokes the Authorizer Lambda function on <strong>every single incoming HTTP request</strong>.
<br>• This doubles Lambda execution costs, adds 50–150ms of extra latency per hop, and risks exhausting account Lambda concurrency limits.
<br><strong>Fix:</strong> Set <code>authorizer_result_ttl_in_seconds = 300</code> (5 minutes). API Gateway caches the generated IAM policy keyed by the Authorization header, validating subsequent calls at the edge in sub-millisecond time.
<br><br>
<strong>Part C (REST API vs HTTP API):</strong>
<br>• <strong>HTTP API:</strong> Up to 70% cheaper ($1.00/million vs $3.50/million), lower latency, native OIDC/OAuth2 JWT validation at edge without custom Lambda. Ideal for cloud-native microservices.
<br>• <strong>REST API:</strong> Required if you need API Keys, Usage Plans, Request Validation, WAF integration, or SOAP/XML transformations.""",
        "optimized_code": """resource "aws_api_gateway_authorizer" "jwt_authorizer" {
  name                             = "custom-jwt-authorizer"
  rest_api_id                      = aws_api_gateway_rest_api.app_api.id
  authorizer_uri                   = aws_lambda_function.authorizer_lambda.invoke_arn
  authorizer_result_ttl_in_seconds = 300 # Cache policy for 5 minutes
  type                             = "TOKEN"
  identity_source                  = "method.request.header.Authorization"
}""",
        "junior_eval": "Disables authorizer caching completely due to fear of stale user roles or cannot explain the difference between burst and steady-state rate limits.",
        "expert_eval": "Configures Token Bucket rate and burst parameters, enables 300s authorizer policy caching, and compares HTTP API vs REST API cost and latency profiles."
    })

    # Q14: Blue/Green & Canary Deployments with AWS CodeDeploy
    questions.append({
        "id": 14,
        "badge": "CI/CD & Zero-Downtime Rollouts",
        "keywords": "codedeploy blue green canary linear traffic shifting alb target group rollback",
        "concept": "AWS CodeDeploy deployment strategies, Canary vs Linear traffic shifting, ALB weighted target groups, and automated CloudWatch rollback alarms.",
        "question": """A continuous deployment pipeline uses AWS CodeDeploy to release updates to an auto-scaled EC2 cluster behind an Application Load Balancer. Look at the CodeDeploy configuration snippet.
<br><br>
<strong>Part A:</strong> Contrast an <strong>In-Place Deployment</strong> against a <strong>Blue/Green Deployment</strong> across rollback speed, infrastructure cost, and downtime risk.
<br>
<strong>Part B:</strong> What is the difference between <code>CodeDeployDefault.Canary10Percent5Minutes</code> and <code>CodeDeployDefault.Linear10PercentEvery1Minute</code>?
<br>
<strong>Part C:</strong> How do CloudWatch Alarms and ALB Weighted Target Groups collaborate during traffic shifting to execute an automatic zero-downtime rollback if error rates breach 1%?""",
        "snippet_title": "codedeploy-deployment.tf",
        "snippet_code": """resource "aws_codedeploy_deployment_group" "app_deployment_group" {
  app_name              = aws_codedeploy_app.app.name
  deployment_group_name = "production-deployment-group"
  service_role_arn      = aws_iam_role.codedeploy_role.arn

  deployment_config_name = "CodeDeployDefault.Canary10Percent5Minutes"

  deployment_style {
    deployment_option = "WITH_TRAFFIC_CONTROL"
    deployment_type   = "BLUE_GREEN"
  }

  load_balancer_info {
    target_group_info {
      name = aws_lb_target_group.target_group_blue.name
    }
  }
}""",
        "rating_concept": "AWS CodeDeploy Blue/Green vs Canary deployments, weighted target groups, and alarm rollbacks",
        "solution": """<strong>Part A (In-Place vs Blue/Green Comparison):</strong>
<br>• <strong>In-Place Deployment:</strong> Stops application on existing instances, updates code, and restarts.
<br><em>Pros:</em> Zero extra infrastructure cost.
<br><em>Cons:</em> Reduces cluster capacity during deploy; rollback requires redeploying old code (slow, 5–15 mins downtime risk).
<br>• <strong>Blue/Green Deployment:</strong> Provisions a brand-new identical Green fleet alongside the active Blue fleet.
<br><em>Pros:</em> Zero downtime; instant rollback by shifting load balancer back to Blue fleet in seconds.
<br><em>Cons:</em> Temporarily doubles compute costs during deployment.
<br><br>
<strong>Part B (Canary vs Linear Traffic Shifting):</strong>
<br>• <code>Canary10Percent5Minutes</code>: Shifts exactly 10% of traffic to the Green fleet for 5 minutes. If no alarms fire, the remaining 90% shifts immediately in one step.
<br>• <code>Linear10PercentEvery1Minute</code>: Shifts 10% of traffic every minute gradually (10%, 20%, 30%... 100%), taking 10 minutes total. Ideal for large fleets to detect subtle memory leaks.
<br><br>
<strong>Part C (Automated Rollback Integration):</strong>
<br>CodeDeploy shifts traffic by adjusting ALB Weighted Target Groups (e.g. Blue: 90%, Green: 10%).
<br>A CloudWatch Alarm monitors <code>HTTPCode_Target_5XX_Count</code> on the Green Target Group. If the alarm enters <code>ALARM</code> state, CodeDeploy automatically halts the deployment, sets Green traffic weight to 0%, and shifts 100% back to Blue.""",
        "optimized_code": """resource "aws_codedeploy_deployment_group" "app_deployment_group" {
  # ...
  auto_rollback_configuration {
    enabled = true
    events  = ["DEPLOYMENT_FAILURE", "DEPLOYMENT_STOP_ON_ALARM"]
  }

  alarm_configuration {
    alarms  = [aws_cloudwatch_metric_alarm.green_5xx_alarm.name]
    enabled = true
  }
}""",
        "junior_eval": "Uses in-place OneAtATime deployments without load balancer health checks, leaving the cluster in a mixed, broken state when updates fail.",
        "expert_eval": "Designs Blue/Green pipelines with Canary traffic shifting, hooks CloudWatch 5XX alarms for automated instant rollback, and manages ALB weighted target groups."
    })

    # Q15: AWS CloudWatch: Metrics, Percentiles & Composite Alarms
    questions.append({
        "id": 15,
        "badge": "Observability & Operational Health",
        "keywords": "cloudwatch metrics percentiles p99 p95 average composite alarm alarm storm",
        "concept": "AWS CloudWatch metric aggregation, why <code>Average</code> statistics mask critical tail-latency outages, percentile metrics (<code>p99</code>, <code>p99.9</code>), and CloudWatch Composite Alarms.",
        "question": """An e-commerce API serves 10,000 requests per minute. Look at the CloudWatch Alarm configuration snippet.
<br><br>
<strong>Part A:</strong> During peak hours, hundreds of VIP corporate customers experience 15-second checkout hangs and timeouts, yet the CloudWatch alarm never triggers. Why does using the <strong>Average</strong> statistic mask catastrophic tail latency?
<br>
<strong>Part B:</strong> What is the difference between <code>p95</code>, <code>p99</code>, and <code>p99.9</code> latency statistics? How does CloudWatch calculate percentiles across distributed clusters?
<br>
<strong>Part C:</strong> During an Amazon RDS database failover, 40 separate CloudWatch alarms fire simultaneously across microservices, causing an <strong>Alarm Storm</strong> that overwhelms the on-call engineer. How do <strong>CloudWatch Composite Alarms</strong> prevent alarm fatigue?""",
        "snippet_title": "cloudwatch-alarms.tf",
        "snippet_code": """resource "aws_cloudwatch_metric_alarm" "api_latency_alarm" {
  alarm_name          = "api-high-latency"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Average" # Flawed statistic for latency
  threshold           = 2.0       # 2 seconds
}""",
        "rating_concept": "CloudWatch percentiles (p99 vs Average) and Composite Alarms for alarm storm reduction",
        "solution": """<strong>Part A (The Fallacy of the Average):</strong>
<br>• If 9,900 requests take 50ms, and 100 requests take 15,000ms (15 seconds):
<br>• The mathematical average is: $\\frac{(9900 \\times 0.05) + (100 \\times 15)}{10000} = \\frac{495 + 1500}{10000} = 0.1995\\text{s} = \\mathbf{199.5\\text{ms}}$.
<br>• Because 199ms is well below the 2.0-second threshold, the alarm <strong>never triggers</strong>!
<br>• The average statistic completely dilutes and hides the fact that 1% of your highest-value transactions are completely failing.
<br><br>
<strong>Part B (Percentile Latency Metrics):</strong>
<br>• <strong>p99 (99th percentile):</strong> 99% of requests are faster than this value; exactly 1 out of 100 is slower. (Reflects the true user experience of worst-case transactions).
<br>• <strong>p99.9 (99.9th percentile):</strong> 1 out of 1,000 requests is slower. Crucial for distributed systems where a single user request invokes 20 internal microservices.
<br><br>
<strong>Part C (CloudWatch Composite Alarms):</strong>
<br>Composite Alarms use boolean logic (<code>AND</code>, <code>OR</code>, <code>NOT</code>) to combine multiple alarms.
<br>Instead of paging the engineer with 40 individual alerts, a Composite Alarm checks:
<br><code>ALARM(DatabaseDown) AND (ALARM(ApiLatency) OR ALARM(OrderFailures))</code>
<br>It suppresses secondary alerts and fires a single, actionable page: <em>\"Database Failover in Progress: Suppressed 39 downstream API alerts.\"</em>""",
        "optimized_code": """resource "aws_cloudwatch_metric_alarm" "api_p99_latency" {
  alarm_name          = "api-p99-latency-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  extended_statistic  = "p99" # Monitors true tail latency
  threshold           = 1.5   # Trigger if p99 exceeds 1.5s
}""",
        "junior_eval": "Relies entirely on Average CPU and Latency metrics, unable to explain why high-value user checkouts time out while monitoring dashboards show green.",
        "expert_eval": "Calculates percentile tail-latency masking math, configures p99/p99.9 extended statistics, and groups alerts into Composite Alarms to eliminate alarm fatigue."
    })

    # Q16: Amazon CloudFront & S3: Cache Invalidation & Edge Functions
    questions.append({
        "id": 16,
        "badge": "Edge Caching & Content Delivery",
        "keywords": "cloudfront s3 cache invalidation oac origin access control edge functions s-maxage",
        "concept": "Amazon CloudFront CDN caching hierarchies, Cache-Control headers (<code>max-age</code> vs <code>s-maxage</code>), Origin Access Control (OAC), and CloudFront Functions vs Lambda@Edge.",
        "question": """A high-traffic web application serves static assets and dynamic APIs through Amazon CloudFront. Look at the deployment script.
<br><br>
<strong>Part A:</strong> After every continuous integration build, a script executes <code>aws cloudfront create-invalidation --paths "/*"</code>. Why is blanket wildcard cache invalidation considered an operational anti-pattern?
<br>
<strong>Part B:</strong> What is the difference between <code>Cache-Control: max-age=3600</code> and <code>Cache-Control: s-maxage=86400</code>? How do you achieve instant zero-cost cache updates using asset fingerprinting?
<br>
<strong>Part C:</strong> Compare <strong>CloudFront Functions</strong> against <strong>Lambda@Edge</strong> across execution location, runtime restrictions, latency, and capability to make external network calls.""",
        "snippet_title": "deploy-frontend.sh",
        "snippet_code": """# Problematic CI/CD Deployment Script
aws s3 sync ./dist s3://company-frontend-assets/
aws cloudfront create-invalidation --distribution-id E123456EXAMPLE --paths "/*" """,
        "rating_concept": "CloudFront caching, s-maxage, asset fingerprinting, and CloudFront Functions vs Lambda@Edge",
        "solution": """<strong>Part A (Why Wildcard Invalidation Is an Anti-Pattern):</strong>
<br>1. <strong>Cost:</strong> AWS provides 1,000 free invalidation paths per month; each additional path costs $0.005. Running wildcard invalidations on every commit across staging and production racks up unnecessary charges.
<br>2. <strong>Cache Stampede:</strong> Invalidating the entire edge cache forces millions of subsequent user requests to bypass CloudFront and hit the origin S3/backend simultaneously, risking origin collapse.
<br><br>
<strong>Part B (Asset Fingerprinting & Caching Headers):</strong>
<br>• <strong>Fingerprinting / Content Hashing:</strong> Build tools (Webpack, Vite) generate immutable filenames with content hashes (e.g. <code>main.7f8b9c.js</code>).
<br>• When a file is updated, its filename changes. The new HTML loads the new URL immediately &mdash; <strong>zero cache invalidation required!</strong>
<br>• <code>s-maxage=31536000</code>: Tells shared caches (CloudFront CDN) to cache the immutable hashed asset for 1 year.
<br>• <code>max-age=3600</code>: Directs the end-user's browser cache.
<br><br>
<strong>Part C (CloudFront Functions vs Lambda@Edge):</strong>
<br>• <strong>CloudFront Functions:</strong> Lightweight JavaScript engine running at 450+ CloudFront edge points of presence. Sub-millisecond execution, max execution time < 1ms, 2MB memory limit. Ideal for URL rewrites, header manipulation, and redirect normalization. (Cannot make external HTTP calls).
<br>• <strong>Lambda@Edge:</strong> Full Node.js/Python runtime running at Regional Edge Caches (13 locations). Can make remote HTTP calls, access databases, and inspect body payloads. Up to 10GB memory, 30s timeout.""",
        "optimized_code": """# Upload immutable hashed assets with 1-year CDN cache
aws s3 sync ./dist/assets s3://company-assets/assets \\
  --cache-control "public, max-age=31536000, immutable"

# Upload index.html with NO-CACHE so browsers always fetch latest bundle URL
aws s3 cp ./dist/index.html s3://company-assets/index.html \\
  --cache-control "no-cache, no-store, must-revalidate" """,
        "junior_eval": "Executes aws cloudfront create-invalidation /* on every build or doesn't know the difference between browser cache and CDN edge cache.",
        "expert_eval": "Implements immutable content-hashed asset pipelines with s-maxage headers, eliminates invalidation costs, and selects CloudFront Functions for sub-millisecond URL rewrites."
    })

    # Q17: Amazon Route 53: Routing Policies & Failover
    questions.append({
        "id": 17,
        "badge": "DNS Architecture & Global Traffic Management",
        "keywords": "route 53 dns failover latency based routing health checks ttl split brain",
        "concept": "Amazon Route 53 DNS routing policies (Latency-Based, Geo-DNS, Failover), Route 53 health checks, and DNS TTL caching dynamics during disaster recovery.",
        "question": """An enterprise deploys a multi-region Active-Passive disaster recovery architecture between <code>us-east-1</code> (Primary) and <code>us-west-2</code> (Secondary). Look at the Route 53 configuration snippet.
<br><br>
<strong>Part A:</strong> The primary region suffers a total outage. Route 53 health checks detect the failure and trigger DNS failover within 30 seconds. However, 40% of global user traffic continues attempting to connect to the dead primary region for hours. Explain why.
<br>
<strong>Part B:</strong> What is an <strong>Alias Record</strong> in Route 53, and why is an Alias record preferred over a standard <code>CNAME</code> record when pointing the apex zone (e.g. <code>example.com</code>) to an Application Load Balancer?
<br>
<strong>Part C:</strong> Compare <strong>Latency-Based Routing</strong> against <strong>Geolocation Routing</strong>. Which policy should be selected to enforce European Union GDPR data residency compliance?""",
        "snippet_title": "route53-failover.tf",
        "snippet_code": """resource "aws_route53_record" "primary_failover" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.company.com"
  type    = "A"
  ttl     = 86400 # 24 Hours Anti-Pattern for Failover Records

  failover_routing_policy {
    type = "PRIMARY"
  }

  set_identifier = "primary-us-east-1"
  health_check_id = aws_route53_health_check.primary_health.id
}""",
        "rating_concept": "Route 53 DNS failover, TTL caching impact on disaster recovery, and Alias vs CNAME records",
        "solution": """<strong>Part A (DNS TTL Caching & Stale Client Resolvers):</strong>
<br>• The DNS record configuration sets <code>ttl = 86400</code> (24 hours).
<br>• When clients query DNS, recursive resolvers (ISPs, Google 8.8.8.8, enterprise proxies) <strong>cache the IP address for the duration of the TTL</strong>.
<br>• Even though Route 53 updates its authoritative nameserver within 30 seconds, millions of client machines and ISP resolvers will not query Route 53 again until their local 24-hour cache expires.
<br><strong>Fix:</strong> For failover and dynamic endpoints, set TTL to <strong>10 to 60 seconds</strong>.
<br><br>
<strong>Part B (Alias Records vs CNAME at Zone Apex):</strong>
<br>• <strong>DNS RFC 1034 Rule:</strong> A CNAME record cannot coexist with other records (like SOA or NS) at the <strong>zone apex</strong> (root domain: <code>company.com</code>).
<br>• <strong>Alias Records:</strong> An AWS proprietary DNS extension that maps the apex domain directly to AWS resources (ALB, CloudFront, S3) using native <code>A</code> queries. Route 53 resolves the ALB IP internally with zero extra DNS hops, and queries to Alias records are completely free.
<br><br>
<strong>Part C (Latency-Based vs Geolocation Routing):</strong>
<br>• <strong>Latency-Based:</strong> Routes users to the AWS region that yields the lowest network round-trip time.
<br>• <strong>Geolocation:</strong> Routes traffic based strictly on the geographic origin of the user's IP (e.g., all traffic originating from Europe routes to Frankfurt <code>eu-central-1</code>). Geolocation is <strong>strictly required</strong> to guarantee GDPR compliance and legal data residency constraints.""",
        "optimized_code": """resource "aws_route53_record" "primary_failover" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "company.com"
  type    = "A"

  alias {
    name                   = aws_lb.primary_alb.dns_name
    zone_id                = aws_lb.primary_alb.zone_id
    evaluate_target_health = true # Evaluates target group health directly
  }
}""",
        "junior_eval": "Sets high TTL (86400) on failover DNS records or tries to create a CNAME at the root apex domain.",
        "expert_eval": "Explains ISP recursive resolver caching, implements Route 53 Alias records at zone apex with target health evaluation, and enforces Geolocation routing for GDPR boundaries."
    })

    # Q18: Cross-Account Access: Confused Deputy & ExternalId
    questions.append({
        "id": 18,
        "badge": "Multi-Account Security & IAM Governance",
        "keywords": "cross account assume role external id confused deputy sts iam trust policy",
        "concept": "Multi-account AWS security governance, cross-account IAM role assumption via AWS STS, and mitigating the <strong>Confused Deputy Problem</strong> using <code>sts:ExternalId</code>.",
        "question": """A multi-tenant SaaS vendor (Vendor Account A) manages AWS infrastructure on behalf of thousands of enterprise clients (Client Account B). Look at the IAM Trust Policy snippet.
<br><br>
<strong>Part A:</strong> What is the <strong>Confused Deputy Problem</strong> in multi-tenant AWS architectures? How can a malicious tenant trick Vendor Account A into hijacking Client Account B's cloud resources?
<br>
<strong>Part B:</strong> How does adding an <code>sts:ExternalId</code> condition to the IAM trust policy mathematically eliminate the Confused Deputy vulnerability?
<br>
<strong>Part C:</strong> Contrast <strong>Identity-Based Policies</strong> (Role Assumption) against <strong>Resource-Based Policies</strong> (S3 Bucket Policies, KMS Key Policies) for granting cross-account access.""",
        "snippet_title": "trust-policy.json",
        "snippet_code": """{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::111122223333:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}""",
        "rating_concept": "Cross-account IAM role assumption, Confused Deputy mitigation, and sts:ExternalId",
        "solution": """<strong>Part A (The Confused Deputy Attack Scenario):</strong>
<br>• SaaS Vendor (Account A) manages customer AWS accounts by assuming an IAM role in each customer's account.
<br>• Customer B configures an IAM role with the trust policy above, allowing Account A to assume it.
<br>• Malicious Customer C signs up for the SaaS service. During setup, Customer C provides Customer B's AWS Role ARN.
<br>• When Customer C asks the SaaS service to run an action, the SaaS platform (the \"deputy\") blindly calls <code>sts:AssumeRole(RoleArn = Customer B's ARN)</code>.
<br>• Because the trust policy allows Account A unconditionally, STS permits the call. Customer C now controls Customer B's entire AWS infrastructure through the confused deputy!
<br><br>
<strong>Part B (The sts:ExternalId Defense):</strong>
<br>• The SaaS vendor generates a unique, cryptographically random <code>ExternalId</code> per tenant upon registration.
<br>• Customer B configures their trust policy with:
<br><code>\"Condition\": { \"StringEquals\": { \"sts:ExternalId\": \"tenant-xyz-secret-uuid\" } }</code>
<br>• When assuming the role, Account A passes the specific tenant's ExternalId. Malicious Customer C cannot guess Customer B's ExternalId, and STS rejects the assumption.
<br><br>
<strong>Part C (Identity-Based vs Resource-Based Policies):</strong>
<br>• <strong>Identity-Based (AssumeRole):</strong> Requires the caller to give up original IAM permissions and take on the target role's identity via STS temporary credentials.
<br>• <strong>Resource-Based (S3 Bucket Policy):</strong> The caller retains their original identity and directly accesses the resource. The principal account does not need to assume a role.""",
        "optimized_code": """{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::111122223333:root" },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "e9c4-4f81-9b12-client-uuid-778"
        }
      }
    }
  ]
}""",
        "junior_eval": "Leaves IAM trust policies open to root account ARNs without conditions, unaware of cross-tenant privilege escalation.",
        "expert_eval": "Walks through the Confused Deputy attack vector, enforces sts:ExternalId conditions in cross-account trust policies, and compares STS role assumption with resource-based policies."
    })

    # Q19: AWS Lambda Concurrency: Reserved vs Provisioned
    questions.append({
        "id": 19,
        "badge": "Serverless Scaling & Resource Allocation",
        "keywords": "lambda concurrency reserved provisioned burst limit unreserved pool 429",
        "concept": "AWS Lambda regional concurrency quotas (default 1,000), unreserved concurrency pool starvation, Reserved Concurrency vs Provisioned Concurrency, and burst capacity.",
        "question": """An enterprise runs 40 microservices on AWS Lambda within a single AWS account. Look at the architecture and configuration.
<br><br>
<strong>Part A:</strong> A non-critical background data ingestion Lambda spikes to 1,000 concurrent executions. Instantly, all other critical Lambda functions in the account (including payment processing and login APIs) fail with <code>HTTP 429 Too Many Requests: Rate Exceeded</code>. Explain why this account-wide starvation occurs.
<br>
<strong>Part B:</strong> What is <strong>Reserved Concurrency</strong>? Explain how it serves both as a guaranteed floor AND as a strict ceiling.
<br>
<strong>Part C:</strong> Contrast <strong>Provisioned Concurrency</strong> against <strong>Reserved Concurrency</strong>. How does Provisioned Concurrency completely eliminate cold starts for low-latency financial transactions?""",
        "snippet_title": "lambda-concurrency.tf",
        "snippet_code": """resource "aws_lambda_function" "background_ingest_lambda" {
  function_name = "heavy-background-ingest"
  runtime       = "java17"
  handler       = "com.company.IngestHandler::handleRequest"
  memory_size   = 2048
  timeout       = 300
  # No concurrency limits specified
}""",
        "rating_concept": "Lambda concurrency allocation, Reserved vs Provisioned concurrency, and unreserved pool exhaustion",
        "solution": """<strong>Part A (Account-Wide Concurrency Exhaustion):</strong>
<br>• AWS accounts have a default regional concurrency limit of <strong>1,000 concurrent executions</strong> shared across all Lambda functions in the region.
<br>• Functions without explicit configuration draw from the <strong>Unreserved Concurrency Pool</strong>.
<br>• If a background ETL or batch job scales to 1,000 executions, it completely drains the unreserved pool.
<br>• Any other function in the account (even a critical 10ms payment API) cannot allocate execution slots and is immediately throttled with <code>HTTP 429 Rate Exceeded</code>.
<br><br>
<strong>Part B (Reserved Concurrency: Floor & Ceiling):</strong>
<br>• Allocating <code>reserved_concurrent_executions = 200</code> achieves two things:
<br>1. <strong>Guaranteed Floor:</strong> 200 execution slots are dedicated strictly to this function; other functions cannot steal them.
<br>2. <strong>Strict Ceiling:</strong> The function can never scale beyond 200 executions, preventing it from consuming the rest of the account's unreserved pool.
<br><em>Note:</em> AWS requires at least 100 concurrency units to remain in the unreserved pool.
<br><br>
<strong>Part C (Provisioned Concurrency):</strong>
<br>• Reserved Concurrency allocates slots, but instances still suffer initial cold starts upon invocation.
<br>• <strong>Provisioned Concurrency:</strong> AWS pre-initializes the execution environment, boots the JVM, and loads classes in advance. Functions respond in sub-10ms with <strong>zero cold starts</strong>. It is billed per GB-second of provisioned uptime.""",
        "optimized_code": """resource "aws_lambda_function" "critical_payment_lambda" {
  function_name = "payment-processor"
  # ...
  reserved_concurrent_executions = 300 # Isolates 300 slots for payment
}

resource "aws_lambda_provisioned_concurrency_config" "payment_warm" {
  function_name                     = aws_lambda_function.critical_payment_lambda.function_name
  provisioned_concurrent_executions = 50 # 50 pre-warmed JVMs ready for zero-latency calls
  qualifier                         = "prod"
}""",
        "junior_eval": "Assumes Lambda functions have unlimited independent scaling or leaves background batch jobs unthrottled in production.",
        "expert_eval": "Explains regional unreserved concurrency exhaustion, applies Reserved Concurrency to isolate critical microservices, and allocates Provisioned Concurrency for zero-cold-start SLAs."
    })

    # Q20: AWS Disaster Recovery Architectures: RPO / RTO & Strategies
    questions.append({
        "id": 20,
        "badge": "High Availability & Multi-Region DR",
        "keywords": "disaster recovery rpo rto pilot light warm standby active active multi region aurora global",
        "concept": "AWS Disaster Recovery strategies (Backup & Restore, Pilot Light, Warm Standby, Multi-Region Active-Active), RPO vs RTO trade-offs, and Amazon Aurora Global Database replication.",
        "question": """An enterprise defines a Disaster Recovery mandate for its tier-1 payment microservices: Recovery Point Objective (RPO) < 1 minute, and Recovery Time Objective (RTO) < 15 minutes, with optimized cost. Look at the architecture diagram and script.
<br><br>
<strong>Part A:</strong> Define <strong>RPO</strong> and <strong>RTO</strong> in the context of an AWS regional disaster (e.g. total data center loss in <code>us-east-1</code>).
<br>
<strong>Part B:</strong> Evaluate the 4 standard AWS Disaster Recovery strategies: <strong>Backup & Restore</strong>, <strong>Pilot Light</strong>, <strong>Warm Standby</strong>, and <strong>Multi-Region Active-Active</strong> across cost, complexity, and RPO/RTO metrics.
<br>
<strong>Part C:</strong> Detail the architecture of a <strong>Pilot Light</strong> deployment using Amazon Aurora Global Database and Terraform to meet the 15-minute RTO mandate without paying for idle EC2/EKS clusters in the secondary region.""",
        "snippet_title": "aurora-global-dr.tf",
        "snippet_code": """resource "aws_rds_global_cluster" "global_db" {
  global_cluster_identifier = "enterprise-global-db"
  engine                    = "aurora-postgresql"
  engine_version            = "15.4"
  database_name             = "payments"
  storage_encrypted         = true
}

resource "aws_rds_cluster" "primary_cluster" {
  cluster_identifier        = "aurora-primary-us-east-1"
  global_cluster_identifier = aws_rds_global_cluster.global_db.id
  # Active Primary in us-east-1
}""",
        "rating_concept": "AWS Disaster Recovery strategies, RPO/RTO calculations, and Pilot Light architecture with Aurora Global DB",
        "solution": """<strong>Part A (RPO vs RTO in Cloud Disaster Recovery):</strong>
<br>• <strong>RPO (Recovery Point Objective):</strong> The maximum acceptable volume of data loss measured in time. RPO < 1 minute means after failover, data loss cannot exceed 60 seconds of transactions.
<br>• <strong>RTO (Recovery Time Objective):</strong> The maximum allowable downtime before business operations are restored. RTO < 15 minutes means systems must be fully processing traffic in the secondary region within 15 minutes.
<br><br>
<strong>Part B (The 4 AWS DR Strategies Comparison):</strong>
<br>1. <strong>Backup & Restore:</strong> Periodic snapshots to S3/Glacier. Cost: $, RTO: 24+ hours, RPO: 24 hours.
<br>2. <strong>Pilot Light:</strong> Core data is continuously replicated; minimal core infrastructure (databases) is live; compute is launched on failover. Cost: $$, RTO: 10–15 mins, RPO: < 1 min.
<br>3. <strong>Warm Standby:</strong> Scaled-down minimum fleet running 24/7 in secondary region, scaled out during failover. Cost: $$$, RTO: minutes, RPO: seconds.
<br>4. <strong>Active-Active Multi-Region:</strong> Full capacity running in both regions simultaneously. Cost: $$$$, RTO: near 0, RPO: near 0.
<br><br>
<strong>Part C (Pilot Light Architecture Implementation):</strong>
<br>• <strong>Database Layer:</strong> Amazon Aurora Global Database replicates storage across regions asynchronously at the storage layer with typical replication latency <strong>under 1 second</strong> (meeting RPO < 1m).
<br>• <strong>Compute Layer:</strong> Golden AMIs and container images are replicated to the secondary region. Compute instances are <strong>not running</strong> (saving 70% of infrastructure cost).
<br>• <strong>Failover Automation:</strong> An automated script promotes the secondary Aurora cluster to standalone master (takes 1 minute), applies Terraform to spin up ASG/EKS compute from cached images (takes 8–10 minutes), and updates Route 53 DNS (takes 1 minute), comfortably meeting RTO < 15 minutes.""",
        "optimized_code": """# Secondary Region Aurora Replica (Pilot Light)
resource "aws_rds_cluster" "secondary_cluster" {
  provider                  = aws.secondary_region # us-west-2
  cluster_identifier        = "aurora-secondary-us-west-2"
  global_cluster_identifier = aws_rds_global_cluster.global_db.id

  # Compute instances in secondary region run minimal or zero nodes until promoted
}""",
        "junior_eval": "Assumes nightly S3 snapshots meet 15-minute RTO or insists on Multi-Region Active-Active for all applications regardless of budget or complexity.",
        "expert_eval": "Defines RPO/RTO quantitatively, designs a cost-optimized Pilot Light architecture with Aurora Global Database (<1s replication lag), and scripts automated infrastructure-as-code promotion."
    })

    return questions

def generate_aws_html():
    from create_aws_page import html_header, html_footer
    questions = get_aws_questions()

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
            # strip single-line comments (# or //) if not part of http://
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
                                <button class="star-btn" data-rating="1" onclick="setQuestionRating('aws', {q_id}, 1, '{rating_concept_escaped}')">
                                    <span class="star-num">1</span>
                                    <span class="star-label">Cannot Explain</span>
                                </button>
                                <button class="star-btn" data-rating="2" onclick="setQuestionRating('aws', {q_id}, 2, '{rating_concept_escaped}')">
                                    <span class="star-num">2</span>
                                    <span class="star-label">Partial</span>
                                </button>
                                <button class="star-btn" data-rating="3" onclick="setQuestionRating('aws', {q_id}, 3, '{rating_concept_escaped}')">
                                    <span class="star-num">3</span>
                                    <span class="star-label">Good</span>
                                </button>
                                <button class="star-btn" data-rating="4" onclick="setQuestionRating('aws', {q_id}, 4, '{rating_concept_escaped}')">
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
                                <div class="code-header"><span>Architectural / Code Solution</span><span class="code-lang">Terraform / Java / Config</span></div>
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

    out_path = "/Users/barvepan/Pandharinath/Developer/Workspace/interview-questions/aws-deployment.html"
    with open(out_path, "w") as f:
        f.write(full_html)
    print(f"Generated {out_path} with {len(questions)} questions successfully!")

if __name__ == "__main__":
    generate_aws_html()

