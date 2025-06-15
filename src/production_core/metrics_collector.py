"""
Metrics Collector - Production Grade Performance Monitoring
==========================================================

Comprehensive metrics collection and analysis system with:
- Real-time performance metrics collection
- Custom metric definitions and tracking
- Statistical analysis and trend detection
- Alerting based on metric thresholds
- Export capabilities for monitoring systems
- Historical data retention and analysis
"""

import asyncio
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"          # Monotonically increasing value
    GAUGE = "gauge"              # Current value that can go up or down
    HISTOGRAM = "histogram"      # Distribution of values
    TIMER = "timer"              # Duration measurements
    RATE = "rate"                # Rate of change over time


class AggregationType(Enum):
    """Types of metric aggregation"""
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE_50 = "p50"
    PERCENTILE_90 = "p90"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"


@dataclass
class MetricValue:
    """Individual metric value with timestamp"""
    value: Union[int, float]
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags
        }


@dataclass
class MetricDefinition:
    """Definition of a metric"""
    name: str
    metric_type: MetricType
    description: str = ""
    unit: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Retention settings
    retention_hours: int = 24
    max_values: int = 10000
    
    # Alerting thresholds
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    threshold_direction: str = "above"  # "above" or "below"


@dataclass
class MetricSummary:
    """Statistical summary of metric values"""
    name: str
    count: int
    sum_value: float
    min_value: float
    max_value: float
    avg_value: float
    median_value: float
    std_dev: float
    percentile_90: float
    percentile_95: float
    percentile_99: float
    first_timestamp: datetime
    last_timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'count': self.count,
            'sum': self.sum_value,
            'min': self.min_value,
            'max': self.max_value,
            'avg': self.avg_value,
            'median': self.median_value,
            'std_dev': self.std_dev,
            'p90': self.percentile_90,
            'p95': self.percentile_95,
            'p99': self.percentile_99,
            'first_timestamp': self.first_timestamp.isoformat(),
            'last_timestamp': self.last_timestamp.isoformat()
        }


class TimeSeries:
    """Time series data structure for metrics"""
    
    def __init__(self, max_size: int = 10000, retention_hours: int = 24):
        self.max_size = max_size
        self.retention_hours = retention_hours
        self.values: deque[MetricValue] = deque(maxlen=max_size)
        self._lock = asyncio.Lock()
    
    async def add_value(self, value: Union[int, float], tags: Dict[str, str] = None):
        """Add a value to the time series"""
        async with self._lock:
            metric_value = MetricValue(
                value=value,
                timestamp=datetime.utcnow(),
                tags=tags or {}
            )
            self.values.append(metric_value)
            
            # Clean old values based on retention
            await self._clean_old_values()
    
    async def _clean_old_values(self):
        """Remove values older than retention period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)
        
        while self.values and self.values[0].timestamp < cutoff_time:
            self.values.popleft()
    
    async def get_values(self, start_time: Optional[datetime] = None, 
                        end_time: Optional[datetime] = None) -> List[MetricValue]:
        """Get values within time range"""
        async with self._lock:
            if not start_time and not end_time:
                return list(self.values)
            
            start_time = start_time or datetime.min
            end_time = end_time or datetime.utcnow()
            
            return [
                value for value in self.values
                if start_time <= value.timestamp <= end_time
            ]
    
    async def get_latest_value(self) -> Optional[MetricValue]:
        """Get the most recent value"""
        async with self._lock:
            return self.values[-1] if self.values else None
    
    async def calculate_summary(self, start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None) -> Optional[MetricSummary]:
        """Calculate statistical summary of values"""
        values = await self.get_values(start_time, end_time)
        
        if not values:
            return None
        
        numeric_values = [v.value for v in values]
        
        return MetricSummary(
            name="",  # Will be set by caller
            count=len(numeric_values),
            sum_value=sum(numeric_values),
            min_value=min(numeric_values),
            max_value=max(numeric_values),
            avg_value=statistics.mean(numeric_values),
            median_value=statistics.median(numeric_values),
            std_dev=statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0,
            percentile_90=self._percentile(numeric_values, 0.90),
            percentile_95=self._percentile(numeric_values, 0.95),
            percentile_99=self._percentile(numeric_values, 0.99),
            first_timestamp=values[0].timestamp,
            last_timestamp=values[-1].timestamp
        )
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile of values"""
        if not values:
            return 0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        index = min(index, len(sorted_values) - 1)
        return sorted_values[index]


class MetricCollector:
    """
    Production-grade metrics collection system
    
    Features:
    - Multiple metric types (counter, gauge, histogram, timer)
    - Real-time statistical analysis
    - Configurable retention and aggregation
    - Threshold-based alerting
    - Export capabilities
    """
    
    def __init__(self):
        self.metrics: Dict[str, MetricDefinition] = {}
        self.time_series: Dict[str, TimeSeries] = {}
        self.alert_handlers: List[Callable] = []
        
        # Aggregation tasks
        self.aggregation_tasks: Dict[str, asyncio.Task] = {}
        self.is_collecting = False
        
        # Performance tracking
        self.collection_stats = {
            'total_metrics_collected': 0,
            'collection_errors': 0,
            'last_collection_time': None,
            'avg_collection_time_ms': 0
        }
        
        logger.info("Metrics collector initialized")
    
    def define_metric(self, definition: MetricDefinition):
        """Define a new metric for collection"""
        self.metrics[definition.name] = definition
        self.time_series[definition.name] = TimeSeries(
            max_size=definition.max_values,
            retention_hours=definition.retention_hours
        )
        
        logger.info(f"Defined metric: {definition.name} ({definition.metric_type.value})")
    
    def add_alert_handler(self, handler: Callable[[str, MetricValue, MetricDefinition], None]):
        """Add alert handler for threshold violations"""
        self.alert_handlers.append(handler)
    
    async def record_counter(self, name: str, value: Union[int, float] = 1, 
                           tags: Dict[str, str] = None):
        """Record a counter metric (monotonically increasing)"""
        await self._record_metric(name, value, MetricType.COUNTER, tags)
    
    async def record_gauge(self, name: str, value: Union[int, float], 
                          tags: Dict[str, str] = None):
        """Record a gauge metric (current value)"""
        await self._record_metric(name, value, MetricType.GAUGE, tags)
    
    async def record_timer(self, name: str, duration_ms: float, 
                          tags: Dict[str, str] = None):
        """Record a timer metric (duration measurement)"""
        await self._record_metric(name, duration_ms, MetricType.TIMER, tags)
    
    async def record_histogram(self, name: str, value: Union[int, float], 
                              tags: Dict[str, str] = None):
        """Record a histogram metric (value distribution)"""
        await self._record_metric(name, value, MetricType.HISTOGRAM, tags)
    
    async def _record_metric(self, name: str, value: Union[int, float], 
                           metric_type: MetricType, tags: Dict[str, str] = None):
        """Internal method to record any metric"""
        start_time = time.time()
        
        try:
            # Auto-define metric if not exists
            if name not in self.metrics:
                self.define_metric(MetricDefinition(
                    name=name,
                    metric_type=metric_type,
                    description=f"Auto-generated {metric_type.value} metric"
                ))
            
            # Record the value
            time_series = self.time_series[name]
            await time_series.add_value(value, tags)
            
            # Check thresholds and trigger alerts
            await self._check_thresholds(name, value)
            
            # Update collection stats
            self.collection_stats['total_metrics_collected'] += 1
            self.collection_stats['last_collection_time'] = datetime.utcnow()
            
            collection_time = (time.time() - start_time) * 1000
            self._update_avg_collection_time(collection_time)
            
        except Exception as e:
            self.collection_stats['collection_errors'] += 1
            logger.error(f"Error recording metric {name}: {e}")
    
    async def _check_thresholds(self, name: str, value: Union[int, float]):
        """Check if metric value violates thresholds"""
        definition = self.metrics[name]
        
        if definition.warning_threshold is None and definition.critical_threshold is None:
            return
        
        # Determine if threshold is violated
        violated_threshold = None
        threshold_type = None
        
        if definition.critical_threshold is not None:
            if definition.threshold_direction == "above" and value > definition.critical_threshold:
                violated_threshold = definition.critical_threshold
                threshold_type = "critical"
            elif definition.threshold_direction == "below" and value < definition.critical_threshold:
                violated_threshold = definition.critical_threshold
                threshold_type = "critical"
        
        if violated_threshold is None and definition.warning_threshold is not None:
            if definition.threshold_direction == "above" and value > definition.warning_threshold:
                violated_threshold = definition.warning_threshold
                threshold_type = "warning"
            elif definition.threshold_direction == "below" and value < definition.warning_threshold:
                violated_threshold = definition.warning_threshold
                threshold_type = "warning"
        
        # Trigger alerts if threshold violated
        if violated_threshold is not None:
            metric_value = MetricValue(value=value, timestamp=datetime.utcnow())
            await self._send_threshold_alert(name, metric_value, definition, threshold_type, violated_threshold)
    
    async def _send_threshold_alert(self, name: str, value: MetricValue, 
                                   definition: MetricDefinition, threshold_type: str, 
                                   threshold_value: float):
        """Send threshold violation alert"""
        for handler in self.alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(name, value, definition, threshold_type, threshold_value)
                else:
                    handler(name, value, definition, threshold_type, threshold_value)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
    
    def _update_avg_collection_time(self, collection_time_ms: float):
        """Update average collection time"""
        current_avg = self.collection_stats['avg_collection_time_ms']
        total_collections = self.collection_stats['total_metrics_collected']
        
        if total_collections > 1:
            new_avg = ((current_avg * (total_collections - 1)) + collection_time_ms) / total_collections
            self.collection_stats['avg_collection_time_ms'] = new_avg
        else:
            self.collection_stats['avg_collection_time_ms'] = collection_time_ms
    
    async def get_metric_summary(self, name: str, start_time: Optional[datetime] = None,
                                end_time: Optional[datetime] = None) -> Optional[MetricSummary]:
        """Get statistical summary for a metric"""
        if name not in self.time_series:
            return None
        
        time_series = self.time_series[name]
        summary = await time_series.calculate_summary(start_time, end_time)
        
        if summary:
            summary.name = name
        
        return summary
    
    async def get_metric_values(self, name: str, start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None) -> List[MetricValue]:
        """Get raw metric values"""
        if name not in self.time_series:
            return []
        
        time_series = self.time_series[name]
        return await time_series.get_values(start_time, end_time)
    
    async def get_latest_value(self, name: str) -> Optional[MetricValue]:
        """Get latest value for a metric"""
        if name not in self.time_series:
            return None
        
        time_series = self.time_series[name]
        return await time_series.get_latest_value()
    
    async def get_all_metrics_summary(self, start_time: Optional[datetime] = None,
                                     end_time: Optional[datetime] = None) -> Dict[str, MetricSummary]:
        """Get summary for all metrics"""
        summaries = {}
        
        for name in self.metrics.keys():
            summary = await self.get_metric_summary(name, start_time, end_time)
            if summary:
                summaries[name] = summary
        
        return summaries
    
    async def export_metrics(self, format_type: str = "json", 
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> str:
        """Export metrics in specified format"""
        if format_type.lower() == "json":
            return await self._export_json(start_time, end_time)
        elif format_type.lower() == "prometheus":
            return await self._export_prometheus()
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    async def _export_json(self, start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None) -> str:
        """Export metrics as JSON"""
        export_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'collection_stats': self.collection_stats,
            'metrics': {}
        }
        
        for name, definition in self.metrics.items():
            summary = await self.get_metric_summary(name, start_time, end_time)
            values = await self.get_metric_values(name, start_time, end_time)
            
            export_data['metrics'][name] = {
                'definition': {
                    'name': definition.name,
                    'type': definition.metric_type.value,
                    'description': definition.description,
                    'unit': definition.unit,
                    'tags': definition.tags
                },
                'summary': summary.to_dict() if summary else None,
                'values': [value.to_dict() for value in values]
            }
        
        return json.dumps(export_data, indent=2)
    
    async def _export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        for name, definition in self.metrics.items():
            latest_value = await self.get_latest_value(name)
            
            if latest_value is None:
                continue
            
            # Add metric help
            if definition.description:
                lines.append(f"# HELP {name} {definition.description}")
            
            # Add metric type
            prometheus_type = self._get_prometheus_type(definition.metric_type)
            lines.append(f"# TYPE {name} {prometheus_type}")
            
            # Add metric value with tags
            tags_str = ""
            if latest_value.tags:
                tag_pairs = [f'{k}="{v}"' for k, v in latest_value.tags.items()]
                tags_str = "{" + ",".join(tag_pairs) + "}"
            
            lines.append(f"{name}{tags_str} {latest_value.value}")
        
        return "\n".join(lines)
    
    def _get_prometheus_type(self, metric_type: MetricType) -> str:
        """Convert metric type to Prometheus type"""
        mapping = {
            MetricType.COUNTER: "counter",
            MetricType.GAUGE: "gauge",
            MetricType.HISTOGRAM: "histogram",
            MetricType.TIMER: "histogram",
            MetricType.RATE: "gauge"
        }
        return mapping.get(metric_type, "gauge")
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get metrics collection statistics"""
        return {
            **self.collection_stats,
            'total_defined_metrics': len(self.metrics),
            'active_time_series': len(self.time_series),
            'is_collecting': self.is_collecting
        }
    
    async def reset_metrics(self, metric_names: Optional[List[str]] = None):
        """Reset specified metrics or all metrics"""
        if metric_names is None:
            metric_names = list(self.metrics.keys())
        
        for name in metric_names:
            if name in self.time_series:
                self.time_series[name] = TimeSeries(
                    max_size=self.metrics[name].max_values,
                    retention_hours=self.metrics[name].retention_hours
                )
        
        logger.info(f"Reset {len(metric_names)} metrics")


class TimerContext:
    """Context manager for timing operations"""
    
    def __init__(self, collector: MetricCollector, metric_name: str, 
                 tags: Dict[str, str] = None):
        self.collector = collector
        self.metric_name = metric_name
        self.tags = tags
        self.start_time = None
    
    async def __aenter__(self):
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration_ms = (time.time() - self.start_time) * 1000
            await self.collector.record_timer(self.metric_name, duration_ms, self.tags)


# Global metrics collector instance
metrics_collector = MetricCollector()


# Convenience functions
async def record_counter(name: str, value: Union[int, float] = 1, tags: Dict[str, str] = None):
    """Record a counter metric"""
    await metrics_collector.record_counter(name, value, tags)


async def record_gauge(name: str, value: Union[int, float], tags: Dict[str, str] = None):
    """Record a gauge metric"""
    await metrics_collector.record_gauge(name, value, tags)


async def record_timer(name: str, duration_ms: float, tags: Dict[str, str] = None):
    """Record a timer metric"""
    await metrics_collector.record_timer(name, duration_ms, tags)


def timer(metric_name: str, tags: Dict[str, str] = None) -> TimerContext:
    """Create a timer context manager"""
    return TimerContext(metrics_collector, metric_name, tags)


# Decorator for timing functions
def timed(metric_name: str, tags: Dict[str, str] = None):
    """Decorator to time function execution"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            async with timer(metric_name, tags):
                return await func(*args, **kwargs)
        return wrapper
    return decorator