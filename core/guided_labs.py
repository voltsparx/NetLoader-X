"""
NetLoader-X :: Guided Labs Module
==================================================
Pre-set scenarios that teach specific concepts about
load behavior, server degradation, and defensive measures.

Each lab is self-contained, includes educational narration,
and teaches one key concept.

Author  : voltsparx
Contact : voltsparx@gmail.com
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum


class LabDifficulty(Enum):
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3


@dataclass
class GuidedLab:
    """Single guided learning scenario."""
    id: int
    name: str
    description: str
    difficulty: LabDifficulty
    learning_objective: str
    duration: int  # seconds
    threads: int
    profile: str
    configuration: Dict[str, Any]
    narrative: str  # Educational text shown during lab
    key_insight: str  # Main takeaway


# ==================================================
# GUIDED LABS CATALOG
# ==================================================

GUIDED_LABS: List[GuidedLab] = [
    GuidedLab(
        id=1,
        name="Queue Overflow Basics",
        description="See what happens when requests exceed server capacity",
        difficulty=LabDifficulty.BEGINNER,
        learning_objective="Understand how queues fill and servers degrade",
        duration=30,
        threads=20,
        profile="http",
        configuration={
            "server_profile": "small-web",
            "queue_limit": 200,
            "base_rate": 500,
            "max_rate": 3000
        },
        narrative="""
Welcome to Lab 1: Queue Overflow Basics

In this lab, you'll observe what happens when client 
requests arrive faster than the server can process them.

Watch the metrics as the simulation runs:
1. Queue depth will grow steadily
2. Latency will increase non-linearly
3. Error rate will climb as queue fills
4. The server won't crash, but degradation is obvious

KEY INSIGHT: Queues are your warning system.
When queue depth exceeds 50% of capacity, act immediately.
""",
        key_insight="Queues grow exponentially under load; monitor them closely for early warning signs"
    ),

    GuidedLab(
        id=2,
        name="Slowloris Connection Exhaustion",
        description="Learn how slow clients can exhaust worker pools with few connections",
        difficulty=LabDifficulty.BEGINNER,
        learning_objective="Understand connection exhaustion attacks and defenses",
        duration=30,
        threads=50,
        profile="slow",
        configuration={
            "server_profile": "small-web",
            "slow_client_ratio": 0.5,
            "hold_time": 25
        },
        narrative="""
Welcome to Lab 2: Slowloris Connection Exhaustion

This lab simulates an attack where a few clients
hold connections open for a long time.

Observe:
1. With only 50 virtual clients, worker pool fills
2. Other legitimate requests get queued
3. Long-lived connections consume resources
4. Server performance degrades gracefully

DEFENSE INSIGHTS:
- Implement connection timeouts (T-SOX requirement)
- Prioritize quick requests over slow ones
- Monitor idle connections
- Set aggressive keepalive timeouts
""",
        key_insight="A few slow clients can exhaust a server; implement aggressive timeout policies"
    ),

    GuidedLab(
        id=3,
        name="Burst Traffic Response",
        description="Observe server behavior during sudden flash-crowd scenarios",
        difficulty=LabDifficulty.INTERMEDIATE,
        learning_objective="Understand flash-crowd behavior and autoscaling need",
        duration=40,
        threads=100,
        profile="burst",
        configuration={
            "server_profile": "api-backend",
            "burst_interval": 10,
            "burst_length": 3,
            "base_rate": 1000,
            "max_rate": 8000
        },
        narrative="""
Welcome to Lab 3: Burst Traffic Response

Sudden spikes in traffic (e.g., viral tweets, news links)
create a common stress scenario.

Watch the dashboard as periodic bursts occur:
1. Queue depth will spike dramatically
2. Latency will jump during burst windows
3. Error rates will increase
4. Recovery will be gradual

DEFENSIVE LESSON:
- Implement circuit breakers to reject excess traffic
- Use load shedding to prioritize critical requests
- Auto-scaling must react BEFORE overload
- Queue monitoring enables early warning
""",
        key_insight="Bursts are sudden; pre-emptive defenses matter more than reactive scaling"
    ),

    GuidedLab(
        id=4,
        name="Error Rate Cascade",
        description="Understand how errors grow non-linearly with load",
        difficulty=LabDifficulty.INTERMEDIATE,
        learning_objective="Learn about error amplification and retry storms",
        duration=45,
        threads=150,
        profile="http",
        configuration={
            "server_profile": "api-backend",
            "base_rate": 2000,
            "max_rate": 10000,
            "error_growth_factor": 1.3
        },
        narrative="""
Welcome to Lab 4: Error Rate Cascade

Errors don't grow linearly with load; they explode.
This shows why client-side retries can be dangerous.

Observe:
1. Error rate starts near 0%
2. As queue fills, errors spike exponentially
3. Clients retry failed requests
4. Retries amplify the cascade

CASCADING FAILURE MECHANICS:
- Client A fails (network error or timeout)
- Client A retries immediately (exponential backoff!)
- 100 failures cause 200 requests (with retries)
- This feedback loop causes collapse

DEFENSE MITIGATION:
- Exponential backoff with jitter on client side
- Circuit breakers at service boundaries
- Error budgets per client
- Graceful degradation (feature flags)
""",
        key_insight="Error rates cascade exponentially; retries without backoff cause meltdown"
    ),

    GuidedLab(
        id=5,
        name="Queue Limit Impact",
        description="Compare behavior with different queue limit settings",
        difficulty=LabDifficulty.INTERMEDIATE,
        learning_objective="Understand queue limit trade-offs",
        duration=35,
        threads=75,
        profile="burst",
        configuration={
            "server_profile": "small-web",
            "queue_limits_to_test": [50, 200, 500],
            "burst_interval": 8,
            "burst_length": 2
        },
        narrative="""
Welcome to Lab 5: Queue Limit Impact

Queue limits are a critical tuning parameter.
Too low = legitimate requests rejected
Too high = unbounded latency growth

This lab shows the balance:
1. Low limits reject traffic quickly (fail fast)
2. High limits queue requests (resource buildup)
3. Optimal limit depends on workload

QUEUE LIMIT TUNING:
- Measure acceptable latency (e.g., 1000ms)
- Calculate queue depth at that latency
- Set limit to 150% of normal traffic depth
- Monitor for timeout complaints

METRIC TO WATCH:
- p99 latency (99th percentile)
- If p99 exceeds your SLA consistently, reduce queue limit
""",
        key_insight="Smaller queues fail fast and prevent latency amplification; larger queues defer problems"
    ),

    GuidedLab(
        id=6,
        name="Server Recovery Dynamics",
        description="Observe how servers recover after being pushed to degradation",
        difficulty=LabDifficulty.ADVANCED,
        learning_objective="Understand recovery behavior and hysteresis effects",
        duration=60,
        threads=80,
        profile="wave",
        configuration={
            "server_profile": "enterprise-app",
            "wave_period": 15,
            "base_rate": 1500,
            "max_rate": 6000
        },
        narrative="""
Welcome to Lab 6: Server Recovery Dynamics

Servers don't recover instantly after overload.
Observe the slow, asymmetric recovery pattern.

What you'll see:
1. Load builds -> degradation -> peak latency
2. Load drops -> slow recovery (recovery lag)
3. Recovery slower than degradation (hysteresis)
4. Cascading effects persist even as traffic drops

WHY RECOVERY IS SLOW:
- Backlog of delayed requests still being processed
- Resource contention among queued requests
- Client retries adding phantom traffic
- Thread pool still busy with stale work

RECOVERY STRATEGIES:
- Aggressive load shedding during recovery
- Priority queues for new vs queued requests
- Circuit breakers to prevent retry storms
- Telemetry to detect lingering load
""",
        key_insight="Recovery is slower and messier than degradation; architecture matters"
    ),

    GuidedLab(
        id=7,
        name="Chaos Engineering: Random Faults",
        description="See how random failures compound under load",
        difficulty=LabDifficulty.ADVANCED,
        learning_objective="Understand chaos engineering principles and fault injection",
        duration=45,
        threads=100,
        profile="http",
        configuration={
            "server_profile": "api-backend",
            "chaos_enabled": True,
            "fault_injection_rate": 0.05,  # 5% of requests fail randomly
            "base_rate": 3000,
            "max_rate": 8000
        },
        narrative="""
Welcome to Lab 7: Chaos Engineering - Random Faults

Real systems experience random failures:
- Network timeouts
- Disk I/O errors
- Worker crashes
- GC pauses

This lab injects 5% fault rate on top of normal load.

Observe:
1. Base error rate from overload + chaos faults
2. Client retry cascades during fault windows
3. Graceful handling of mixed failures
4. Recovery patterns with compound failures

CHAOS ENGINEERING BEST PRACTICES:
- Inject failures in production (carefully!)
- Start with small failure rates
- Measure impact on end-to-end latency
- Test automatic recovery
- Use game days to practice response

RECOMMENDED FAULT INJECTION:
- Network latency variance (50-200ms outliers)
- Random timeout exceptions (1-3% of requests)
- Periodic worker restarts
- Memory pressure events
- Cascading failures (downstream service failure)
""",
        key_insight="Random faults combined with load create complex cascades; resilience requires layered defense"
    ),
]


# ==================================================
# LAB MANAGER
# ==================================================

class LabManager:
    """Manages guided labs catalog and execution."""

    def __init__(self):
        self.labs = GUIDED_LABS

    def list_labs(self) -> None:
        """Print formatted list of all labs."""
        print("\n" + "=" * 70)
        print("NetLoader-X Guided Labs Catalog")
        print("=" * 70)
        
        for lab in self.labs:
            diff_str = {
                LabDifficulty.BEGINNER: "BEGINNER",
                LabDifficulty.INTERMEDIATE: "INTERMEDIATE",
                LabDifficulty.ADVANCED: "ADVANCED"
            }[lab.difficulty]
            
            print(f"\n[Lab {lab.id}] {lab.name}")
            print(f"  Difficulty: {diff_str}")
            print(f"  Duration: {lab.duration}s | Threads: {lab.threads}")
            print(f"  Profile: {lab.profile}")
            print(f"  Objective: {lab.learning_objective}")
            print(f"  Insight: {lab.key_insight}")

    def get_lab(self, lab_id: int) -> GuidedLab:
        """Get lab by ID."""
        for lab in self.labs:
            if lab.id == lab_id:
                return lab
        raise ValueError(f"Lab {lab_id} not found")

    def get_lab_by_difficulty(self, difficulty: LabDifficulty) -> List[GuidedLab]:
        """Get all labs of given difficulty."""
        return [lab for lab in self.labs if lab.difficulty == difficulty]

    def get_beginner_labs(self) -> List[GuidedLab]:
        """Get all beginner labs."""
        return self.get_lab_by_difficulty(LabDifficulty.BEGINNER)

    def get_intermediate_labs(self) -> List[GuidedLab]:
        """Get all intermediate labs."""
        return self.get_lab_by_difficulty(LabDifficulty.INTERMEDIATE)

    def get_advanced_labs(self) -> List[GuidedLab]:
        """Get all advanced labs."""
        return self.get_lab_by_difficulty(LabDifficulty.ADVANCED)
