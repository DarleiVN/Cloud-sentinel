from datetime import datetime, timezone

def get_mock_aws_data():
    """Simula as respostas do Boto3 para testes locais."""
    mock_ebs = {
        "Volumes": [
            {
                "VolumeId": "vol-0123456789abcdef0",
                "Size": 30,
                "State": "in-use",
                "VolumeType": "gp3",
                "CreateTime": datetime(2026, 5, 1, tzinfo=timezone.utc),
                "Attachments": [{"InstanceId": "i-abcdef01234567890", "State": "attached"}]
            },
            {
                "VolumeId": "vol-9876543210fedcba0",
                "Size": 50,
                "State": "available",
                "VolumeType": "gp2",
                "CreateTime": datetime(2026, 6, 10, tzinfo=timezone.utc),
                "Attachments": []
            }
        ]
    }
    
    mock_eip = {
        "Addresses": [
            {
                "PublicIp": "54.210.43.12",
                "AllocationId": "eipalloc-0123456789abcdef0",
                "InstanceId": "i-abcdef01234567890",
                "AssociationId": "eipassoc-01234567"
            },
            {
                "PublicIp": "34.200.15.99",
                "AllocationId": "eipalloc-9876543210fedcba0",
                "Domain": "vpc"
            }
        ]
    }

    # NOVO MOCK: Simulação de instâncias EC2
    mock_ec2 = {
        "Reservations": [
            {
                "Instances": [
                    {
                        "InstanceId": "i-1234567890abcdef0",
                        "InstanceType": "t3.medium",
                        "State": {"Name": "running"},
                        "LaunchTime": datetime(2026, 6, 1, tzinfo=timezone.utc),
                        # Simulação de métrica que extrairíamos do CloudWatch
                        "CpuUtilizationAverage": 4.2 
                    },
                    {
                        "InstanceId": "i-9876543210abcdef1",
                        "InstanceType": "t3.large",
                        "State": {"Name": "running"},
                        "LaunchTime": datetime(2026, 6, 15, tzinfo=timezone.utc),
                        "CpuUtilizationAverage": 78.5
                    }
                ]
            }
        ]
    }
    
    return mock_ebs, mock_eip, mock_ec2