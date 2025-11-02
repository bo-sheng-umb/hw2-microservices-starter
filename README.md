HW2: Microservices with Load Balancing and Fault Tolerance
Quick Start
1. Clone Your Repository
bashgit clone https://github.com/CS4XX-Fall-2024/hw2-microservices-[yourusername].git
cd hw2-microservices-[yourusername]
2. Complete the Implementation
Edit grpc_assignment.py and implement all sections marked with:
python# TODO: STUDENT MUST IMPLEMENT
3. Test Locally First
bash# Terminal 1: Start service instances
python3 grpc_assignment.py server 9000

# Terminal 2: Start another instance
python3 grpc_assignment.py server 9001

# Terminal 3: Start third instance
python3 grpc_assignment.py server 9002

# Terminal 4: Run tests
python3 grpc_assignment.py test

# Or run demo mode
python3 grpc_assignment.py demo
Cloud Deployment
Option A: Google Cloud Platform (GCP) - Recommended
Prerequisites

Claim your $50 GCP credits using the link provided by instructor
Create a GCP project: cs4xx-hw2-[yourusername]

Using Cloud Shell (No Installation Required)

Go to https://console.cloud.google.com
Click the terminal icon (>_) in top-right corner
Clone your repository in Cloud Shell:

bashgit clone https://github.com/CS4XX-Fall-2024/hw2-microservices-[yourusername].git
cd hw2-microservices-[yourusername]
Deploy Instances
bash# Create 3 instances (costs ~$0.01/hour total with preemptible)
for i in 0 1 2; do
  gcloud compute instances create hw2-instance-$i \
    --zone=us-central1-a \
    --machine-type=e2-micro \
    --preemptible \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud
done

# Get instance IPs
gcloud compute instances list

# SSH to each instance and run service
gcloud compute ssh hw2-instance-0 --zone=us-central1-a
# In SSH session:
git clone [your-repo]
cd [repo-folder]
python3 grpc_assignment.py server 9000
IMPORTANT: Clean Up After Testing
bash# Stop instances when not using (no charges while stopped)
gcloud compute instances stop hw2-instance-0 hw2-instance-1 hw2-instance-2 --zone=us-central1-a

# Delete instances when completely done
gcloud compute instances delete hw2-instance-0 hw2-instance-1 hw2-instance-2 --zone=us-central1-a --quiet
Option B: CloudLab (Free Alternative)

Request nodes at https://cloudlab.us
SSH to each node
Clone repository and run services:

bash# On each CloudLab node
git clone [your-repo]
cd [repo-folder]
python3 grpc_assignment.py server 900X  # X = 0, 1, or 2
Option C: Single GCP Instance (Cheapest)
For minimal cloud testing, run all services on one instance:
bash# Create one instance
gcloud compute instances create hw2-test \
  --zone=us-central1-a \
  --machine-type=e2-micro \
  --preemptible

# SSH to instance
gcloud compute ssh hw2-test --zone=us-central1-a

# In SSH session, run all services
git clone [your-repo]
cd [repo-folder]
python3 grpc_assignment.py server 9000 &
python3 grpc_assignment.py server 9001 &
python3 grpc_assignment.py server 9002 &
python3 grpc_assignment.py test
Submission
Save Your Work
bashgit add grpc_assignment.py
git add AI_USAGE.md  # Document your AI tool usage
git commit -m "Implement [feature name]"
git push
Final Submission
bash# Make sure everything is pushed
git status  # Should show "nothing to commit"
git push

# Tag your final version (optional but recommended)
git tag final-submission
git push --tags
Your submission is complete when code is pushed to GitHub before the deadline.
Testing Requirements
Your implementation should pass these tests:
Local Tests

 All service instances start without errors
 Load balancer distributes requests
 Circuit breaker opens after failures
 Retry logic works with backoff
 All operations (sum, avg, min, max, multiply) work

Cloud Tests

 Services run on separate instances/machines
 System handles instance failures
 Performance metrics collected

Grading Criteria

Basic RPC Implementation (30 points)
Load Balancing (25 points)
Fault Tolerance (25 points)
Testing & Deployment (20 points)
Graduate Additional Requirements (+40 points)

Cost Management (GCP)
CRITICAL: Monitor your spending!

Check remaining credits: Billing → Credits in Cloud Console
Always stop/delete instances when done
Use preemptible instances (60-80% cheaper)
Expected total cost: < $10 for entire assignment
Emergency: Delete all instances with:

bashgcloud compute instances delete --all --zone=us-central1-a
Common Issues
Port Already in Use
bash# Find process using port
lsof -i :9000
# Kill process
kill -9 [PID]
Connection Refused

Check firewall rules
Verify server is running
Use correct IP address

GCP Credits Running Low

Switch to local testing only
Use CloudLab instead
Share instance with classmate (coordinate times)

Getting Help

Check assignment page for full requirements
Office Hours: [Schedule]
Piazza/Discord: For questions (don't share code)
GitHub Issues: For starter code problems

Files in This Repository

grpc_assignment.py - Main file you need to complete
README.md - This file
.gitignore - Git ignore rules
AI_USAGE.md - Document your AI tool usage (create this)

Important Dates

Assignment Released: [Date]
Due Date: [Date] at 11:59 PM
Late Policy: -10% per day, max 3 days

Academic Integrity

This is an individual assignment
You may discuss approaches but not share code
Document any resources used
AI tools are allowed with proper documentation


Remember: Start locally, test thoroughly, then deploy to cloud for final testing!