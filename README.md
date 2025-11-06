# CS446/646 HW2: Microservices with RPC and Load Balancing

Build a distributed microservices system from scratch using TCP sockets, implementing RPC, load balancing, and fault tolerance patterns.

## Quick Start

### 1. Accept GitHub Classroom Assignment
Click the link provided by your instructor to create your private repository.

### 2. Clone Your Repository
```bash
git clone https://github.com/umb-cs446/hw2-microservices-[yourusername].git
cd hw2-microservices-[yourusername]
```

### 3. Edit the Code
Open `rpc_assignment.py` and implement all sections marked with:
```python
# TODO: STUDENT MUST IMPLEMENT
```

### 4. Test Locally

**Option A: On Your Laptop (Recommended)**
```bash
# Terminal 1: Start service instances
python3 rpc_assignment.py server 9000

# Terminal 2: Start another instance  
python3 rpc_assignment.py server 9001

# Terminal 3: Start third instance
python3 rpc_assignment.py server 9002

# Terminal 4: Run tests
python3 rpc_assignment.py test

# Or run demo mode
python3 rpc_assignment.py demo
```

**Option B: In Cloud Shell (Browser-Based)**
```bash
# Start all services in background
python3 rpc_assignment.py server 9000 &
python3 rpc_assignment.py server 9001 &
python3 rpc_assignment.py server 9002 &

# Run tests
python3 rpc_assignment.py test

# Stop services
pkill -f rpc_assignment.py
```

---

## Cloud Deployment (Required for Submission)

### Why Distributed Deployment?
Your final submission must demonstrate **true distributed system behavior**:
- Services run on separate physical machines
- Client connects over real network (from your laptop)
- Tests actual latency, failures, and recovery

### Architecture: Client-Side Load Balancing

**Important:** Your client contains the load balancer logic (client-side load balancing):

```
┌─────────────────────────────────────┐
│  Your Laptop                        │
│                                     │
│  ┌────────────────────────────┐   │
│  │ Client + LoadBalancer      │   │  Your code decides which
│  │ - select_instance()        │   │  service to call
│  │ - Circuit breakers         │   │
│  └────────────────────────────┘   │
│              │                      │
│      Directly connects to services │
└──────────────┼─────────────────────┘
               │
      ┌────────┼────────┐
      ▼        ▼        ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│Service 0 │ │Service 1 │ │Service 2 │
│  :9000   │ │  :9001   │ │  :9002   │
│GCP/Cloud │ │GCP/Cloud │ │GCP/Cloud │
└──────────┘ └──────────┘ └──────────┘
```

**No separate load balancer server** - your client code makes load balancing decisions and directly connects to services. This is how Netflix, Kubernetes, and gRPC work!

---

## Deployment Steps

### Step 1: Cloud Credentials
- Go to [https://console.cloud.google.com](https://console.cloud.google.com)
- Sign in with your account that has the $50 credits
- Create/select project: `cs446-hw2-[yourusername]`

### Step 2: Create 3 Instances

**Using Web Interface (Recommended - Easiest!):**

**Quick version:**
1. Go to: **Compute Engine** → **VM instances**
2. Click **CREATE INSTANCE** button
3. Create 3 instances with these settings:
   - Names: `rpc-service-0`, `rpc-service-1`, `rpc-service-2`
   - Region: `us-central1 (Iowa)`, Zone: `us-central1-a`
   - Machine type: `e2-micro`
   - Boot disk: Ubuntu 20.04 LTS, 10 GB
   - **IMPORTANT:** Under "Availability policy", select **Spot** (60-80% cheaper!)

**Using Command Line (Alternative):**

<details>
<summary>Click to expand gcloud commands</summary>

```bash
# Enable Compute Engine
gcloud services enable compute.googleapis.com

# Set your project
gcloud config set project cs446-hw2-[yourusername]

# Create 3 separate instances (one for each service)
for i in 0 1 2; do
  echo "Creating instance $i..."
  gcloud compute instances create rpc-service-$i \
    --zone=us-central1-a \
    --machine-type=e2-micro \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --preemptible \
    --tags=rpc-services
done
```
</details>

### Step 3: Create Firewall Rule (One-Time)

**Using Web Interface:**
1. Navigate to: **VPC network** → **Firewall**
2. Click **CREATE FIREWALL RULE**
3. Name: `allow-rpc-services`
4. Direction: Ingress, Action: Allow
5. Targets: All instances in the network
6. Source IPv4 ranges: `0.0.0.0/0`
7. Protocols and ports: Check TCP, enter `9000-9002`
8. Click **CREATE**

**Using Command Line:**

<details>
<summary>Click to expand</summary>

```bash
gcloud compute firewall-rules create allow-rpc-services \
  --allow tcp:9000-9002 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow RPC client connections"
```
</details>

### Step 4: Deploy Code to Instances

**Using Web SSH (In Browser - Easy!):**

For each instance:
1. In the VM instances list, click the **SSH** button
2. Browser terminal opens automatically
3. Run these commands:

```bash
# Install git and Python (if needed)
sudo apt-get update
sudo apt-get install -y git python3

# Clone your repository
git clone https://github.com/umb-cs446/hw2-microservices-[yourusername].git
cd hw2-microservices-[yourusername]

# Start the service (use correct port for each instance!)
# For instance-0:
nohup python3 rpc_assignment.py server 9000 > service.log 2>&1 &

# For instance-1:
nohup python3 rpc_assignment.py server 9001 > service.log 2>&1 &

# For instance-2:
nohup python3 rpc_assignment.py server 9002 > service.log 2>&1 &

# Verify it's running
ps aux | grep rpc_assignment
tail service.log
```

**Using Command Line:**

<details>
<summary>Click to expand</summary>

```bash
# Deploy to all instances
for i in 0 1 2; do
  echo "Deploying to instance $i..."
  gcloud compute ssh rpc-service-$i --zone=us-central1-a --command "
    git clone https://github.com/umb-cs446/hw2-microservices-[yourusername].git && \
    cd hw2-microservices-[yourusername] && \
    nohup python3 rpc_assignment.py server 900$i > service.log 2>&1 &
  " 
done

echo "✅ All services deployed!"
```
</details>

### Step 5: Get Instance IPs

**Using Web Interface:**
1. Go to **Compute Engine** → **VM instances**
2. Look at the **External IP** column
3. Write down the 3 IP addresses

**Using Command Line:**

<details>
<summary>Click to expand</summary>

```bash
gcloud compute instances list --format="table(name,networkInterfaces[0].accessConfigs[0].natIP)"
```
</details>

### Step 5: Test from Your Laptop

**Update your code to use cloud IPs:**

Edit `rpc_assignment.py` - find the configuration section at the top and update it:

```python
# ============================================================
# CONFIGURATION: Edit this section for cloud deployment
# ============================================================

# Comment out localhost:
# SERVICE_INSTANCES = [
#     ('localhost', 9000),
#     ('localhost', 9001),
#     ('localhost', 9002),
# ]

# Add your actual GCP instance IPs (from step 4):
SERVICE_INSTANCES = [
    ('35.232.123.45', 9000),  # Replace with YOUR instance-0 IP
    ('35.232.123.46', 9001),  # Replace with YOUR instance-1 IP
    ('35.232.123.47', 9002),  # Replace with YOUR instance-2 IP
]

# ============================================================
```

**Run tests from YOUR LAPTOP:**
```bash
python3 rpc_assignment.py test
```

This tests **real distributed behavior** - network latency, failures, load balancing!

**Important:** Remember to change back to localhost configuration for local development.

---

## Test Real Failures

One of the best parts - test your fault tolerance:

```bash
# Kill one instance
gcloud compute instances stop rpc-service-1 --zone=us-central1-a

# Run tests - should still work!
# (Your rpc_assignment.py should still have cloud IPs configured)
python3 rpc_assignment.py test

# Your circuit breaker should open for instance-1
# Load balancer should route around the failure

# Restart instance and redeploy
gcloud compute instances start rpc-service-1 --zone=us-central1-a
# Wait 30 seconds, SSH in, restart service, test again
```

---

## CRITICAL: Stop Instances When Done

**This is the most important step to save your credits!**

**Using Web Interface:**
1. Go to **Compute Engine** → **VM instances**
2. Check the boxes next to all 3 instances
3. Click **STOP** button at the top
4. Confirm

Status will change to: **Stopped (disk preserved)**

**Using Command Line:**

<details>
<summary>Click to expand</summary>

```bash
# Stop all instances (no charges while stopped)
gcloud compute instances stop rpc-service-0 rpc-service-1 rpc-service-2 \
  --zone=us-central1-a

# Check they're stopped
gcloud compute instances list

# Restart when needed
gcloud compute instances start rpc-service-0 rpc-service-1 rpc-service-2 \
  --zone=us-central1-a

# Delete completely when assignment is done
gcloud compute instances delete rpc-service-0 rpc-service-1 rpc-service-2 \
  --zone=us-central1-a --quiet
```
</details>

---

## Cost Management

### Expected Costs
- **Local development**: $0 (FREE)
- **3 instances for testing** (stopped when not using): ~$1-2 total
- **Total for assignment**: < $5

### Tips to Save Money
✅ Develop and test locally first (FREE)  
✅ Only use cloud for final distributed testing  
✅ Use preemptible instances (60-80% cheaper)  
✅ **ALWAYS stop instances** when done for the day  
✅ Delete instances when assignment complete

❌ Don't leave instances running overnight  
❌ Don't create instances until code works locally

### Monitor Your Usage
```bash
# Check running instances
gcloud compute instances list

# View billing (in browser)
# Go to: console.cloud.google.com/billing
```

---

## Submission

### What to Submit

Push these to your GitHub repository:

1. **Code**
   - `rpc_assignment.py` - Your completed implementation

2. **Documentation** (create these files)
   - `README.md` - How to run your code (you can replace this file)
   - `DESIGN.md` - Design decisions and trade-offs (1-2 pages)
   - `DEPLOYMENT.md` - Include required screenshots

3. **For Graduate Students**
   - `ADVANCED.md` - Description of advanced features

### Required Screenshots (in DEPLOYMENT.md)

1. **Instance listing:**
   ```bash
   gcloud compute instances list --format=table
   ```

2. **Test output from your laptop** connecting to cloud instances:
   ```bash
   python3 rpc_assignment.py test --ips=IP1,IP2,IP3
   ```

### How to Submit

```bash
# Commit your changes
git add .
git commit -m "Complete HW2 implementation"
git push origin main

# Your push to GitHub = submission
# Make sure you push before the deadline!
```

---

## Troubleshooting

### Can't connect to instances
```bash
# Check firewall
gcloud compute firewall-rules list

# Verify rule exists
gcloud compute firewall-rules describe allow-rpc-services
```

### Service not running
```bash
# SSH to instance
gcloud compute ssh rpc-service-0 --zone=us-central1-a

# Check if running
ps aux | grep rpc_assignment

# Check logs
cd hw2-microservices-[yourusername]
cat service.log

# Restart manually
python3 rpc_assignment.py server 9000 &
```

### Port already in use (local testing)
```bash
# Find process using port
lsof -i :9000

# Kill process
kill -9 [PID]

# Or kill all
pkill -f rpc_assignment.py
```

---

## Alternative: CloudLab (Free)

If you prefer CloudLab:
- Request 3 nodes at [https://cloudlab.us](https://cloudlab.us)
- SSH to each node
- Clone repository and run one service per node
- Test from your laptop

---

## Files in This Repository

- `rpc_assignment.py` - Main file you need to complete
- `README.md` - This file
- `.gitignore` - Git ignore rules

---

## Important Dates

- **Assignment Released**: 11/06/2025
- **Due Date**: 12/05/2025 at 11:59 PM

---

## Academic Integrity

- This is an individual assignment
- You may discuss approaches but not share code
- AI tools are allowed and encouraged
- You must understand all code you submit
- Document any resources used

---

## Key Points

✅ Develop locally first (FREE)  
✅ Test locally before cloud deployment  
✅ Deploy to 3 separate cloud instances for final testing  
✅ Run client from your laptop to test real distributed behavior  
✅ Stop instances when not using them  
✅ Delete instances when assignment complete  
✅ Expected cost: < $5


Good luck! 🚀