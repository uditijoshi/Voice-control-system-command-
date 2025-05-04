from collections import deque

# Round Robin Scheduler for user requests
class RoundRobinScheduler:
    def __init__(self, time_quantum):
        self.time_quantum = time_quantum
        self.queue = deque()  # Ready queue for user requests
    
    def add_request(self, user, request):
        self.queue.append((user, request))
    
    def process_requests(self):
        while self.queue:
            current_user, current_request = self.queue.popleft()
            print(f"Processing request from User {current_user}: {current_request}")
            
            # Simulate time taken to process the request
            processing_time = min(len(current_request), self.time_quantum)
            print(f"Processed {processing_time} seconds of request: {current_request}")
            
            # If the request is not fully processed, re-add it to the queue
            if len(current_request) > processing_time:
                self.queue.append((current_user, current_request[processing_time:]))
                print(f"Re-queued remaining part: {current_request[processing_time:]}")
            print()

# Banker's Algorithm for resource allocation and deadlock avoidance
class BankersAlgorithm:
    def __init__(self, available, max_resources, allocated):
        self.available = available  # Available resources
        self.max_resources = max_resources  # Maximum demand for each process
        self.allocated = allocated  # Resources allocated to processes
    
    def is_safe(self):
        work = self.available[:]  # Available resources
        finish = [False] * len(self.max_resources)  # Process completion status
        safe_sequence = []  # Safe sequence of processes
        
        while len(safe_sequence) < len(self.max_resources):
            for i in range(len(self.max_resources)):
                if not finish[i] and all(self.max_resources[i][j] - self.allocated[i][j] <= work[j] for j in range(len(self.available))):
                    safe_sequence.append(i)
                    finish[i] = True
                    for j in range(len(self.available)):
                        work[j] += self.allocated[i][j]  # Add allocated resources to work
                    break
            else:
                return False, []  # System is in an unsafe state
        
        return True, safe_sequence  # Return safe sequence if no deadlock

# Priority Scheduler for background jobs
class PriorityScheduler:
    def __init__(self):
        self.jobs = []  # List to store jobs with their priority
    
    def add_job(self, job, priority):
        self.jobs.append((job, priority))
    
    def schedule(self):
        # Sort jobs based on priority (lower priority number = higher priority)
        self.jobs.sort(key=lambda x: x[1])
        
        print("Job Execution Order (Priority First):")
        for job, priority in self.jobs:
            print(f"Executing job: {job} with priority {priority}")

# Main system simulating the integration of all algorithms
if __name__ == "__main__":
    # Step 1: Round Robin Scheduling for user requests
    rr_scheduler = RoundRobinScheduler(time_quantum=5)
    
    # Simulate multiple users making requests
    rr_scheduler.add_request("User1", "Withdraw 5000")
    rr_scheduler.add_request("User2", "Check Balance")
    rr_scheduler.add_request("User3", "Transfer 1000 to Account B")
    rr_scheduler.add_request("User4", "Withdraw 2000")
    rr_scheduler.process_requests()
    
    # Step 2: Banker's Algorithm for resource allocation
    available = [3, 3, 2]  # Available resources (e.g., 3 funds, 3 accounts, 2 locks)
    max_resources = [[7, 5, 3], [3, 2, 2], [9, 0, 2]]  # Max demand for each transaction
    allocated = [[0, 1, 0], [2, 0, 0], [3, 0, 2]]  # Allocated resources (e.g., funds allocated)
    
    bankers = BankersAlgorithm(available, max_resources, allocated)
    safe, sequence = bankers.is_safe()

    if safe:
        print(f"System is safe. Safe sequence: {sequence}")
    else:
        print("System is not safe. Possible deadlock detected.")
    
    print()

    # Step 3: Priority Scheduling for background tasks (e.g., fraud detection, report generation)
    priority_scheduler = PriorityScheduler()
    priority_scheduler.add_job("Fraud Detection", 1)  # High priority
    priority_scheduler.add_job("Send Email Notifications", 3)  # Low priority
    priority_scheduler.add_job("Monthly Report Generation", 2)  # Medium priority
    priority_scheduler.schedule()
