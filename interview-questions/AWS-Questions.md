### AWS Questions

#### **VPC CIDR Blocks**
  - CIDR blocks size can be between /16 to /28
  - First four and last IP address are not available for use
#### **Amazon VPC**
  - Logically isolated virtual network in the AWS cloud
  - **Components**
    - **Subnet**
      - It is a section of the network that shares a common address component. All instances whose addresses have the same prefix are in the same subnet. For e.g. EC2 instances whose IP starts with 10.0.1 would be part of the same subnet.
      - Private Subnet
        - Resources from private subnet not exposed to outside world
      - Public Subnet
        - Public Subnet where resources are exposed to the internet through Internet Gateway.
    - **Router**
    - **Internet Gateway**
    - **NAT Instance**
      - Enables internet access for EC2 instances in private subnets ( managed by you )
    - **NAT Gateway**
      - Enables internet access for EC2 instances in private subnets ( managed by AWS )
    - **Security Group**
      - Instance level firewall
    - **Network ACL**
      - Subnet level firewall
  - When you create a VPC, you must specify a range of IPv4 addresses for the VPC in the form of a Classless Inter Domain Routing (CIDR) block. For e.g. 10.0.0.0/16
  - VPC spans all availability zones of the region

#### **Simple Storage Service - S3**
  - S3 standard
  - S3 standard - IA
  - S3 inteligent tiering
  - S3 glacier - instant retrievals
  - S3 glacier - fliexible retrivals
  - S3 glacier - deep archive
