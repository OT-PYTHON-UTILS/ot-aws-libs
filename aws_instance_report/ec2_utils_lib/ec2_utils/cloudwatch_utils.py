import boto3
from datetime import datetime, timedelta, timezone

def fetch_cpu_utilization(session, instance_id, region, period, start, end, last_n_days):
    cloudwatch = session.client('cloudwatch', region_name=region)

    # Determine time range
    if last_n_days:
        end_time = datetime.utcnow()  
        start_time = end_time - timedelta(days=last_n_days)
    else:
        start_time = start
        end_time = end

    # Fetch metrics
    metrics = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=period,
        Statistics= ['Minimum','Maximum','Average'],
        Unit='Percent'
    )

    print(f"Metrics fetched: {metrics}")  # Add logging here

    if metrics['Datapoints']:
        min_cpu = min(dp['Minimum'] for dp in metrics['Datapoints'])
        max_cpu = max(dp['Maximum'] for dp in metrics['Datapoints'])
        avg_cpu = sum(dp['Average'] for dp in metrics['Datapoints']) / len(metrics['Datapoints'])
        return min_cpu, max_cpu, avg_cpu
    else:
        return 0.0, 0.0, 0.0
